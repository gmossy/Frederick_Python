# Calculator Demo Agent

This demo was created for the Frederick Python Meetup to showcase a specialized tool agent designed to perform mathematical calculations using OpenAI's GPT-4.1 model.

## Features

- Performs mathematical calculations
- Maintains chat history for context-aware responses
- Uses OpenAI's GPT-4.1 model
- Simple command-line interface

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the `.env` file from the tool-agent-tutorial project:
```bash
cp ../tool-agent-tutorial/.env .
```

## Usage

Run the calculator agent:
```bash
python calculator_agent.py
```

The agent will prompt you for mathematical expressions to solve. It maintains a conversation history to provide context-aware responses.

## Requirements

- Python 3.11 or higher
- OpenAI API key
- Internet connection for API calls

## Model

This project uses the `gpt-4.1` model from OpenAI.

Note: The model configuration is set in the [CalculatorAgent](cci:2://file:///Users/gmossy/Frederick_Python/calculator-demo/calculator_agent.py:42:0-100:20) class initialization.


To check your API key, run the following command:
python3 -c "import os; from dotenv import load_dotenv, find_dotenv; env_path = find_dotenv(); print('find_dotenv() found:', env_path); load_dotenv(env_path); print('Loaded OPENAI_API_KEY:', os.getenv('OPENAI_API_KEY'))"

