# Tool Agent Tutorial

This project was created for the Frederick Python Meetup to demonstrate how to create a tool agent using OpenAI's GPT-4.1 model.

A Python project demonstrating how to create a tool agent with OpenAI and Python.

## Setup Instructions

1. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**:
   - Copy the `.env.example` file to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file and add your API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

4. **Run the Application**:
   ```bash
   python tool_agent_tutorial.py
   ```

## Project Structure

- `tool_agent_tutorial.py`: Main application file containing the tool agent implementation
- `.env`: Configuration file for environment variables
- `requirements.txt`: List of project dependencies

## Requirements

- Python 3.11 or higher
- OpenAI API key
- Internet connection for API calls

## Usage

The tool agent can be used to process user input and utilize various tools through the OpenAI API. The application maintains a chat history to provide context-aware responses.

### Model Configuration

The LLM model can be configured in the [ToolUsingAgent](cci:2://file:///Users/gmossy/Frederick_Python/tool-agent-tutorial/tool_agent_tutorial.py:129:0-217:5) class initialization. By default, it uses `gpt-4.1-nano`, but you can change it by modifying the `model` parameter in the `ChatOpenAI` initialization:

```python
self.llm = ChatOpenAI(
    model="gpt-4.1-nano",  # Change this to your desired model
    temperature=0.1,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
```

This project uses the `gpt-4.1` model from OpenAI.

Note: The model configuration is set in the [ToolUsingAgent](cci:2://file:///Users/gmossy/Frederick_Python/tool-agent-tutorial/tool_agent_tutorial.py:129:0-217:5) class initialization.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
