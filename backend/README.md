# 🚀 DeepWiki Backend API

This is the backend API for DeepWiki, providing smart code analysis and AI-powered documentation generation with a modular, scalable architecture.

## ✨ Features

- **Modular Architecture**: Clean separation of concerns with domain-specific routers
- **Streaming AI Responses**: Real-time responses using multiple AI providers
- **Smart Code Analysis**: Automatically analyzes GitHub repositories
- **RAG Implementation**: Retrieval Augmented Generation for context-aware responses
- **Local Storage**: All data stored locally - no cloud dependencies
- **Conversation History**: Maintains context across multiple questions
- **Multi-Provider Support**: Google Gemini, OpenAI, OpenRouter, Azure OpenAI, and Ollama

## 🏗️ Architecture Overview

The backend follows a modular architecture pattern:

```
backend/
├── main.py              # Application entry point
├── app.py               # FastAPI application configuration
├── api/                 # API layer
│   └── v1/             # Version 1 API endpoints
│       ├── chat.py      # Chat and conversation endpoints
│       ├── config.py    # Configuration management
│       ├── core.py      # Core API functionality
│       ├── projects.py  # Project management
│       └── wiki.py      # Wiki generation
├── components/          # Core system components
│   ├── embedder/        # Vector embeddings and storage
│   ├── generator/       # AI text generation
│   ├── memory/          # Context and memory management
│   ├── processors/      # Data processing pipelines
│   └── retriever/       # RAG retrieval system
├── services/            # Business logic layer
├── models/              # Data models and schemas
├── data/                # Data storage and database
└── utils/               # Utility functions
```

## 🔧 Quick Setup

### Step 1: Install Dependencies

```bash
# From the project root
pip install -r backend/requirements.txt
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the project root:

```
# Required API Keys
GOOGLE_API_KEY=your_google_api_key        # Required for Google Gemini models
OPENAI_API_KEY=your_openai_api_key        # Required for embeddings and OpenAI models

# Optional API Keys
OPENROUTER_API_KEY=your_openrouter_api_key  # Required only if using OpenRouter models
AZURE_OPENAI_API_KEY=your_azure_openai_api_key      # Required for Azure OpenAI models
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint    # Required for Azure OpenAI models
AZURE_OPENAI_VERSION=your_azure_openai_version      # Required for Azure OpenAI models

# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id      # Required for AWS Bedrock models
AWS_SECRET_ACCESS_KEY=your_aws_secret_key     # Required for AWS Bedrock models
AWS_REGION=us-east-1                          # Optional, defaults to us-east-1
AWS_ROLE_ARN=your_aws_role_arn                # Optional, for role-based authentication

# OpenAI API Configuration
OPENAI_BASE_URL=https://custom-api-endpoint.com/v1  # Optional, for custom OpenAI API endpoints

# Ollama host
OLLAMA_HOST=https://your_ollama_host"  # Optional: Add Ollama host if not local. default: http://localhost:11434

# Server Configuration
PORT=8001  # Optional, defaults to 8001
HOST=0.0.0.0  # Optional, defaults to 0.0.0.0
RELOAD=false  # Optional, enable auto-reload for development
```

If you're not using Ollama mode, you need to configure an OpenAI API key for embeddings. Other API keys are only required when configuring and using models from the corresponding providers.

> 💡 **Where to get these keys:**
> - Get a Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
> - Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
> - Get an OpenRouter API key from [OpenRouter](https://openrouter.ai/keys)
> - Get AWS credentials from [AWS IAM Console](https://console.aws.amazon.com/iam/)

#### Advanced Environment Configuration

##### Provider-Based Model Selection
DeepWiki supports multiple LLM providers. The environment variables above are required depending on which providers you want to use:

- **Google Gemini**: Requires `GOOGLE_API_KEY`
- **OpenAI**: Requires `OPENAI_API_KEY`
- **OpenRouter**: Requires `OPENROUTER_API_KEY`
- **Azure OpenAI**: Requires `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, and `AZURE_OPENAI_VERSION`
- **AWS Bedrock**: Requires `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- **Ollama**: No API key required (runs locally)

##### Custom OpenAI API Endpoints
The `OPENAI_BASE_URL` variable allows you to specify a custom endpoint for the OpenAI API. This is useful for:

- Enterprise users with private API channels
- Organizations using self-hosted or custom-deployed LLM services
- Integration with third-party OpenAI API-compatible services

**Example:** you can use the endpoint which support the OpenAI protocol provided by any organization
```
OPENAI_BASE_URL=https://custom-openai-endpoint.com/v1
```

##### Configuration Files
DeepWiki now uses JSON configuration files to manage various system components instead of hardcoded values:

1. **`generator.json`**: Configuration for text generation models
   - Located in `backend/config/` by default
   - Defines available model providers (Google, OpenAI, OpenRouter, Azure OpenAI, AWS Bedrock, Ollama)
   - Specifies default and available models for each provider
   - Contains model-specific parameters like temperature and top_p

2. **`embedder.json`**: Configuration for embedding models and text processing
   - Located in `backend/config/` by default
   - Defines embedding models for vector storage
   - Contains retriever configuration for RAG
   - Specifies text splitter settings for document chunking

3. **`repo.json`**: Configuration for repository handling
   - Located in `backend/config/` by default
   - Contains file filters to exclude certain files and directories
   - Defines repository size limits and processing rules

You can customize the configuration directory location using the environment variable:

```
DEEPWIKI_CONFIG_DIR=/path/to/custom/config/dir  # Optional, for custom config file location
```

This allows you to maintain different configurations for various environments or deployment scenarios without modifying the code.

### Step 3: Start the API Server

```bash
# From the project root
python -m backend.main

