# Web Search Demo Agent

A LangChain-based web search agent that uses Tavily for web search capabilities.

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Set up environment variables:
- Create a `.env` file in the project root
- Add your Tavily API key:
```
TAVILY_API_KEY=your_api_key_here
```

## Usage

Run the agent:
```bash
python src/web_search_agent.py
```

## Features
- Web search using Tavily
- Natural language query processing
- Results formatting and filtering
