import os
from dotenv import load_dotenv
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool, Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain_core.messages import HumanMessage, AIMessage
import json

# Load environment variables
load_dotenv()


class FileExplorerTool(BaseTool):
    name: str = "file_explorer"
    description: str = "Useful for exploring and managing files in a directory. Supports actions: create_test, list, read, create_file, write_file, update_file, query_file, delete_file."

    def _run(self, query: str) -> str:
        """Run the file explorer tool."""
        try:
            # Try to parse as JSON
            try:
                query_data = json.loads(query)
                action = query_data.get("action")
                path = query_data.get("path", "test")
                content = query_data.get("content", "")
            except json.JSONDecodeError:
                # If not JSON, treat as simple action
                action = query.strip()
                path = "test"
                content = ""

            # Create test directory and file
            if action == "create_test":
                test_dir = os.path.join(os.getcwd(), "test")
                os.makedirs(test_dir, exist_ok=True)
                test_file = os.path.join(test_dir, "test_file.txt")
                with open(test_file, "w") as f:
                    f.write("This is a test file created by the File Agent")
                return f"Created test directory and file at: {test_file}"

            # List directory contents
            elif action == "list":
                if not os.path.exists(path):
                    return f"Directory not found: {path}"
                contents = os.listdir(path)
                file_info = []
                for item in contents:
                    item_path = os.path.join(path, item)
                    if os.path.isfile(item_path):
                        file_info.append(f"FILE: {item}")
                    elif os.path.isdir(item_path):
                        file_info.append(f"DIR: {item}")
                return f"Contents of {path}:\n" + "\n".join(file_info)

            # Read file contents
            elif action == "read":
                if not os.path.exists(path):
                    return f"File not found: {path}"
                if os.path.isdir(path):
                    return f"Cannot read directory as file: {path}"
                try:
                    with open(path, "r", encoding='utf-8') as f:
                        content = f.read()
                    return f"Contents of {path}:\n{content}"
                except UnicodeDecodeError:
                    return f"Cannot read file {path}: Binary file or encoding issue"

            # Create new file
            elif action == "create_file":
                if not path or path == "test":
                    return "Please specify a file path"
                try:
                    # Create directory if it doesn't exist
                    dir_path = os.path.dirname(path)
                    if dir_path:
                        os.makedirs(dir_path, exist_ok=True)

                    with open(path, "w", encoding='utf-8') as f:
                        f.write(content)
                    return f"Created file: {path}"
                except Exception as e:
                    return f"Error creating file {path}: {str(e)}"

            # Write to existing file (or create if doesn't exist)
            elif action == "write_file":
                if not path or path == "test":
                    return "Please specify a file path"
                try:
                    # Create directory if it doesn't exist
                    dir_path = os.path.dirname(path)
                    if dir_path:
                        os.makedirs(dir_path, exist_ok=True)

                    with open(path, "w", encoding='utf-8') as f:
                        f.write(content)
                    return f"Written to file: {path}"
                except Exception as e:
                    return f"Error writing to file {path}: {str(e)}"

            # Delete file
            elif action == "delete_file":
                if not os.path.exists(path):
                    return f"File not found: {path}"
                if os.path.isdir(path):
                    return f"Cannot delete directory as file: {path}"
                try:
                    os.remove(path)
                    return f"Deleted file: {path}"
                except Exception as e:
                    return f"Error deleting file {path}: {str(e)}"

            # Update file with new content (append or prepend)
            elif action == "update_file":
                if not path or path == "test":
                    return "Please specify a file path"
                if not os.path.exists(path):
                    return f"File not found: {path}. Use create_file to create it first."

                # append, prepend, or replace
                update_mode = query_data.get("mode", "append")

                try:
                    if update_mode == "replace":
                        # Replace entire file content
                        with open(path, "w", encoding='utf-8') as f:
                            f.write(content)
                        return f"Replaced content in file: {path}"

                    elif update_mode == "append":
                        # Append to end of file
                        with open(path, "a", encoding='utf-8') as f:
                            f.write(content)
                        return f"Appended content to file: {path}"

                    elif update_mode == "prepend":
                        # Read existing content, then write new content + existing
                        with open(path, "r", encoding='utf-8') as f:
                            existing_content = f.read()
                        with open(path, "w", encoding='utf-8') as f:
                            f.write(content + existing_content)
                        return f"Prepended content to file: {path}"

                    else:
                        return f"Invalid update mode: {update_mode}. Use 'append', 'prepend', or 'replace'"

                except Exception as e:
                    return f"Error updating file {path}: {str(e)}"

            # Query file content - analyze and answer questions about file
            elif action == "query_file":
                if not path or path == "test":
                    return "Please specify a file path"
                if not os.path.exists(path):
                    return f"File not found: {path}"
                if os.path.isdir(path):
                    return f"Cannot query directory as file: {path}"

                query_text = query_data.get("query", "")
                if not query_text:
                    return "Please provide a query text to search for or question to answer about the file"

                try:
                    with open(path, "r", encoding='utf-8') as f:
                        file_content = f.read()

                    # Simple text search
                    if query_text.lower() in file_content.lower():
                        # Find lines containing the query
                        lines = file_content.split('\n')
                        matching_lines = []
                        for i, line in enumerate(lines, 1):
                            if query_text.lower() in line.lower():
                                matching_lines.append(
                                    f"Line {i}: {line.strip()}")

                        # Limit to first 10 matches
                        result = f"Found '{query_text}' in {path}:\n" + \
                            "\n".join(matching_lines[:10])
                        if len(matching_lines) > 10:
                            result += f"\n... and {len(matching_lines) - 10} more matches"
                        return result
                    else:
                        return f"'{query_text}' not found in {path}"

                except UnicodeDecodeError:
                    return f"Cannot query file {path}: Binary file or encoding issue"
                except Exception as e:
                    return f"Error querying file {path}: {str(e)}"

            # Handle natural language requests
            elif any(word in action.lower() for word in ["commands", "help", "what can", "available", "actions"]):
                return """Available commands for the File System Agent:

1. create_test - Create test directory and file
2. list - List directory contents
3. read - Read file contents
4. create_file - Create a new file
5. write_file - Write content to a file
6. update_file - Update existing file content (append/prepend/replace)
7. query_file - Search for text or analyze file content
8. delete_file - Delete a file

JSON Examples:
- {"action": "create_test"}
- {"action": "list", "path": "test"}
- {"action": "read", "path": "test/test_file.txt"}
- {"action": "create_file", "path": "example.txt", "content": "Hello World"}
- {"action": "update_file", "path": "example.txt", "content": "New line", "mode": "append"}
- {"action": "query_file", "path": "example.txt", "query": "search term"}

Natural Language Examples:
- "create test files"
- "list files in test directory"
- "read the test file"
- "search for keyword in example.txt"
- "what does the config file contain?"

Type 'exit' to quit the agent."""

            elif "create test" in action.lower():
                return self._run('{"action": "create_test"}')
            elif "list" in action.lower():
                if "test" in action.lower():
                    return self._run('{"action": "list", "path": "test"}')
                else:
                    return self._run('{"action": "list", "path": "."}')
            elif "read" in action.lower() and "test" in action.lower():
                return self._run('{"action": "read", "path": "test/test_file.txt"}')
            elif "search" in action.lower() and "in" in action.lower():
                # Extract file path and search term from natural language
                words = action.split()
                if "in" in words:
                    in_index = words.index("in")
                    if in_index + 1 < len(words):
                        file_path = words[in_index + 1]
                        search_term = " ".join(
                            words[words.index("search")+2:in_index])
                        return self._run(f'{{"action": "query_file", "path": "{file_path}", "query": "{search_term}"}}')
                return "Please specify what to search for and which file, e.g., 'search for keyword in filename.txt'"

            return f"Unknown action: {action}. Available actions: create_test, list, read, create_file, write_file, update_file, query_file, delete_file"

        except Exception as e:
            return f"Error in file explorer tool: {str(e)}"

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("This tool does not support async")


