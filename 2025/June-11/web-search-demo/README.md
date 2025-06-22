# Web Search Agent Demo

This demo is part of the Frederick Python Meetup series, designed for Python developers to explore how to build a simple web-search agent using LangChain and Tavily.

## Resources
- [Tavily Search](https://app.tavily.com/)
- [Tavily API Docs](https://docs.tavily.com/)
- [OpenAI GPT-4.1](https://platform.openai.com/docs/models/gpt-4)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Anthropic Workflows Overview](https://docs.anthropic.com/claude/docs/workflows)
- [Python Frederick Meetup](https://www.meetup.com/pythonfrederick/)

## Features
- Uses Tavily web search as a tool
- Powered by OpenAI's GPT-4.1 model
- Command-line interface for interactive search

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```
2. Install dependencies:
```bash
pip install -r ../calculator-demo/requirements.txt
```
3. Add your API keys to `.env`:
```
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
```

## Usage
Run the agent:
```bash
python basic_web_search_agent.py
```

## Requirements
- Python 3.11 or higher
- OpenAI API key
- Tavily API key

---
This project demonstrates how to connect LLMs to real-time web search for enhanced agent capabilities.
