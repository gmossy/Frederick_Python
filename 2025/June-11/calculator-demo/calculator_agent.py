"""
calculator_agent.py
-------------------
A command-line calculator agent demo using LangChain and OpenAI's GPT-4.1.

- Loads environment variables from the nearest .env file (recommended: one per month/project root).
- Requires OPENAI_API_KEY to be set in the .env file at the root of the month directory (e.g., June-11/.env).
- Demonstrates a custom calculator tool and agent orchestration.

Usage:
    python3 calculator_agent.py
"""

import os
from dotenv import load_dotenv
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool, Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import initialize_agent, AgentType

# Load environment variables from .env (should be at month/project root)
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
print('Loaded OPENAI_API_KEY:', api_key)
if not api_key:
    print('WARNING: OPENAI_API_KEY is missing or empty! Please set it in your .env file.')


class CalculatorTool(BaseTool):
    """
    Custom tool for evaluating mathematical expressions using Python's eval().
    WARNING: eval() is dangerous if input is not trusted! This is for demo purposes only.
    """
    name: str = "calculator"
    description: str = "Useful for mathematical calculations. Input should be a mathematical expression."

    def _run(self, query: str) -> str:
        """Synchronously evaluate a mathematical expression from the agent."""
        try:
            # Evaluate the mathematical expression (unsafe for untrusted input!)
            result = eval(query)
            return str(result)
        except Exception as e:
            return f"Error calculating expression: {str(e)}"

    async def _arun(self, query: str) -> str:
        """Async version not implemented for this CPU-bound task."""
        raise NotImplementedError("This tool does not support async")


class CalculatorAgent:
    """
    Orchestrates the OpenAI LLM and the calculator tool as a LangChain agent.
    Handles user input, agent invocation, and output display.
    """
    def __init__(self):
        # Initialize the OpenAI chat model
        self.llm = ChatOpenAI(
            model="gpt-4.1",
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        # Initialize tools
        self.tools = [CalculatorTool()]
        # Initialize the agent
        self.agent = self._initialize_agent()

    def _initialize_agent(self):
        """Set up the LangChain agent with the calculator tool and LLM."""
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )
        return agent

    def _get_response(self, user_input: str) -> str:
        """Query the agent and return its response to the user's input. Handles None responses gracefully and prevents StdOutCallbackHandler errors."""
        try:
            response = self.agent.invoke({"input": user_input})
            # Patch: If the agent returns None, return a dict with an error message to prevent downstream .get on NoneType
            if response is None:
                response = {"output": "Error: Agent did not return any response."}
            if not isinstance(response, dict):
                return f"Error: Unexpected agent response type: {type(response)}. Value: {response}"
            return response.get("output", "No response generated")
        except Exception as e:
            return f"Error processing request: {str(e)}"




    def run(self):
        """Main loop: prompt user, send input to agent, print result."""
        print("Calculator Agent - Type 'exit' to quit")
        print("Enter mathematical expressions to solve:")
        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.lower() == "exit":
                    print("\nGoodbye!")
                    break
                response = self._get_response(user_input)
                print(f"\nCalculator: {response}")
            except Exception as e:
                print(f"Error: {str(e)}")
                continue


def main():
    """Entry point for running the calculator agent from the command line."""
    agent = CalculatorAgent()
    agent.run()

if __name__ == "__main__":
    main()
