# LangGraph Agentic Chatbot

This directory contains a LangGraph-based implementation of the agentic chatbot, providing a more structured and maintainable approach to conversation flow management using state graphs.

## Overview

The LangGraph agent is a reimplementation of the original `chatbot_agentic_v3.py` using LangGraph's state management and workflow orchestration capabilities. It maintains the same functionality while providing better structure and flow control.

## Key Features

- **State Management**: Uses LangGraph's state management to track conversation context
- **Node-based Workflow**: Implements conversation flow as a series of connected nodes
- **Function Calling**: Supports OpenAI function calling for tool usage
- **Memory Management**: Maintains chat history and user information
- **Vector Database Integration**: Stores and retrieves conversation context
- **Error Handling**: Robust error handling and fallback mechanisms

## Architecture

### Components

1. **AgentState** (`agent_state.py`): Defines the state schema for the conversation
2. **AgenticChatbot** (`agentic_chatbot.py`): Main chatbot implementation with LangGraph workflow
3. **Chat Interface** (`chat_in_terminal.py`): Terminal-based chat interface
4. **Example Usage** (`example_usage.py`): Programmatic usage examples

### Workflow Nodes

1. **Initialize Conversation**: Sets up session and user context
2. **Generate Response**: Uses OpenAI API to generate responses or function calls
3. **Execute Function**: Handles function calls (vector search, user info storage)
4. **Finalize Response**: Updates chat history and vector database

### Available Functions

- `search_vector_db`: Search the vector database for relevant information
- `add_user_info_to_database`: Store user information in the database

## Usage

### Prerequisites

Ensure you have the following installed:

- Python 3.8+
- OpenAI API key (set in `.env` file)
- Required dependencies (see `requirements.txt`)

### Terminal Interface

Run the interactive terminal chat:

```bash
python langgraph/chat_in_terminal.py
```

### Programmatic Usage

```python
from langgraph.agentic_chatbot import AgenticChatbot

# Initialize the chatbot
chatbot = AgenticChatbot()

# Send a message
response = chatbot.chat("Hello, what can you help me with?")
print(response)

# The chatbot will automatically handle:
# - Function calls when needed
# - User information storage
# - Vector database searches
# - Chat history management
```

### Example Run

```bash
python langgraph/example_usage.py
```

## Configuration

The LangGraph implementation uses a centralized configuration system through `config.py` and environment variables.

### Environment Variables

Create a `.env` file in the langgraph directory with the following variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
CHAT_MODEL=gpt-4-turbo-preview
SUMMARY_MODEL=gpt-3.5-turbo
TEMPERATURE=0.7

# LangSmith Configuration
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=agentic-chatbot
LANGSMITH_TRACING=true

# Database Configuration
DB_PATH=../data/chatbot.db
VECTOR_DB_PATH=../data/vector_db

# Chat History Configuration
MAX_HISTORY_PAIRS=10
MAX_TOKENS=4000
MAX_CHARACTERS=8000

# Function Call Configuration
MAX_FUNCTION_CALLS=5
```

### Configuration System

The configuration system (`config.py`) provides:

- **Centralized Settings**: All configuration in one place
- **Environment Variable Loading**: Automatic loading from `.env`
- **Default Values**: Sensible defaults for optional settings
- **Validation**: Checks for required configuration
- **Type Safety**: All values properly typed and converted

### Usage

```python
from config import config

# Access configuration
openai_config = config.get_openai_config()
langsmith_config = config.get_langsmith_config()
db_config = config.get_db_config()
chat_config = config.get_chat_config()

# Or access individual settings
chat_model = config.chat_model
max_tokens = config.max_tokens
```

### Required Variables

The following variables must be set:

- `OPENAI_API_KEY`: Your OpenAI API key
- `LANGSMITH_API_KEY`: Your LangSmith API key (if tracing is enabled)

All other variables have default values but can be customized as needed.

## Comparison with Original

### Advantages of LangGraph Implementation

1. **Better Flow Control**: Explicit state transitions and workflow management
2. **Easier Debugging**: Clear separation of concerns and state visibility
3. **More Maintainable**: Modular design with separate nodes for different functions
4. **Better Error Handling**: Structured error management through state
5. **Enhanced Monitoring**: Built-in checkpointing and state persistence

### Maintained Features

- All original functionality preserved
- Same function calling capabilities
- Identical user experience
- Compatible with existing databases and configurations

## State Schema

The `AgentState` tracks:

- User messages and responses
- Chat history and summaries
- Function call tracking
- Session and user IDs
- Error states
- System prompts and context

## Error Handling

The implementation includes comprehensive error handling:

- Function call failures
- API errors
- Database connection issues
- Invalid state transitions
- Fallback mechanisms

## LangSmith Integration

The LangGraph implementation now includes LangSmith integration for enhanced observability and debugging. This provides:

- **Tracing**: All LangGraph operations are automatically traced
- **Visualization**: See the workflow execution in real-time
- **Performance Monitoring**: Track latency and usage metrics
- **Debug Information**: Detailed logs for each node in the graph

### Node Tags

Each node in the workflow is tagged for easy filtering in the LangSmith dashboard:

- `initialization`: Initial conversation setup
- `generation`: Response generation using OpenAI
- `function_execution`: Function calls (vector search, user info storage)
- `finalization`: Response finalization and history updates

### Run Metadata

Each conversation run includes metadata:

- User ID
- Timestamp
- Chat model used
- Temperature setting

### Setup

1. Sign up at [smith.langchain.com](https://smith.langchain.com)
2. Get your API key from the dashboard
3. Add to your `.env`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
CHAT_MODEL=gpt-4-turbo-preview
SUMMARY_MODEL=gpt-3.5-turbo
TEMPERATURE=0.7

# LangSmith Configuration
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=agentic-chatbot
LANGSMITH_TRACING=true

# Database Configuration
DB_PATH=../data/chatbot.db
VECTOR_DB_PATH=../data/vector_db

# Chat History Configuration
MAX_HISTORY_PAIRS=10
MAX_TOKENS=4000
MAX_CHARACTERS=8000

# Function Call Configuration
MAX_FUNCTION_CALLS=5
```

### Viewing Traces

1. Visit [smith.langchain.com](https://smith.langchain.com)
2. Go to "Traces" section
3. Filter by project "agentic-chatbot"
4. Click any trace to see the execution flow

This integration helps with:

- Debugging conversation flows
- Optimizing performance
- Understanding function call patterns
- Monitoring system health

## Future Enhancements

Potential improvements for the LangGraph implementation:

1. **Multi-tool Support**: Easy addition of new tools and functions
2. **Parallel Processing**: Concurrent function calls
3. **Advanced Routing**: Conditional workflows based on user intent
4. **State Persistence**: Long-term conversation state storage
5. **Monitoring and Analytics**: Built-in conversation analytics

## Development

To modify or extend the LangGraph agent:

1. **Add New Functions**: Update `agent_functions` in `AgenticChatbot.__init__`
2. **Modify Workflow**: Edit the graph structure in `_create_graph`
3. **Add New Nodes**: Create new node functions and add them to the workflow
4. **Update State**: Modify `AgentState` to track additional information

## Troubleshooting

Common issues and solutions:

1. **Import Errors**: Ensure the project root is in your Python path
2. **Database Errors**: Check database configuration and file permissions
3. **API Errors**: Verify OpenAI API key and quota
4. **Function Call Limits**: Adjust `max_function_calls` in configuration

## License

This implementation follows the same license as the parent project.