class FilesAgent:
    def __init__(self):
        # Initialize the OpenAI chat model
        self.llm = ChatOpenAI(
            model="gpt-4.1",
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Initialize tools
        self.tools = [FileExplorerTool()]

        # Initialize the agent
        self.agent = self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the agent with the file explorer tool."""
        # Create the agent
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        return agent

    def _get_response(self, user_input: str) -> str:
        """Get response from the agent."""
        try:
            response = self.agent.invoke({"input": user_input})
            return response.get("output", "No response generated")
        except Exception as e:
            return f"Error processing request: {str(e)}"

    def run(self):
        """Run the file system agent."""
        print("File System Agent - Type 'exit' to quit")
        print("\nAvailable actions:")
        print("- create_test: Create test directory and file")
        print("- list: List directory contents")
        print("- read: Read file contents")
        print("- create_file: Create a new file")
        print("- write_file: Write content to a file")
        print("- update_file: Update existing file content (append/prepend/replace)")
        print("- query_file: Search for text or analyze file content")
        print("- delete_file: Delete a file")
        print("\nExample queries:")
        print('- JSON: {"action": "create_test"}')
        print('- JSON: {"action": "list", "path": "test"}')
        print('- JSON: {"action": "read", "path": "test/test_file.txt"}')
        print(
            '- JSON: {"action": "create_file", "path": "example.txt", "content": "Hello World"}')
        print(
            '- JSON: {"action": "update_file", "path": "example.txt", "content": "\\nNew line", "mode": "append"}')
        print(
            '- JSON: {"action": "update_file", "path": "example.txt", "content": "Header\\n", "mode": "prepend"}')
        print(
            '- JSON: {"action": "update_file", "path": "example.txt", "content": "Completely new content", "mode": "replace"}')
        print(
            '- JSON: {"action": "query_file", "path": "example.txt", "query": "search term"}')
        print('- Natural: "create test files"')
        print('- Natural: "list files in test directory"')
        print('- Natural: "read the test file"')
        print('- Natural: "search for keyword in example.txt"')
        print('- Natural: "what does the config file contain?"')

        while True:
            try:
                # Get user input
                user_input = input("\nYou: ")

                if user_input.lower() == "exit":
                    print("\nGoodbye!")
                    break

                # Get agent response
                response = self._get_response(user_input)
                print(f"\nAgent: {response}")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                continue


def main():
    """Main function to run the file system agent."""
    try:
        agent = FilesAgent()
        agent.run()
    except Exception as e:
        print(f"Failed to initialize agent: {str(e)}")
        print("Please check your OpenAI API key and dependencies.")


if __name__ == "__main__":
    main()
