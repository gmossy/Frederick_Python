# Tool Agent Tutorial

This tutorial is part of the Frederick Python Meetup series for Python developers, focusing on building multi-tool AI agents with LangChain.

## Resources
- [Tavily Search](https://app.tavily.com/)
- [Tavily API Docs](https://docs.tavily.com/)
- [OpenAI GPT-4.1](https://platform.openai.com/docs/models/gpt-4)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Anthropic Workflows Overview](https://docs.anthropic.com/claude/docs/workflows)
- [Python Frederick Meetup](https://www.meetup.com/pythonfrederick/)

## Features
- Combines multiple tools: Calculator and Tavily web search
- Powered by OpenAI's GPT-4.1 model
- Extensible: add your own tools easily
- Command-line interface for interactive agent use

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
python basic_tool_agent.py
```

## Requirements
- Python 3.11 or higher
- OpenAI API key
- Tavily API key

---
This project demonstrates how to build and extend agents that combine multiple tools for more advanced LLM applications.
