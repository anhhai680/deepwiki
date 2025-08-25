# System Patterns - DeepWiki Project

## Architecture Patterns

### 1. Multi-Provider AI Integration Pattern
**Pattern**: Provider-based model selection system with unified interface
**Implementation**: 
- Abstract base classes for different AI providers
- Factory pattern for LLM creation
- Configuration-driven model selection
- Seamless switching between providers

**Files**: `api/config/generator.json`, `api/config/embedder.json`
**Example**: Google Gemini, OpenAI, OpenRouter, Azure OpenAI, Ollama support

### 2. RAG (Retrieval Augmented Generation) Pattern
**Pattern**: Vector-based code retrieval with AI generation
**Implementation**:
- FAISS vector database for code embeddings
- OpenAI embeddings for text processing
- Context-aware AI responses
- Streaming chat completions

**Files**: `api/rag.py`, `api/tools/embedder.py`
**Benefits**: Accurate, context-aware responses based on actual code

### 3. Real-Time Communication Pattern
**Pattern**: WebSocket-based streaming for AI responses
**Implementation**:
- WebSocket connections for chat
- Streaming response handling
- Real-time diagram updates
- Async processing with FastAPI

**Files**: `api/websocket_wiki.py`, `src/utils/websocketClient.ts`

### 4. Configuration Management Pattern
**Pattern**: JSON-based configuration with environment variable substitution
**Implementation**:
- Centralized config directory (`api/config/`)
- Environment variable placeholders
- Provider-specific configurations
- Runtime configuration updates

**Files**: `api/config.py`, various `.json` config files

### 5. Multi-Language Support Pattern
**Pattern**: Internationalization with context-based language switching
**Implementation**:
- Next.js internationalization
- Language context provider
- Message file organization
- Dynamic language switching

**Files**: `src/contexts/LanguageContext.tsx`, `src/messages/`, `src/i18n.ts`

## Frontend Patterns

### 1. Component Composition Pattern
**Pattern**: Modular React components with clear separation of concerns
**Implementation**:
- Specialized components for specific features
- Configuration modals for settings
- Theme toggle and language selection
- Reusable UI components

**Files**: `src/components/`, component hierarchy

### 2. State Management Pattern
**Pattern**: React hooks and context for state management
**Implementation**:
- Custom hooks for data fetching
- Context providers for global state
- Local state for component-specific data
- Persistent storage with localStorage

**Files**: `src/hooks/`, `src/contexts/`

### 3. Real-Time UI Updates Pattern
**Pattern**: WebSocket-driven UI updates with optimistic rendering
**Implementation**:
- Real-time chat interface
- Live diagram updates
- Progress indicators
- Error handling and retry logic

## Backend Patterns

### 1. FastAPI Service Pattern
**Pattern**: RESTful API with async support and automatic documentation
**Implementation**:
- FastAPI application structure
- Pydantic models for validation
- Async endpoint handlers
- Automatic OpenAPI documentation

**Files**: `api/api.py`, `api/main.py`

### 2. Client Factory Pattern
**Pattern**: Factory pattern for different AI service clients
**Implementation**:
- Base client interfaces
- Provider-specific implementations
- Configuration-driven client creation
- Error handling and fallbacks

**Files**: `api/*_client.py` files

### 3. Data Pipeline Pattern
**Pattern**: Structured data processing with clear stages
**Implementation**:
- Repository cloning and analysis
- Code structure extraction
- Embedding generation
- Wiki content creation

**Files**: `api/data_pipeline.py`

## Security Patterns

### 1. Token-Based Authentication Pattern
**Pattern**: Personal access tokens for private repository access
**Implementation**:
- Secure token storage
- Repository access validation
- Permission checking
- Token refresh handling

### 2. Environment Variable Security Pattern
**Pattern**: Secure API key management through environment variables
**Implementation**:
- `.env` file for local development
- Docker environment variable injection
- Secure credential handling
- API key validation

## Performance Patterns

### 1. Caching Strategy Pattern
**Pattern**: Multi-level caching for improved performance
**Implementation**:
- Repository data caching
- Generated content caching
- Embedding vector caching
- Browser localStorage caching

### 2. Async Processing Pattern
**Pattern**: Non-blocking operations for better user experience
**Implementation**:
- Async API endpoints
- Background task processing
- Streaming responses
- Progress tracking

## Error Handling Patterns

### 1. Graceful Degradation Pattern
**Pattern**: Fallback mechanisms when services are unavailable
**Implementation**:
- Provider fallback logic
- Error message localization
- User-friendly error display
- Retry mechanisms

### 2. Validation Pattern
**Pattern**: Input validation and sanitization
**Implementation**:
- Pydantic model validation
- Frontend form validation
- API endpoint validation
- Error response standardization

## Development Patterns

### 1. Docker Containerization Pattern
**Pattern**: Consistent development and deployment environments
**Implementation**:
- Multi-stage Docker builds
- Docker Compose for local development
- Volume mounting for data persistence
- Environment variable injection

**Files**: `Dockerfile`, `docker-compose.yml`

### 2. Configuration-Driven Development Pattern
**Pattern**: Runtime configuration without code changes
**Implementation**:
- JSON configuration files
- Environment variable substitution
- Dynamic model selection
- Provider configuration updates

## Pattern Benefits

### 1. Maintainability
- Clear separation of concerns
- Consistent implementation approaches
- Easy to understand and modify

### 2. Scalability
- Provider-agnostic architecture
- Modular component design
- Efficient resource utilization

### 3. Flexibility
- Easy to add new AI providers
- Configurable behavior
- Runtime customization

### 4. Reliability
- Comprehensive error handling
- Fallback mechanisms
- Robust validation

## Pattern Evolution

These patterns have evolved based on:
- **User Requirements**: Multi-provider support, real-time features
- **Technical Constraints**: Performance, security, scalability
- **Best Practices**: Modern web development standards
- **AI Integration**: RAG, streaming, multi-model support

## Future Pattern Considerations

- **Microservices**: Potential service decomposition
- **Event-Driven**: Enhanced real-time capabilities
- **Plugin System**: Extensible architecture
- **Advanced Caching**: Redis, CDN integration
