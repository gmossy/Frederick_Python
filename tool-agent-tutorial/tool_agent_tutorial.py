# Tutorial 2: Tool-Using Agent
# Frederick Python Meetup - AI Agents Workshop

import os
import json
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Custom Tools Definition
class CalculatorTool(BaseTool):
    """
    A simple calculator tool for basic mathematical operations.
    This shows how to create custom tools for agents.
    """
    name: str = "calculator"
    description: str = "Useful for mathematical calculations. Input should be a mathematical expression."
    
    def _run(self, expression: str) -> str:
        """Execute the calculator tool"""
        try:
            # Safety: only allow basic mathematical operations
            allowed_chars = "0123456789+-*/.() "
            if not all(c in allowed_chars for c in expression):
                return "Error: Only basic mathematical operations are allowed"
            
            # Evaluate the expression safely
            result = eval(expression)
            return f"The result of {expression} is {result}"
        except Exception as e:
            return f"Error calculating {expression}: {str(e)}"

class WebSearchTool(BaseTool):
    """
    A simplified web search tool using a free API.
    In production, you'd use proper search APIs like Google Custom Search.
    """
    name: str = "web_search"
    description: str = "Search the web for current information. Input should be a search query."
    
    def _run(self, query: str) -> str:
        """Execute web search (simplified version for demo)"""
        try:
            # Using a free API for demo purposes
            # In production, use Google Custom Search, Bing, or similar
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            # Extract relevant information
            if "AbstractText" in data and data["AbstractText"]:
                return f"Search result for '{query}': {data['AbstractText']}"
            elif "Answer" in data and data["Answer"]:
                return f"Answer for '{query}': {data['Answer']}"
            else:
                return f"No specific answer found for '{query}'. Try rephrasing your question."
                
        except Exception as e:
            return f"Error searching for '{query}': {str(e)}"

class PythonCodeExecutor(BaseTool):
    """
    A safe Python code executor for simple operations.
    WARNING: This is simplified for demo - never use eval() in production!
    """
    name: str = "python_executor"
    description: str = "Execute simple Python code. Input should be valid Python code."
    
    def _run(self, code: str) -> str:
        """Execute Python code safely (demo version)"""
        try:
            # DEMO ONLY: Very limited safe execution
            # In production, use containers or sandboxed environments
            allowed_imports = ["math", "datetime", "random"]
            
            # Check for dangerous operations
            dangerous_keywords = ["import", "open", "file", "__", "exec", "eval"]
            if any(keyword in code.lower() for keyword in dangerous_keywords if keyword not in ["import math", "import datetime", "import random"]):
                return "Error: Code contains potentially unsafe operations"
            
            # Create a restricted execution environment
            safe_dict = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "sum": sum,
                    "max": max,
                    "min": min,
                    "range": range,
                }
            }
            
            # Capture output
            from io import StringIO
            import sys
            old_stdout = sys.stdout
            sys.stdout = output = StringIO()
            
            try:
                exec(code, safe_dict)
                result = output.getvalue()
                return result if result else "Code executed successfully (no output)"
            finally:
                sys.stdout = old_stdout
                
        except Exception as e:
            return f"Error executing code: {str(e)}"

class ToolUsingAgent:
    """
    An agent that can use multiple tools to accomplish tasks.
    This demonstrates the power of tool-augmented AI agents.
    """
    
    def __init__(self):
        # Initialize the OpenAI chat model
        self.llm = ChatOpenAI(
            model="gpt-4.1",  # One of the allowed models in your project
            temperature=0.1,  # Lower temperature for more consistent tool usage
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize our tools
        self.tools = [
            CalculatorTool(),
            WebSearchTool(),
            PythonCodeExecutor()
        ]
        
        # Create the agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant for the Frederick Python Meetup.
            You have access to several tools that can help you answer questions and solve problems.
            
            Available tools:
            - calculator: For mathematical calculations
            - web_search: For searching current information online  
            - python_executor: For running simple Python code
            
            Use tools when they would be helpful to provide accurate, up-to-date information.
            Always explain your reasoning and show your work when using tools.
            Be encouraging and educational in your responses."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the agent
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create the agent executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,  # Show reasoning steps
            max_iterations=3,  # Prevent infinite loops
            return_intermediate_steps=True
        )
        
        # Store conversation history
        self.chat_history = []
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input and return response with tool usage information
        """
        try:
            # Execute the agent
            result = self.agent_executor.invoke({
                "input": user_input,
                "chat_history": self.chat_history
            })
            
            # Update chat history
            self.chat_history.append(("human", user_input))
            self.chat_history.append(("ai", result["output"]))
            
            # Keep chat history manageable
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            return {
                "response": result["output"],
                "tools_used": [step[0].tool for step in result.get("intermediate_steps", [])],
                "reasoning_steps": len(result.get("intermediate_steps", []))
            }
            
        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "tools_used": [],
                "reasoning_steps": 0
            }

def demo_tool_agent():
    """
    Demo function to showcase the tool-using agent
    """
    print("🛠️  Frederick Python Meetup - Tool-Using Agent Demo")
    print("=" * 60)
    print("This agent can use tools: Calculator, Web Search, Python Executor")
    print("Type 'quit' to exit")
    print()
    
    # Example questions to suggest
    print("💡 Try asking:")
    print("- What's 15% of 247?")
    print("- Search for latest Python news")
    print("- Calculate the factorial of 5 using Python")
    print("- What's the weather like today?")
    print()
    
    # Create our agent
    agent = ToolUsingAgent()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Thanks for exploring tools with me!")
                break
            elif not user_input:
                continue
            
            # Get agent response
            print("\n🤖 Agent thinking...")
            result = agent.chat(user_input)
            
            print(f"\n🤖 Agent: {result['response']}")
            
            # Show tool usage information
            if result['tools_used']:
                print(f"\n🛠️  Tools used: {', '.join(result['tools_used'])}")
                print(f"🧠 Reasoning steps: {result['reasoning_steps']}")
            
            print("\n" + "-" * 50 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

# Example usage and testing
if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set your OPENAI_API_KEY in a .env file")
        exit(1)
    
    # Run the demo
    demo_tool_agent()

# Practice Exercises for Meetup Participants:
"""
🏃‍♂️ Advanced Exercises:

1. BEGINNER: Create a new tool that converts temperatures between Celsius and Fahrenheit

2. INTERMEDIATE: Add a tool that can read and summarize text files
   Hint: Use the file reading capabilities with safety checks

3. ADVANCED: Create a tool that can interact with a simple database or API
   Hint: Use requests library to interact with a public API

4. CHALLENGE: Implement tool result caching to avoid repeated calculations
   Hint: Store tool results with input hashes as keys

5. EXPERT: Add tool dependency management (some tools need results from others)
   Hint: Modify the agent to recognize when tools should be chained together
"""