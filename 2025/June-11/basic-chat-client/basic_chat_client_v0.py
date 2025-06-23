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
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env (should be at month/project root)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print("Loaded OPENAI_API_KEY:", api_key)
if not api_key:
    print("WARNING: OPENAI_API_KEY is missing or empty! Please set it in your .env file.")

client = OpenAI(api_key=api_key)

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
print("\nAI Response:\n", response)
