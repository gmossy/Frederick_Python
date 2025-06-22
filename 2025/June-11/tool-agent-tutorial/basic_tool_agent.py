import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools.tavily_search import TavilySearchResults
from langchain_core.tools import Tool

# Load environment variables
load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.1,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Calculator Tool
class CalculatorTool(Tool):
    name = "calculator"
    description = "Useful for mathematical calculations. Input should be a mathematical expression."

    def _run(self, query: str) -> str:
        try:
            result = eval(query)
            return str(result)
        except Exception as e:
            return f"Error calculating expression: {str(e)}"

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("This tool does not support async")

# Tavily Search Tool
search = TavilySearchResults(api_key=os.getenv("TAVILY_API_KEY"))

# Add more tools as needed
calculator = CalculatorTool()
tools = [calculator, search]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

def main():
    print("Tool Agent - Type 'exit' to quit")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break
        response = agent.invoke({"input": user_input})
        print(f"\nAgent: {response['output']}")

if __name__ == "__main__":
    main()
