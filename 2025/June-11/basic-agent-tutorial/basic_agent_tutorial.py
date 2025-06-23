# Tutorial 1: Basic Conversational Agent
# Frederick Python Meetup - AI Agents Workshop

"""
basic_agent_tutorial.py
----------------------
A basic conversational agent demo for the Frederick Python Meetup.

- Loads environment variables from the nearest .env file (should be at month/project root).
- Requires OPENAI_API_KEY to be set in the .env file at the root of the month directory (e.g., June-11/.env).

Usage:
    python3 basic_agent_tutorial.py
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

# Load environment variables from .env (should be at month/project root)
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
print('Loaded OPENAI_API_KEY:', api_key)
if not api_key:
    print('WARNING: OPENAI_API_KEY is missing or empty! Please set it in your .env file.')

class BasicAgent:
    """
    A simple conversational agent with memory.
    Perfect for beginners to understand agent basics.
    """
    
    def __init__(self):
        # Initialize the OpenAI chat model
        # Using GPT-3.5-turbo for cost efficiency in demos
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,  # Some creativity, but not too much
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize memory to remember conversation history
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        
        # System prompt to define agent personality
        self.system_prompt = """You are a helpful AI assistant for the Frederick Python Meetup.
        You're knowledgeable about Python, AI, and programming in general.
        Be friendly, encouraging, and provide practical examples when possible.
        If you don't know something, say so honestly."""
    
    def chat(self, user_input: str) -> str:
        """
        Main chat method - processes user input and returns response
        """
        try:
            # Get conversation history from memory
            chat_history = self.memory.chat_memory.messages
            
            # Prepare messages for the LLM
            messages = [HumanMessage(content=self.system_prompt)]
            messages.extend(chat_history)
            messages.append(HumanMessage(content=user_input))
            
            # Get response from OpenAI
            response = self.llm.invoke(messages)
            
            # Save to memory
            self.memory.chat_memory.add_user_message(user_input)
            self.memory.chat_memory.add_ai_message(response.content)
            
            return response.content
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_conversation_summary(self) -> str:
        """
        Get a summary of the conversation so far
        """
        messages = self.memory.chat_memory.messages
        if not messages:
            return "No conversation yet."
        
        conversation = ""
        for msg in messages:
            if isinstance(msg, HumanMessage):
                conversation += f"Human: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                conversation += f"AI: {msg.content}\n"
        
        return conversation

def demo_basic_agent():
    """
    Demo function to show the basic agent in action
    """
    print("🤖 Frederick Python Meetup - Basic Agent Demo")
    print("=" * 50)
    print("Type 'quit' to exit, 'summary' to see conversation history")
    print()
    
    # Create our agent
    agent = BasicAgent()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            # Handle special commands
            if user_input.lower() == 'quit':
                print("👋 Thanks for chatting! See you at the meetup!")
                break
            elif user_input.lower() == 'summary':
                print("\n📝 Conversation Summary:")
                print("-" * 30)
                print(agent.get_conversation_summary())
                continue
            elif not user_input:
                continue
            
            # Get agent response
            print("🤖 Agent: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
            print()
            
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
        print("Example .env file content:")
        print("OPENAI_API_KEY=your_api_key_here")
        exit(1)
    
    # Run the demo
    demo_basic_agent()

# Practice Exercises for Meetup Participants:
"""
🏃‍♂️ Try These Exercises:

1. BEGINNER: Modify the system prompt to make the agent specialize in a topic you're interested in

2. INTERMEDIATE: Add a method to clear the conversation memory

3. ADVANCED: Implement conversation summarization when memory gets too long
   Hint: Use the LLM to summarize old messages when they exceed a certain count

4. CHALLENGE: Add sentiment analysis to track how the conversation is going
   Hint: Ask the LLM to rate the conversation mood on each exchange
"""