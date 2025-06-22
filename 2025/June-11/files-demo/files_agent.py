import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()


class FileOperationError(Exception):
    """Custom exception for file operation errors."""
    pass


class FileExplorerTool(BaseTool):
    name: str = "file_explorer"
    description: str = """Useful for file and folder operations. Input should be a JSON string with an 'action' field.
    
Available actions:
- create_test: Creates test directory and file
- list: Lists directory contents (requires 'path' field)
- read: Reads file contents (requires 'path' field)
- create_file: Creates new file (requires 'path' and optional 'content' fields)
- create_folder: Creates new directory (requires 'path' field)
- write_file: Writes to file (requires 'path' and 'content' fields)
- update_file: Updates file (requires 'path', 'content', and optional 'mode' fields)
- query_file: Searches in file (requires 'path' and 'query' fields)
- delete_file: Deletes file (requires 'path' field)
- delete_folder: Deletes directory (requires 'path' field, optional 'recursive' field)
- copy_file: Copies file (requires 'source' and 'destination' fields)
- move_file: Moves/renames file (requires 'source' and 'destination' fields)

Example: {"action": "create_file", "path": "example.txt", "content": "Hello World"}"""

    def _run(self, query: str) -> str:
        """Main entry point for file operations."""
        try:
            print(f"DEBUG: Tool received query: {repr(query)}")

            # Parse input and execute action
            parsed_data = self._parse_input(query)
            return self._execute_action(parsed_data)

        except Exception as e:
            error_msg = f"Error in file explorer tool: {str(e)}"
            print(f"DEBUG: {error_msg}")
            return error_msg

    def _parse_input(self, query: str) -> Dict[str, Any]:
        """Parse input query into structured data."""
        try:
            # Try JSON parsing first
            query_data = json.loads(query)
            action = query_data.get("action")
            if not action:
                raise ValueError("No 'action' field specified in JSON")

            print(f"DEBUG: Parsed JSON - action: {action}")
            return query_data

        except json.JSONDecodeError:
            print(f"DEBUG: JSON parse failed, trying natural language")
            return self._parse_natural_language(query.strip())

    def _parse_natural_language(self, query: str) -> Dict[str, Any]:
        """Parse natural language queries into structured data."""
        query_lower = query.lower().strip()

        # Help commands
        if any(word in query_lower for word in ["commands", "help", "what can", "available", "actions"]):
            return {"action": "help"}

        # Test creation
        elif "create test" in query_lower:
            return {"action": "create_test"}

        # File creation patterns
        elif "create file" in query_lower:
            filename = self._extract_filename_from_create(query_lower, "file")
            return {"action": "create_file", "path": filename, "content": ""}

        # Folder creation patterns
        elif any(phrase in query_lower for phrase in ["create folder", "create directory", "make folder", "make directory"]):
            foldername = self._extract_filename_from_create(
                query_lower, ["folder", "directory"])
            return {"action": "create_folder", "path": foldername}

        # List operations
        elif query_lower.startswith("list") or "list files" in query_lower or "show files" in query_lower:
            # Extract path if specified
            if " in " in query_lower:
                path = query_lower.split(" in ")[-1].strip()
            elif len(query_lower.split()) > 1 and not any(word in query_lower for word in ["files", "contents"]):
                path = query_lower.split()[1]
            else:
                path = "."
            return {"action": "list", "path": path}

        # Read operations
        elif query_lower.startswith("read") or "show content" in query_lower:
            if "test" in query_lower and "file" in query_lower:
                return {"action": "read", "path": "test/test_file.txt"}
            else:
                # Extract filename
                words = query_lower.split()
                if len(words) > 1:
                    filename = words[1]
                    return {"action": "read", "path": filename}
                else:
                    return {"action": "unknown", "error": "No filename specified for read operation"}

        # Write operations
        elif "write to" in query_lower or "write in" in query_lower:
            return self._parse_write_query(query)

        # Search operations
        elif "search" in query_lower and "for" in query_lower:
            return self._parse_search_query(query)

        # Delete operations
        elif "delete file" in query_lower or "remove file" in query_lower:
            filename = self._extract_filename_after_action(
                query_lower, ["delete file", "remove file"])
            return {"action": "delete_file", "path": filename}

        elif "delete folder" in query_lower or "remove folder" in query_lower:
            foldername = self._extract_filename_after_action(
                query_lower, ["delete folder", "remove folder"])
            return {"action": "delete_folder", "path": foldername, "recursive": False}

        # Copy operations
        elif "copy" in query_lower and "to" in query_lower:
            return self._parse_copy_move_query(query, "copy")

        # Move operations
        elif "move" in query_lower and "to" in query_lower:
            return self._parse_copy_move_query(query, "move")

        else:
            return {"action": "unknown", "original_query": query}

    def _extract_filename_from_create(self, query: str, keywords: Union[str, list]) -> str:
        """Extract filename from create commands."""
        if isinstance(keywords, str):
            keywords = [keywords]

        words = query.split()

        # Look for patterns like "create file called filename" or "create file filename"
        for keyword in keywords:
            if keyword in words:
                try:
                    keyword_idx = words.index(keyword)

                    # Check for "called" or "named" after keyword
                    if keyword_idx + 1 < len(words) and words[keyword_idx + 1] in ["called", "named"]:
                        if keyword_idx + 2 < len(words):
                            return words[keyword_idx + 2]
                    # Direct pattern: "create file filename"
                    elif keyword_idx + 1 < len(words):
                        next_word = words[keyword_idx + 1]
                        if next_word not in ["called", "named", "in", "at"]:
                            return next_word
                except (ValueError, IndexError):
                    continue

        # Default name if nothing found
        if "file" in keywords:
            return "unnamed_file.txt"
        else:
            return "unnamed_folder"

    def _extract_filename_after_action(self, query: str, action_phrases: list) -> str:
        """Extract filename after action phrases like 'delete file'."""
        for phrase in action_phrases:
            if phrase in query:
                parts = query.split(phrase, 1)
                if len(parts) > 1:
                    filename = parts[1].strip()
                    if filename:
                        return filename
        return "unknown_file"

    def _parse_write_query(self, query: str) -> Dict[str, Any]:
        """Parse write queries like 'write to file.txt content here'."""
        query_lower = query.lower()

        if "write to" in query_lower:
            parts = query.split("write to", 1)[1].strip()
        elif "write in" in query_lower:
            parts = query.split("write in", 1)[1].strip()
        else:
            return {"action": "unknown", "error": "Invalid write command"}

        # Split into filename and content
        words = parts.split()
        if len(words) == 0:
            return {"action": "unknown", "error": "No filename specified"}

        filename = words[0]

        # Content is everything after the filename
        if len(words) > 1:
            content = " ".join(words[1:])
            # Remove quotes if present
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            elif content.startswith("'") and content.endswith("'"):
                content = content[1:-1]
        else:
            content = ""

        return {"action": "write_file", "path": filename, "content": content}

    def _parse_search_query(self, query: str) -> Dict[str, Any]:
        """Parse search queries like 'search for term in file.txt'."""
        query_lower = query.lower()

        try:
            # Pattern: "search for X in Y" or "search in Y for X"
            if "search for" in query_lower and " in " in query_lower:
                parts = query_lower.split("search for")[1]
                search_part, file_part = parts.split(" in ", 1)
                search_term = search_part.strip()
                file_path = file_part.strip()
            elif "search in" in query_lower and " for " in query_lower:
                parts = query_lower.split("search in")[1]
                file_part, search_part = parts.split(" for ", 1)
                file_path = file_part.strip()
                search_term = search_part.strip()
            else:
                return {"action": "unknown", "error": "Invalid search format. Use 'search for term in file' or 'search in file for term'"}

            return {"action": "query_file", "path": file_path, "query": search_term}

        except ValueError:
            return {"action": "unknown", "error": "Could not parse search query"}

    def _parse_copy_move_query(self, query: str, operation: str) -> Dict[str, Any]:
        """Parse copy/move queries like 'copy file1.txt to file2.txt'."""
        query_lower = query.lower()

        try:
            if operation == "copy":
                parts = query_lower.split("copy")[1]
            else:  # move
                parts = query_lower.split("move")[1]

            source_part, dest_part = parts.split(" to ", 1)
            source = source_part.strip()
            destination = dest_part.strip()

            action = "copy_file" if operation == "copy" else "move_file"
            return {"action": action, "source": source, "destination": destination}

        except ValueError:
            return {"action": "unknown", "error": f"Invalid {operation} format. Use '{operation} source to destination'"}

    def _execute_action(self, data: Dict[str, Any]) -> str:
        """Execute the parsed action."""
        action = data.get("action", "unknown")

        # Route to appropriate handler
        action_handlers = {
            "create_test": lambda: self._create_test(),
            "list": lambda: self._list_directory(data.get("path", ".")),
            "read": lambda: self._read_file(data.get("path", "")),
            "create_file": lambda: self._create_file(data.get("path", ""), data.get("content", "")),
            "create_folder": lambda: self._create_folder(data.get("path", "")),
            "write_file": lambda: self._write_file(data.get("path", ""), data.get("content", "")),
            "update_file": lambda: self._update_file(data.get("path", ""), data.get("content", ""), data.get("mode", "append")),
            "query_file": lambda: self._query_file(data.get("path", ""), data.get("query", "")),
            "delete_file": lambda: self._delete_file(data.get("path", "")),
            "delete_folder": lambda: self._delete_folder(data.get("path", ""), data.get("recursive", False)),
            "copy_file": lambda: self._copy_file(data.get("source", ""), data.get("destination", "")),
            "move_file": lambda: self._move_file(data.get("source", ""), data.get("destination", "")),
            "help": lambda: self._get_help()
        }

        if action in action_handlers:
            return action_handlers[action]()
        else:
            error_msg = data.get("error", f"Unknown action: {action}")
            return f"❌ {error_msg}. Use 'help' to see available commands."

    # Helper methods for path operations
    def _validate_path(self, path: str, operation: str = "") -> str:
        """Validate and normalize file path."""
        if not path or path.strip() == "":
            raise FileOperationError(f"Path required for {operation}")
        return path.strip()

    def _ensure_directory(self, path: str) -> None:
        """Ensure directory exists for the given file path."""
        dir_path = os.path.dirname(path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
            print(f"DEBUG: Created directory: {dir_path}")

    def _safe_file_operation(self, operation_func, *args, **kwargs) -> str:
        """Safely execute file operations with error handling."""
        try:
            return operation_func(*args, **kwargs)
        except FileNotFoundError as e:
            return f"File not found: {e}"
        except PermissionError as e:
            return f"Permission denied: {e}"
        except OSError as e:
            return f"OS error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    # Individual action implementations
    def _create_test(self) -> str:
        """Create test directory and file."""
        test_dir = os.path.join(os.getcwd(), "test")
        os.makedirs(test_dir, exist_ok=True)
        test_file = os.path.join(test_dir, "test_file.txt")

        with open(test_file, "w", encoding='utf-8') as f:
            f.write("This is a test file created by the File Agent")

        return f"✅ Created test directory and file at: {test_file}"

    def _list_directory(self, path: str) -> str:
        """List directory contents."""
        try:
            path = self._validate_path(path, "list directory")

            if not os.path.exists(path):
                return f"❌ Directory not found: {path}"

            if not os.path.isdir(path):
                return f"❌ Path is not a directory: {path}"

            contents = os.listdir(path)
            if not contents:
                return f"📁 Directory '{path}' is empty"

            file_info = []
            for item in sorted(contents):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    file_info.append(f"📄 {item} ({size} bytes)")
                elif os.path.isdir(item_path):
                    file_info.append(f"📁 {item}/")

            return f"📁 Contents of '{path}':\n" + "\n".join(file_info)

        except Exception as e:
            return f"❌ Error listing directory: {e}"

    def _read_file(self, path: str) -> str:
        """Read file contents."""
        try:
            path = self._validate_path(path, "read file")

            if not os.path.exists(path):
                return f"❌ File not found: {path}"

            if os.path.isdir(path):
                return f"❌ Cannot read directory as file: {path}"

            with open(path, "r", encoding='utf-8') as f:
                content = f.read()

            return f"📄 Contents of '{path}':\n{'-' * 40}\n{content}\n{'-' * 40}"

        except UnicodeDecodeError:
            return f"❌ Cannot read binary file: {path}"
        except Exception as e:
            return f"❌ Error reading file: {e}"

    def _create_file(self, path: str, content: str = "") -> str:
        """Create a new file with optional content."""
        try:
            path = self._validate_path(path, "create file")

            # Create directory structure if needed
            self._ensure_directory(path)

            # Check if file already exists
            if os.path.exists(path):
                return f"⚠️ File already exists: {path}. Use 'write_file' to overwrite or 'update_file' to modify."

            with open(path, "w", encoding='utf-8') as f:
                f.write(content)

            return f"✅ Created file: {path} ({len(content)} characters)"

        except Exception as e:
            return f"❌ Error creating file: {e}"

    def _create_folder(self, path: str) -> str:
        """Create a new directory."""
        try:
            path = self._validate_path(path, "create folder")

            if os.path.exists(path):
                if os.path.isdir(path):
                    return f"⚠️ Directory already exists: {path}"
                else:
                    return f"❌ Path exists as file, cannot create directory: {path}"

            os.makedirs(path, exist_ok=True)
            return f"✅ Created directory: {path}"

        except Exception as e:
            return f"❌ Error creating directory: {e}"

    def _write_file(self, path: str, content: str) -> str:
        """Write content to file (creates or overwrites)."""
        try:
            path = self._validate_path(path, "write file")

            # Create directory structure if needed
            self._ensure_directory(path)

            action = "Updated" if os.path.exists(path) else "Created"

            with open(path, "w", encoding='utf-8') as f:
                f.write(content)

            return f"✅ {action} file: {path} ({len(content)} characters)"

        except Exception as e:
            return f"❌ Error writing file: {e}"

    def _update_file(self, path: str, content: str, mode: str = "append") -> str:
        """Update existing file content."""
        try:
            path = self._validate_path(path, "update file")

            if not os.path.exists(path):
                return f"❌ File not found: {path}. Use 'create_file' first."

            if mode == "replace":
                with open(path, "w", encoding='utf-8') as f:
                    f.write(content)
                return f"✅ Replaced content in: {path}"

            elif mode == "append":
                with open(path, "a", encoding='utf-8') as f:
                    f.write(content)
                return f"✅ Appended to: {path}"

            elif mode == "prepend":
                with open(path, "r", encoding='utf-8') as f:
                    existing_content = f.read()
                with open(path, "w", encoding='utf-8') as f:
                    f.write(content + existing_content)
                return f"✅ Prepended to: {path}"
            else:
                return f"❌ Invalid mode: {mode}. Use 'append', 'prepend', or 'replace'"

        except Exception as e:
            return f"❌ Error updating file: {e}"

    def _query_file(self, path: str, query: str) -> str:
        """Search for text in file."""
        try:
            path = self._validate_path(path, "query file")

            if not query:
                return "❌ Query text required"

            if not os.path.exists(path):
                return f"❌ File not found: {path}"

            if os.path.isdir(path):
                return f"❌ Cannot query directory: {path}"

            with open(path, "r", encoding='utf-8') as f:
                content = f.read()

            if query.lower() in content.lower():
                lines = content.split('\n')
                matches = []
                for i, line in enumerate(lines, 1):
                    if query.lower() in line.lower():
                        matches.append(f"Line {i}: {line.strip()}")

                result = f"🔍 Found '{query}' in {path}:\n" + \
                    "\n".join(matches[:10])
                if len(matches) > 10:
                    result += f"\n... and {len(matches) - 10} more matches"
                return result
            else:
                return f"🔍 '{query}' not found in {path}"

        except UnicodeDecodeError:
            return f"❌ Cannot search binary file: {path}"
        except Exception as e:
            return f"❌ Error querying file: {e}"

    def _delete_file(self, path: str) -> str:
        """Delete a file."""
        try:
            path = self._validate_path(path, "delete file")

            if not os.path.exists(path):
                return f"❌ File not found: {path}"

            if os.path.isdir(path):
                return f"❌ Cannot delete directory as file: {path}. Use 'delete_folder'"

            os.remove(path)
            return f"✅ Deleted file: {path}"

        except Exception as e:
            return f"❌ Error deleting file: {e}"

    def _delete_folder(self, path: str, recursive: bool = False) -> str:
        """Delete a directory."""
        try:
            path = self._validate_path(path, "delete folder")

            if not os.path.exists(path):
                return f"❌ Directory not found: {path}"

            if not os.path.isdir(path):
                return f"❌ Path is not a directory: {path}. Use 'delete_file'"

            if recursive:
                shutil.rmtree(path)
                return f"✅ Deleted directory and contents: {path}"
            else:
                try:
                    os.rmdir(path)
                    return f"✅ Deleted empty directory: {path}"
                except OSError:
                    return f"❌ Directory not empty: {path}. Use recursive=true to delete with contents"

        except Exception as e:
            return f"❌ Error deleting directory: {e}"

    def _copy_file(self, source: str, destination: str) -> str:
        """Copy a file."""
        try:
            if not source or not destination:
                return "❌ Both source and destination required"

            if not os.path.exists(source):
                return f"❌ Source file not found: {source}"

            if os.path.isdir(source):
                return f"❌ Cannot copy directory as file: {source}"

            # Create destination directory if needed
            self._ensure_directory(destination)

            shutil.copy2(source, destination)
            return f"✅ Copied {source} → {destination}"

        except Exception as e:
            return f"❌ Error copying file: {e}"

    def _move_file(self, source: str, destination: str) -> str:
        """Move/rename a file."""
        try:
            if not source or not destination:
                return "❌ Both source and destination required"

            if not os.path.exists(source):
                return f"❌ Source not found: {source}"

            # Create destination directory if needed
            self._ensure_directory(destination)

            shutil.move(source, destination)
            return f"✅ Moved {source} → {destination}"

        except Exception as e:
            return f"❌ Error moving file: {e}"

    def _get_help(self) -> str:
        """Return help information."""
        return """🔧 File System Agent Commands:

📁 DIRECTORY OPERATIONS:
  • create_folder - Create directory
  • list - List directory contents
  • delete_folder - Delete directory

📄 FILE OPERATIONS:  
  • create_file - Create new file
  • write_file - Write to file (overwrite)
  • read - Read file contents
  • update_file - Modify file (append/prepend/replace)
  • query_file - Search in file
  • delete_file - Delete file
  • copy_file - Copy file
  • move_file - Move/rename file

🔧 UTILITY:
  • create_test - Create test directory/file

📝 JSON EXAMPLES:
  {"action": "create_file", "path": "readme.txt", "content": "Hello"}
  {"action": "create_folder", "path": "documents"}
  {"action": "copy_file", "source": "file1.txt", "destination": "backup/file1.txt"}
  
💬 NATURAL LANGUAGE:
  "create file called example.txt"
  "create folder documents"
  "list files"
  "read test file"
  "write to file.txt Hello World"
  "search for text in file.txt"
  "copy file1.txt to backup.txt"

Type 'exit' to quit."""

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("This tool does not support async")


class FilesAgent:
    """Main agent class for file operations."""

    def __init__(self):
        self.llm = self._initialize_llm()
        self.tools = [FileExplorerTool()]

    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the language model."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        return ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            openai_api_key=api_key
        )

    def help(self):
        """Display available commands and their usage."""
        help_text = """
🔧 File System Agent Commands:

📄 FILE OPERATIONS:
- create file [name] - Create a new file
- write to [file] [content] - Write content to a file
- read [file] - Read file contents
- update [file] [content] - Update file contents
- delete file [name] - Delete a file
- copy [source] to [destination] - Copy a file
- move [source] to [destination] - Move/rename a file

📁 FOLDER OPERATIONS:
- create folder [name] - Create a new folder
- delete folder [name] - Delete a folder
- list [path] - List directory contents

🔍 SEARCH:
- search for [query] in [file] - Search for text in a file
- search in [file] for [query] - Alternative search syntax

🔧 SPECIAL COMMANDS:
- create test - Create test directory and file
- help - Display this help message
- exit - Quit the program

📝 EXAMPLES:
- create file demo.txt
- write to demo.txt "Hello World"
- list
- search for "Hello" in demo.txt
- copy demo.txt to backup.txt
- move demo.txt to new_location/demo.txt
- create folder documents
- delete file old.txt

💡 JSON FORMAT (alternative):
{"action": "create_file", "path": "test.txt", "content": "Hello"}
{"action": "write_file", "path": "test.txt", "content": "New content"}
{"action": "list", "path": "."}
"""
        return help_text

    def _get_response(self, user_input: str) -> str:
        """Process user input and return response."""
        try:
            print(f"DEBUG: Processing input: {repr(user_input)}")

            # Handle help command
            if user_input.lower() in ["help", "commands", "?", "what can you do"]:
                return self.help()

            # Use the tool directly for all processing
            return self.tools[0]._run(user_input)

        except Exception as e:
            return f"❌ Error processing request: {str(e)}"

    def run(self):
        """Main application loop."""
        self._print_welcome()

        while True:
            try:
                user_input = input("\n🤖 You: ").strip()

                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("\n👋 Goodbye!")
                    break

                if not user_input:
                    continue

                response = self._get_response(user_input)
                print(f"\n🔧 Agent: {response}")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

    def _print_welcome(self):
        """Print welcome message and instructions."""
        print("🔧 File System Agent - Type 'exit' to quit")
        print("\n📋 Quick Commands:")
        print("  • help - Show all commands")
        print("  • create test - Create test files")
        print("  • list - List current directory")
        print("\n💡 Example commands:")
        print("  • create file readme.txt")
        print("  • write to readme.txt \"Hello World\"")
        print("  • create folder documents")
        print("  • list")
        print("  • search for \"Hello\" in readme.txt")
        print("\n💬 Both natural language and JSON formats supported!")


def main():
    """Main function to run the file system agent."""
    try:
        agent = FilesAgent()
        agent.run()
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        print("💡 Please check your OpenAI API key and dependencies.")


if __name__ == "__main__":
    main()
