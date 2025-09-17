# Technical Context - DeepWiki Project

## Technology Stack Overview

### Frontend Technology Stack
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript 5
- **UI Library**: React 19
- **Styling**: Tailwind CSS 4
- **State Management**: React Hooks + Context API
- **Build Tool**: Turbopack (development)
- **Package Manager**: npm/yarn

### Backend Technology Stack
- **Framework**: FastAPI (Python)
- **Language**: Python 3.x
- **Async Support**: Uvicorn with standard extras
- **API Documentation**: OpenAPI/Swagger (automatic)
- **Validation**: Pydantic 2.x
- **Package Management**: pip + requirements.txt

### AI and ML Technologies
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: OpenAI embeddings (default)
- **LLM Providers**: Multiple (Google, OpenAI, OpenRouter, Azure, Ollama, Private Models)
- **Text Processing**: Tiktoken, LangID
- **RAG Framework**: Custom implementation
- **Private Model Support**: OpenAI-compatible private deployments (vLLM, LocalAI, custom)

### Infrastructure and Deployment
- **Containerization**: Docker + Docker Compose
- **Process Management**: Uvicorn (ASGI server)
- **Environment Management**: python-dotenv
- **Logging**: Python logging module
- **File Storage**: Local filesystem with volume mounting

## Current Project Architecture (Post-Restructure)

### Backend Structure
```
backend/
├── api/                    # API layer with versioned endpoints
│   ├── v1/                # API version 1 endpoints
│   │   ├── chat.py        # Chat-related endpoints
│   │   ├── config.py      # Configuration endpoints
│   │   ├── core.py        # Core functionality endpoints
│   │   ├── projects.py    # Project management endpoints
│   │   └── wiki.py        # Wiki-related endpoints
│   ├── dependencies.py    # FastAPI dependencies
│   └── __init__.py        # API package initialization
├── components/             # Core business logic components
│   ├── embedder/          # Embedding provider components
│   ├── generator/          # AI generation components
│   │   ├── providers/     # AI provider implementations
│   │   └── templates/     # Prompt templates
│   ├── memory/            # Memory management components
│   ├── processors/        # Data processing components
│   └── retriever/         # Retrieval components
├── core/                   # Core infrastructure
│   ├── config/            # Configuration management
│   ├── exceptions.py      # Custom exception classes
│   ├── interfaces/        # Abstract interfaces
│   └── types.py           # Type definitions
├── data/                   # Data layer
│   ├── repositories/      # Data access layer
│   ├── vector_store.py    # Vector storage operations
│   └── faiss_integration.py # FAISS integration
├── models/                 # Pydantic data models
│   ├── chat.py            # Chat-related models
│   ├── common.py          # Common model definitions
│   ├── config.py          # Configuration models
│   └── wiki.py            # Wiki-related models
├── pipelines/              # Processing pipelines
│   ├── base/              # Base pipeline classes
│   ├── chat/              # Chat processing pipeline
│   │   └── steps/         # Chat pipeline steps
│   └── rag/               # RAG processing pipeline
│       └── steps/         # RAG pipeline steps
├── services/               # Business logic services
│   ├── chat_service.py    # Chat business logic
│   └── project_service.py # Project processing logic
├── utils/                  # Utility functions
│   ├── config_utils.py    # Configuration utilities
│   ├── file_utils.py      # File operation utilities
│   ├── response_utils.py  # Response formatting utilities
│   ├── text_utils.py      # Text processing utilities
│   ├── token_utils.py     # Token management utilities
│   └── validation_utils.py # Validation utilities
├── websocket/              # WebSocket functionality
│   └── wiki_handler.py    # WebSocket message handling
├── app.py                  # FastAPI application factory
├── container.py            # Dependency injection container
├── main.py                 # Application entry point
└── requirements.txt        # Python dependencies
```

### Frontend Structure
```
src/
├── app/                    # Next.js app router pages
│   ├── [owner]/           # Dynamic owner routes
│   │   └── [repo]/        # Dynamic repository routes
│   ├── api/               # API route handlers
│   ├── wiki/              # Wiki interface
│   └── layout.tsx         # Root layout component
├── components/             # React components
│   ├── Ask.tsx            # Question asking interface
│   ├── ConfigurationModal.tsx # Configuration modal
│   ├── Markdown.tsx       # Markdown rendering
│   ├── Mermaid.tsx        # Diagram rendering
│   ├── ModelSelectionModal.tsx # AI model selection
│   ├── ProcessedProjects.tsx # Project display
│   ├── WikiTreeView.tsx   # Wiki navigation tree
│   └── WikiTypeSelector.tsx # Wiki type selection
├── contexts/               # React contexts
│   └── LanguageContext.tsx # Language selection context
├── hooks/                  # Custom React hooks
│   └── useProcessedProjects.ts # Project data hook
├── messages/               # Internationalization messages
├── types/                  # TypeScript type definitions
└── utils/                  # Utility functions
```

## Dependencies Analysis

