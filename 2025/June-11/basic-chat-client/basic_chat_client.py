"""
basic_chat_client.py
-------------------
A minimal OpenAI chat client demo for Frederick Python Meetup.

- Loads environment variables from the nearest .env file (should be at month/project root).
- Requires OPENAI_API_KEY to be set in the .env file at the root of the month directory (e.g., June-11/.env).

Usage:
    python basic_chat_client.py
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI


def main():
    # Load environment variables from .env (should be at month/project root)
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    print("Loaded OPENAI_API_KEY:", api_key)

    # Debug information
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for .env file...")

    if not api_key:
        print("ERROR: OPENAI_API_KEY is missing or empty!")
        print("Please check:")
        print("1. Your .env file exists in the project root")
        print("2. The .env file contains: OPENAI_API_KEY=your-key-here")
        print("3. There are no extra spaces or quotes around the key")
        sys.exit(1)

    # Show partial key for verification (hide most characters for security)
    masked_key = api_key[:12] + "*" * (len(api_key) - 16) + \
        api_key[-4:] if len(api_key) > 16 else "KEY_TOO_SHORT"
    print(f"Loaded OPENAI_API_KEY: {masked_key}")

    # Validate key format
    if not api_key.startswith(('sk-', 'sk-proj-')):
        print("WARNING: API key doesn't start with expected prefix (sk- or sk-proj-)")
        print("Please verify your API key is correct")

    try:
        client = OpenAI(api_key=api_key)

        # Test the connection first
        print("Testing API connection...")

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You're a helpful assistant."},
                {
                    "role": "user",
                    "content": "Write a limerick about the Python programming language, also say hello to the Frederick Python Meetup developers"
                },
            ],
        )

        response = completion.choices[0].message.content
        print("\n" + "="*50)
        print("AI Response:")
        print("="*50)
        print(response)
        print("="*50)

    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        print("\nTroubleshooting suggestions:")
        print("1. Verify your API key at https://platform.openai.com/api-keys")
        print("2. Generate a new API key if the current one is invalid")
        print("3. Check if you have sufficient credits in your OpenAI account")
        print("4. Ensure your API key has the necessary permissions")
        sys.exit(1)


if __name__ == "__main__":
    main()
