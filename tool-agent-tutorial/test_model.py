import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

def test_model():
    """Test the OpenAI model configuration"""
    try:
        # Verify API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable is not set")
            return
        print(f"API key loaded successfully (last 4 chars: {api_key[-4:]})")
        
        # Initialize the OpenAI chat model
        llm = ChatOpenAI(
            model="gpt-4.1",  # One of the allowed models in your project
            temperature=0.1,
            openai_api_key=api_key
        )
        
        # Test with a simple prompt
        response = llm.invoke("What is 2 + 2?")
        print("Model Response:", response)
        
        print("\nModel test successful!")
        
    except Exception as e:
        print(f"Error testing model: {str(e)}")

if __name__ == "__main__":
    test_model()
