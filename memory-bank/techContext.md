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
- **LLM Providers**: Multiple (Google, OpenAI, OpenRouter, Azure, Ollama)
- **Text Processing**: Tiktoken, LangID
- **RAG Framework**: Custom implementation

### Infrastructure and Deployment
- **Containerization**: Docker + Docker Compose
- **Process Management**: Uvicorn (ASGI server)
- **Environment Management**: python-dotenv
- **Logging**: Python logging module
- **File Storage**: Local filesystem with volume mounting

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
LOG_FILE_PATH=api/logs/application.log

# Authorization
DEEPWIKI_AUTH_MODE=false
DEEPWIKI_AUTH_CODE=your_auth_code
```

### Configuration Files
- **`api/config/generator.json`**: LLM model configurations
- **`api/config/embedder.json`**: Embedding and retrieval settings
- **`api/config/repo.json`**: Repository processing rules
- **`api/config/lang.json`**: Language-specific configurations

## Development Environment

### Local Development Setup
```bash
# Backend
cd api/
pip install -r requirements.txt
python -m api.main

# Frontend
npm install
npm run dev
```

### Docker Development
```bash
# Full stack
docker-compose up

# Backend only
docker run -p 8001:8001 -e GOOGLE_API_KEY=... deepwiki-open
```

### Data Persistence
- **Repository Storage**: `~/.adalflow/repos/`
- **Vector Database**: `~/.adalflow/databases/`
- **Wiki Cache**: `~/.adalflow/wikicache/`
- **Logs**: `api/logs/` (configurable)

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