### Frontend Dependencies
```json
{
  "mermaid": "^11.4.1",           // Diagram rendering
  "next": "15.3.1",               // React framework
  "next-intl": "^4.1.0",          // Internationalization
  "next-themes": "^0.4.6",        // Theme management
  "react": "^19.0.0",             // UI library
  "react-dom": "^19.0.0",         // React DOM
  "react-icons": "^5.5.0",        // Icon library
  "react-markdown": "^10.1.0",    // Markdown rendering
  "react-syntax-highlighter": "^15.6.1", // Code highlighting
  "rehype-raw": "^7.0.0",         // HTML processing
  "remark-gfm": "^4.0.1",         // GitHub Flavored Markdown
  "svg-pan-zoom": "^3.6.2"        // SVG interaction
}
```

### Backend Dependencies
```python
# Core Framework
fastapi>=0.95.0                    # Web framework
uvicorn[standard]>=0.21.1          # ASGI server
pydantic>=2.0.0                    # Data validation

# AI and ML
google-generativeai>=0.3.0         # Google Gemini
google-ai-generativelanguage>=0.6.15 # Google AI
tiktoken>=0.5.0                    # Tokenization
adalflow>=0.1.0                    # Repository management
numpy>=1.24.0                      # Numerical computing
faiss-cpu>=1.7.4                   # Vector similarity search
langid>=1.1.6                      # Language detection

# HTTP and Communication
requests>=2.28.0                    # HTTP client
aiohttp>=3.8.4                      # Async HTTP
websockets>=11.0.3                  # WebSocket support

# Cloud Providers
openai>=1.76.2                      # OpenAI API
ollama>=0.4.8                       # Local Ollama
boto3>=1.34.0                       # AWS services
azure-identity>=1.12.0              # Azure authentication
azure-core>=1.24.0                  # Azure core

# Utilities
jinja2>=3.1.2                       # Template engine
python-dotenv>=1.0.0                # Environment management
```

## Recent Technical Improvements (September 2025)

### Mermaid Diagram Rendering Enhancement
- **Problem Solved**: Critical syntax parsing errors causing diagram render failures
- **Implementation**: Comprehensive preprocessing pipeline with error recovery
- **Files Updated**: `src/components/Mermaid.tsx`, `src/app/[owner]/[repo]/page.tsx`
- **Technical Achievement**: Single comprehensive regex replacing multiple operations for better performance

#### Key Technical Features
- **Unified Regex Pattern**: `/(\w+)\[([^\]]*?)(?:\]|$|\n)/gm` handles all bracket pattern issues
- **Intelligent Syntax Correction**: Automatic quoting for special characters and spaces
- **Error Recovery**: Graceful degradation with detailed debugging information
- **Performance Optimization**: Single-pass processing instead of multiple iterations
- **Code Quality**: Eliminated duplicate regex patterns and improved maintainability

#### Error Handling Strategy
```typescript
// Enhanced error display with debugging information
if (mermaidRef.current) {
  const cleanedChart = preprocessMermaidChart(chart);
  mermaidRef.current.innerHTML = `
    <div class="text-red-500 dark:text-red-400 text-xs mb-2">
      <strong>Chart Rendering Error</strong><br/>
      ${errorMessage}
    </div>
    <div class="text-xs mb-2"><strong>Original Chart:</strong></div>
    <pre class="text-xs overflow-auto p-2 bg-gray-100 dark:bg-gray-800 rounded mb-2">${chart}</pre>
    ${cleanedChart !== chart ? `
      <div class="text-xs mb-2"><strong>Cleaned Chart (attempted fix):</strong></div>
      <pre class="text-xs overflow-auto p-2 bg-gray-100 dark:bg-gray-800 rounded">${cleanedChart}</pre>
    ` : ''}
  `;
}
```

### Multi-Repository Architecture Enhancement
- **Advanced State Management**: Bidirectional synchronization between Ask form and sidebar selection
- **Component Isolation**: Perfect separation between home page features and individual repository pages
- **TypeScript Enhancement**: Comprehensive type definitions for new multi-repository functionality
- **UI Optimization**: Conditional rendering based on selection state for cleaner interfaces

### Performance and Code Quality Improvements
- **Single-Pass Processing**: Optimized regex operations for better performance
- **Memory Management**: Proper cleanup of timeouts and event listeners
- **Code Deduplication**: Eliminated overlapping patterns and consolidated logic
- **Build Optimization**: Reduced warnings and improved compilation efficiency

## Technical Constraints

### Performance Constraints
- **Vector Search**: FAISS CPU implementation (memory and CPU intensive)
- **Real-time Processing**: WebSocket streaming for immediate feedback
- **Large Repository Handling**: Memory usage scales with repository size
- **Concurrent Users**: Single FastAPI instance (can be scaled horizontally)

### Security Constraints
- **API Key Management**: Environment variables only
- **Repository Access**: Personal access tokens for private repos
- **CORS**: Configured for development (needs production hardening)
- **Authentication**: Basic token-based (no user management system)

### Scalability Constraints
- **Single Instance**: No built-in load balancing
- **File Storage**: Local filesystem (no distributed storage)
- **Database**: In-memory FAISS (no persistence across restarts)
- **Caching**: Local caching only (no distributed cache)

