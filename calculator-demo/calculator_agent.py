import os
from dotenv import load_dotenv
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool, Tool
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import initialize_agent, AgentType

# Load environment variables
load_dotenv()


class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = "Useful for mathematical calculations. Input should be a mathematical expression."

    def _run(self, query: str) -> str:
        """Run the calculator tool."""
        try:
            # Evaluate the mathematical expression
            result = eval(query)
            return str(result)
        except Exception as e:
            return f"Error calculating expression: {str(e)}"

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("This tool does not support async")
        # The core logic of our tool is result = eval(query). This is a purely CPU-bound operation. 
        # The processor is actively engaged in calculating the mathematical result. There is no waiting period.


class CalculatorAgent:
    def __init__(self):
        # Initialize the OpenAI chat model
        # Initialize the calculator agent with the OpenAI model and tools."""
        self.llm = ChatOpenAI(
            model="gpt-4.1",  # Using GPT-4.1 for better performance
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Initialize tools
        self.tools = [CalculatorTool()]

        # Initialize the agent
        self.agent = self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the agent with the calculator tool."""
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
        """Run the calculator agent."""
        print("Calculator Agent - Type 'exit' to quit")
        print("Enter mathematical expressions to solve:")

        while True:
            try:
                # Get user input
                user_input = input("\nYou: ")

                if user_input.lower() == "exit":
                    print("\nGoodbye!")
                    break

                # Get agent response
                response = self._get_response(user_input)

                print(f"\nCalculator: {response}")

            except Exception as e:
                print(f"Error: {str(e)}")
                continue


def main():
    """Main function to run the calculator agent."""
    agent = CalculatorAgent()
    agent.run()


if __name__ == "__main__":
    main()