# Or with custom port/host
python -m backend.main --port 8002 --host 127.0.0.1

# Or with auto-reload for development
RELOAD=true python -m backend.main
```

The API will be available at `http://localhost:8001` (or your custom port)

## 🧠 How It Works

### 1. Repository Indexing
When you provide a GitHub repository URL, the API:
- Clones the repository locally (if not already cloned)
- Reads all files in the repository
- Creates embeddings for the files using OpenAI
- Stores the embeddings in a local database

### 2. Smart Retrieval (RAG)
When you ask a question:
- The API finds the most relevant code snippets
- These snippets are used as context for the AI
- The AI generates a response based on this context

### 3. Real-Time Streaming
- Responses are streamed in real-time
- You see the answer as it's being generated
- This creates a more interactive experience

## 📡 API Endpoints

### Core Endpoints

#### GET /
Returns basic API information and available endpoints.

#### GET /health
Health check endpoint for monitoring.

#### GET /docs
Interactive API documentation (Swagger UI).

#### GET /redoc
Alternative API documentation (ReDoc).

### Chat Endpoints

#### POST /api/v1/chat/completions/stream
Streams an AI-generated response about a GitHub repository.

**Request Body:**

```json
{
  "repo_url": "https://github.com/username/repo",
  "messages": [
    {
      "role": "user",
      "content": "What does this repository do?"
    }
  ],
  "filePath": "optional/path/to/file.py"  // Optional
}
```

**Response:**
A streaming response with the generated text.

### Wiki Endpoints

#### POST /api/v1/wiki/generate
Generates a complete wiki for a repository.

#### GET /api/v1/wiki/status/{task_id}
Checks the status of a wiki generation task.

### Project Endpoints

#### GET /api/v1/projects
Lists all processed projects.

#### DELETE /api/v1/projects/{project_id}
Deletes a project and its associated data.

### Configuration Endpoints

#### GET /api/v1/config
Retrieves current configuration.

#### PUT /api/v1/config
Updates configuration settings.

## 📝 Example Code

```python
import requests

# API endpoint
url = "http://localhost:8001/api/v1/chat/completions/stream"

# Request data
payload = {
    "repo_url": "https://github.com/AsyncFuncAI/deepwiki-open",
    "messages": [
        {
            "role": "user",
            "content": "Explain how React components work"
        }
    ]
}

# Make streaming request
response = requests.post(url, json=payload, stream=True)

# Process the streaming response
for chunk in response.iter_content(chunk_size=None):
    if chunk:
        print(chunk.decode('utf-8'), end='', flush=True)
```

## 💾 Storage

All data is stored locally on your machine:
- Cloned repositories: `~/.adalflow/repos/`
- Embeddings and indexes: `~/.adalflow/databases/`
- Generated wiki cache: `~/.adalflow/wikicache/`

No cloud storage is used - everything runs on your computer!

## 🔧 Development

### Running in Development Mode

```bash
# Enable auto-reload
RELOAD=true python -m backend.main

# Or use the environment variable
export RELOAD=true
python -m backend.main
```

### Project Structure

The backend follows a clean architecture pattern:

- **`main.py`**: Application entry point and server configuration
- **`app.py`**: FastAPI application setup and middleware configuration
- **`api/v1/`**: Versioned API endpoints organized by domain
- **`components/`**: Core system components (embedder, generator, retriever, etc.)
- **`services/`**: Business logic layer
- **`models/`**: Data models and Pydantic schemas
- **`utils/`**: Utility functions and helpers

### Adding New Endpoints

1. Create a new router in `api/v1/`
2. Define your endpoints using FastAPI decorators
3. Include the router in `app.py`
4. Add appropriate tests

### Configuration Management

Configuration is managed through:
- Environment variables for sensitive data
- JSON configuration files for system settings
- Runtime configuration updates via API endpoints

## 🧪 Testing

Run the test suite:

```bash
# From the project root
python -m pytest test/

# Or with coverage
python -m pytest test/ --cov=backend
```

## 📚 Additional Resources

- [Main README](../README.md) - Complete project overview
- [Frontend Documentation](../src/README.md) - Frontend setup and usage
- [Configuration Guide](../docs/) - Detailed configuration options
- [API Documentation](http://localhost:8001/docs) - Interactive API docs when running
