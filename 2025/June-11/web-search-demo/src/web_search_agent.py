"""
web_search_agent.py
------------------
A web search agent demo using LangChain and OpenAI.

- Loads environment variables from the nearest .env file (should be at month/project root).
- Requires OPENAI_API_KEY to be set in the .env file at the root of the month directory (e.g., June-11/.env).

Usage:
    python3 src/web_search_agent.py
"""

import os
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import HumanMessage, AIMessage
from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from langchain_core.output_parsers import JsonOutputParser
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI

# Load environment variables from .env (should be at month/project root)
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
print('Loaded OPENAI_API_KEY:', api_key)
if not api_key:
    print('WARNING: OPENAI_API_KEY is missing or empty! Please set it in your .env file.')

class WebSearchTool:
    """Tool for performing web searches."""
    name = "web_search"
    description = "Search the web for information"
    is_single_input = True

    @tool
    def search_web(self, query: str) -> str:
        """Search the web for information.
        
        Args:
            query: The search query to perform
            
        Returns:
            Formatted search results
        """
        try:
            results = []
            for url in search(query, num_results=5):
                try:
                    # Get a brief snippet of content from the URL
                    response = requests.get(url, timeout=5)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Get the first paragraph or meta description
                    snippet = ''
                    if soup.find('meta', {'name': 'description'}):
                        snippet = soup.find('meta', {'name': 'description'})['content']
                    elif soup.find('p'):
                        snippet = soup.find('p').get_text()[:150] + '...'
                    
                    results.append({
                        'url': url,
                        'snippet': snippet
                    })
                except Exception as e:
                    print(f"Error fetching content from {url}: {str(e)}")
                    continue
            
            if not results:
                return "No results found for your query."
                
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(f"{i}. {result['snippet']}\nURL: {result['url']}")
            
            return "\n".join(formatted_results)
        except Exception as e:
            return f"Error performing web search: {str(e)}"

class WebSearchAgent:
    def __init__(self):
        self.tools = [WebSearchTool()]
        self.agent = self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the agent with web search tool."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful web search assistant. You have access to the web_search tool.

When responding, ONLY output the search results without any additional text.
Example: {\"action\": \"search_web\", \"query\": \"python programming\"}

Available actions:
- search_web: Performs a web search using Tavily API""")
        ])

        agent = initialize_agent(
            tools=self.tools,
            llm=self._initialize_llm(),
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            output_parser=JsonOutputParser()
        )

        return agent

    def _initialize_llm(self):
        """Initialize the language model."""
        return ChatOpenAI(model_name="gpt-4", temperature=0.7)

    def run(self):
        """Main application loop."""
        print("\n🤖 Web Search Agent - Type 'exit' to quit")
        print("💡 Type your search query or use natural language commands")
        
        while True:
            try:
                user_input = input("\n🤖 You: ").strip()
                
                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("\n👋 Goodbye!")
                    break
                    
                response = self.agent.invoke({"input": user_input})
                print(f"\n🔍 Results:\n{response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    agent = WebSearchAgent()
    agent.run()