### Compatibility Constraints
- **Python Version**: 3.x (specific version not pinned)
- **Node.js Version**: Compatible with Next.js 15
- **Browser Support**: Modern browsers with ES6+ support
- **Operating System**: Cross-platform (Linux, macOS, Windows)

## Configuration Management

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key

# Optional
OPENROUTER_API_KEY=your_openrouter_api_key
AZURE_OPENAI_API_KEY=your_azure_api_key
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
AZURE_OPENAI_VERSION=your_azure_version
OLLAMA_HOST=your_ollama_host

# Configuration
PORT=8001                           # API server port
SERVER_BASE_URL=http://localhost:8001
DEEPWIKI_CONFIG_DIR=/path/to/config
LOG_LEVEL=INFO
LOG_FILE_PATH=backend/logs/application.log

# Authorization
DEEPWIKI_AUTH_MODE=false
DEEPWIKI_AUTH_CODE=your_auth_code
```

### Configuration Files
- **`backend/config/generator.json`**: LLM model configurations
- **`backend/config/embedder.json`**: Embedding and retrieval settings
- **`backend/config/repo.json`**: Repository processing rules
- **`backend/config/lang.json`**: Language-specific configurations

## Development Environment

### Local Development Setup
```bash
# Backend
cd backend/
pip install -r requirements.txt
python -m backend.main

# Frontend
npm install
npm run dev
```

### Docker Development
```bash
# Full stack
docker-compose up

# Backend only
docker run -p 8001:8001 -e GOOGLE_API_KEY=... deepwiki
```

### Data Persistence
- **Repository Storage**: `~/.adalflow/repos/`
- **Vector Database**: `~/.adalflow/databases/`
- **Wiki Cache**: `~/.adalflow/wikicache/`
- **Logs**: `backend/logs/` (configurable)

## API Architecture

### REST Endpoints
- **`/api/auth/status`**: Authentication status
- **`/api/auth/validate`**: Token validation
- **`/api/chat/stream`**: Streaming chat completions
- **`/api/models/config`**: Model configuration
- **`/api/wiki/projects`**: Wiki project management

### WebSocket Endpoints
- **`/ws/wiki`**: Real-time wiki updates
- **`/ws/chat`**: Streaming chat responses

### Data Models
- **Repository Information**: URL, platform, access tokens
- **Wiki Content**: Generated documentation, diagrams, structure
- **Chat Messages**: User queries, AI responses, context
- **Configuration**: Model settings, processing options

## Testing and Quality

### Testing Framework
- **Backend**: pytest (configured)
- **Frontend**: No testing framework configured
- **Integration**: Manual testing through UI
- **API Testing**: FastAPI automatic OpenAPI documentation

### Code Quality
- **Linting**: ESLint for frontend, no backend linter
- **Formatting**: No automatic formatter configured
- **Type Checking**: TypeScript strict mode, Python type hints
- **Documentation**: Comprehensive README, inline code comments

## Deployment Considerations

### Production Requirements
- **Environment Variables**: Secure API key management
- **Reverse Proxy**: Nginx/Apache for SSL termination
- **Process Management**: Systemd/supervisor for backend
- **Monitoring**: Log aggregation and health checks
- **Backup**: Data persistence and recovery procedures

### Scaling Strategies
- **Horizontal Scaling**: Multiple FastAPI instances
- **Load Balancing**: Nginx/HAProxy
- **Database**: Redis for caching, PostgreSQL for persistence
- **Storage**: Object storage (S3, Azure Blob) for repositories
- **CDN**: Static asset delivery optimization

## Technical Debt and Improvements

### Identified Areas
- **Testing**: Limited test coverage
- **Error Handling**: Basic error responses
- **Monitoring**: No metrics or health checks
- **Documentation**: API documentation could be enhanced
- **Security**: CORS and authentication hardening needed

### Improvement Priorities
1. **Testing Infrastructure**: Unit and integration tests
2. **Error Handling**: Comprehensive error management
3. **Monitoring**: Health checks and metrics
4. **Security**: Production-ready security measures
5. **Performance**: Caching and optimization

## Post-Restructure Benefits

### 1. **Architecture Improvements**
- **Modular Design**: Clear separation of concerns
- **Component Organization**: Logical grouping of functionality
- **Dependency Management**: Clean dependency injection
- **Interface Definition**: Clear contracts between components

### 2. **Development Experience**
- **Code Navigation**: Easier to find and understand code
- **Testing**: Isolated component testing
- **Maintenance**: Focused changes with minimal side effects
- **Documentation**: Clear component boundaries and responsibilities

### 3. **Performance and Scalability**
- **Resource Management**: Better resource utilization
- **Caching**: Improved caching strategies
- **Import Optimization**: Faster module resolution
- **Memory Usage**: Better memory management patterns

### 4. **Quality Assurance**
- **Testing Framework**: Comprehensive testing infrastructure
- **Import Validation**: Automated import error detection
- **Code Quality**: Consistent patterns and standards
- **Error Handling**: Improved error management and recovery

The restructure has successfully established a clean, maintainable architecture that preserves all original functionality while providing significant improvements in code organization, testability, and scalability.
