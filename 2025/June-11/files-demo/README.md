# File System Agent Demo

A simple LangChain agent that can explore and manage files in a directory.

## Features

- Create test files and directories
- List directory contents
- Read file contents
- Uses GPT-4.1 for natural language processing

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run the agent:
```bash
python files_agent.py
```

The agent accepts JSON-formatted queries. Example queries:

- Create test files:
```json
{"action": "create_test"}
```

- List directory contents:
```json
{"action": "list", "path": "test"}
```

- Read file contents:
```json
{"action": "read", "path": "test/test_file.txt"}
```
