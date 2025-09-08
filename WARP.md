# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Backend (Python FastAPI)
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Start backend development server (port 8001)
python -m backend.main
# or use the convenience script
./run.sh

# Run with auto-reload for development
RELOAD=true python -m backend.main

# Run Python tests
./run-tests.sh
# or manually
python -m pytest test/
```

### Frontend (Next.js TypeScript)
```bash
# Install dependencies
npm install

# Start frontend development server (port 3000)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint
```

### Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up --build

# Build Docker image manually
docker build -t deepwiki .
```

### Testing
```bash
# Run all Python tests
python -m pytest test/

# Run tests with coverage
python -m pytest test/ --cov=backend

# Run specific test file
python -m pytest test/test_specific.py

# Validate imports
python backend/tools/validate_imports.py
```

## Architecture Overview

### High-Level Structure
DeepWiki is a full-stack AI-powered application that automatically generates interactive wikis from GitHub/GitLab/BitBucket repositories using a modern, modular architecture.

**Tech Stack:**
- Backend: Python 3.11+, FastAPI, uvicorn
- Frontend: Next.js 15.3.1, React 19, TypeScript, Tailwind CSS  
- AI: Multiple providers (Google Gemini, OpenAI, Azure OpenAI, OpenRouter, Ollama)
- Vector DB: FAISS for embeddings
- Data: RAG (Retrieval Augmented Generation) pipeline

### Backend Architecture (Modular Component-Based)

The backend follows a clean, modular architecture with clear separation of concerns:

```
backend/
├── main.py                   # Entry point (port 8001)
├── app.py                    # FastAPI app configuration  
├── container.py              # Dependency injection container
├── api/v1/                   # Versioned API endpoints
├── components/               # Core RAG pipeline components
│   ├── embedder/            # Vector embeddings and storage
│   ├── generator/           # AI text generation (multi-provider)
│   ├── retriever/           # RAG retrieval system
│   ├── memory/              # Context and conversation management
│   └── processors/          # Data processing pipelines
├── pipelines/               # Orchestration layer
│   ├── base/               # Pipeline framework
│   ├── rag/                # RAG pipeline implementation
│   └── chat/               # Chat pipeline implementation
├── services/                # Business logic layer
├── data/                    # Vector operations & database
└── utils/                   # 83 utility functions in 6 modules
```

### Key Architectural Patterns

**1. Provider-Based AI Integration**
- Abstract interfaces for different AI providers
- Factory pattern for LLM creation
- Configuration-driven model selection via JSON files
- Seamless switching between Google Gemini, OpenAI, Azure, OpenRouter, Ollama

**2. RAG Pipeline Architecture**  
- Component-based RAG system with FAISS vector storage
- Step-based processing with context management
- Retrieval → Generation → Response streaming
- Context-aware responses based on actual repository code

**3. Pipeline Framework**
- Base pipeline classes with step-based execution
- Sequential and parallel pipeline support
- Context propagation between steps
- Error handling and validation at each step

**4. Service Layer Pattern**
- Business logic separation with dependency injection
- Chat service for conversation management
- Project service for repository indexing
- Clean separation between API and business logic

**5. Configuration Management**
- JSON-based configuration with environment variable substitution
- Provider-specific configurations in `backend/config/`
- Runtime configuration updates via API endpoints

### Frontend Architecture

**Component-Based Next.js Structure:**
```
src/
├── app/                     # Next.js app router
├── components/              # React components
│   ├── Ask.tsx             # RAG-powered Q&A interface
│   ├── ChatPanel.tsx       # Two-column layout chat panel
│   ├── ExistingProjectsPanel.tsx # Repository selection
│   └── Mermaid.tsx         # Diagram rendering with preprocessing
├── contexts/               # React contexts (Language, Theme)
└── types/                  # TypeScript definitions
```

**Key Frontend Patterns:**
- Two-column responsive layout for optimal space utilization
- Real-time WebSocket communication for streaming responses
- Interactive repository selection with dual-click behavior (300ms timeout detection)
- Robust Mermaid diagram preprocessing with error recovery
- Multi-repository support with platform detection (GitHub/GitLab/BitBucket)

### Data Flow & Communication

**Repository Processing:**
1. Repository URL input → Clone/analyze code structure
2. Create embeddings using OpenAI API → Store in FAISS vector DB
3. Generate documentation with selected AI provider
4. Create visual Mermaid diagrams → Organize as interactive wiki

**Real-Time Communication:**
- WebSocket connections for streaming AI responses
- Chat completions with conversation context
- Real-time diagram updates and progress indicators

## Environment Configuration

### Required Environment Variables
Create `.env` file in project root:
```bash
# Required for embeddings (even if not using OpenAI models)
OPENAI_API_KEY=your_openai_api_key

# Optional - provider-specific API keys
GOOGLE_API_KEY=your_google_api_key
OPENROUTER_API_KEY=your_openrouter_api_key  
AZURE_OPENAI_API_KEY=your_azure_api_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_VERSION=your_azure_version
OLLAMA_HOST=http://localhost:11434

# Optional configuration
PORT=8001
SERVER_BASE_URL=http://localhost:8001
LOG_LEVEL=INFO
DEEPWIKI_CONFIG_DIR=/custom/config/path
```

### Configuration Files
Located in `backend/config/` (customizable via `DEEPWIKI_CONFIG_DIR`):
- `generator.json` - AI model provider configurations
- `embedder.json` - Vector embedding and retrieval settings  
- `repo.json` - Repository processing filters and limits
- `lang.json` - Language and localization settings

## Development Guidelines

### Component Development
- Follow existing modular architecture patterns
- Use dependency injection via `container.py`
- Implement proper error handling and logging
- Write tests for new components in `test/` directory

### API Development  
- Add new endpoints to `api/v1/` with proper versioning
- Follow FastAPI patterns with Pydantic models
- Include OpenAPI documentation
- Maintain backward compatibility

### Pipeline Extensions
- Extend base pipeline classes for new workflows
- Implement step-based processing with context
- Add proper validation and error recovery
- Use the existing component interfaces

### Configuration Changes
- Update JSON config files rather than hardcoding values
- Support environment variable substitution
- Maintain configuration validation
- Document configuration options

### Testing Requirements
- Write unit tests for new components
- Add integration tests for pipelines  
- Test API endpoints with proper mocks
- Validate configuration changes

## Key Integration Points

### Multi-Provider AI Support
The system abstracts AI provider differences through:
- `components/generator/providers/` - Provider-specific implementations
- `components/generator/generator_manager.py` - Provider orchestration
- Configuration-driven provider selection

### RAG System Components
- `components/retriever/faiss_retriever.py` - Vector similarity search
- `components/embedder/embedder_manager.py` - Text embedding creation
- `pipelines/rag/` - End-to-end RAG workflow orchestration

### WebSocket Communication
- `websocket/wiki_handler.py` - Real-time wiki generation updates
- Streaming responses for chat completions
- Progress updates during repository processing

### Data Persistence
- Local storage in `~/.adalflow/` directory
- Vector embeddings in FAISS indices
- Repository clones and metadata caching
- Wiki content caching for performance

This architecture supports rapid development while maintaining clean separation of concerns, testability, and extensibility for future AI provider integrations and feature additions.
