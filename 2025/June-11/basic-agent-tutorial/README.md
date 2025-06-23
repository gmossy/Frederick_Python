# Basic Agent Tutorial

A simple conversational agent demo for the Frederick Python Meetup.

## Features
- Uses OpenAI's GPT models via LangChain
- Maintains conversation memory
- Loads API key from a `.env` file
- CLI interface for interactive chat

## Setup

1. **Install dependencies:**
   ```bash
   pip install langchain openai python-dotenv
   ```

2. **Set up your environment variables:**
   - The `.env` file should be located in the **June-11 month folder**:
     ```
     /Users/gmossy/Frederick_Python/2025/June-11/.env
     ```
   - It must include your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

3. **Run the agent:**
   ```bash
   python basic_agent_tutorial.py
   ```

## Troubleshooting
- If the script cannot find your API key, ensure you are running it from a subfolder of the June-11 directory and that the `.env` file exists at the month root.
- To check which `.env` is being loaded, run:
  ```bash
  python3 -c "import os; from dotenv import load_dotenv, find_dotenv; env_path = find_dotenv(); print('find_dotenv() found:', env_path); load_dotenv(env_path); print('Loaded OPENAI_API_KEY:', os.getenv('OPENAI_API_KEY'))"
  ```

---
**.env Location:**
- The `.env` file should be at: `/Users/gmossy/Frederick_Python/2025/June-11/.env`
- Do NOT place `.env` files in subfolders.
