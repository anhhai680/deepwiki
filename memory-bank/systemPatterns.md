# System Patterns - DeepWiki Project

## Architecture Patterns

### 1. Multi-Provider AI Integration Pattern
**Pattern**: Provider-based model selection system with unified interface
**Implementation**: 
- Abstract base classes for different AI providers
- Factory pattern for LLM creation
- Configuration-driven model selection
- Seamless switching between providers

**Files**: `backend/config/generator.json`, `backend/config/embedder.json`
**Example**: Google Gemini, OpenAI, OpenRouter, Azure OpenAI, Ollama support

### 2. RAG (Retrieval Augmented Generation) Pattern
**Pattern**: Vector-based code retrieval with AI generation
**Implementation**:
- FAISS vector database for code embeddings
- OpenAI embeddings for text processing
- Context-aware AI responses
- Streaming chat completions

**Files**: `backend/pipelines/rag/`, `backend/components/retriever/`
**Benefits**: Accurate, context-aware responses based on actual code

### 3. Real-Time Communication Pattern
**Pattern**: WebSocket-based streaming for AI responses
**Implementation**:
- WebSocket connections for chat
- Streaming response handling
- Real-time diagram updates
- Async processing with FastAPI

**Files**: `backend/websocket/wiki_handler.py`

### 4. Configuration Management Pattern
**Pattern**: JSON-based configuration with environment variable substitution
**Implementation**:
- Centralized config directory (`backend/config/`)
- Environment variable placeholders
- Provider-specific configurations
- Runtime configuration updates

**Files**: `backend/core/config/`, various `.json` config files

### 5. Multi-Language Support Pattern
**Pattern**: Internationalization with context-based language switching
**Implementation**:
- Next.js internationalization
- Language context provider
- Message file organization
- Dynamic language switching

**Files**: `src/contexts/LanguageContext.tsx`, `src/messages/`, `src/i18n.ts`

## New Architecture Patterns (Post-Restructure)

### 6. Modular Component Architecture Pattern
**Pattern**: Clean separation of concerns with specialized component modules
**Implementation**:
- Dedicated directories for each component type
- Clear interfaces between components
- Dependency injection through container system
- Consistent module organization

**Files**: `backend/components/`, organized by functionality
**Benefits**: Improved maintainability, testability, and scalability

### 7. Pipeline Architecture Pattern
**Pattern**: Step-based processing with clear data flow
**Implementation**:
- Base pipeline classes with common functionality
- Specialized pipeline implementations (RAG, Chat)
- Modular step components for each processing stage
- Clear data transformation between steps

**Files**: `backend/pipelines/`, `backend/pipelines/rag/steps/`, `backend/pipelines/chat/steps/`
**Benefits**: Clear processing flow, easy to modify and extend

### 8. Service Layer Pattern
**Pattern**: Business logic separation with service orchestration
**Implementation**:
- Service classes for major business domains
- Clear separation between API and business logic
- Dependency injection for service composition
- Consistent error handling and response patterns

**Files**: `backend/services/`, `backend/container.py`
**Benefits**: Clean separation of concerns, improved testability

### 9. Data Layer Pattern
**Pattern**: Specialized data processing and storage components
**Implementation**:
- Dedicated processors for different data types
- Vector operations management for embeddings
- Repository pattern for data access
- Clear separation of data concerns

**Files**: `backend/data/`, `backend/components/processors/`
**Benefits**: Organized data handling, improved performance

### 10. Utilities Organization Pattern
**Pattern**: Comprehensive utility package with logical module organization
**Implementation**:
- 6 specialized utility modules (text, file, validation, token, config, response)
- 83 utility functions organized by functionality
- Consistent error handling and type safety
- Backward compatibility maintenance

**Files**: `backend/utils/`, organized utility modules
**Benefits**: Centralized utility access, improved code reuse

## Frontend Patterns

### 1. Component Composition Pattern
**Pattern**: Modular React components with clear separation of concerns
**Implementation**:
- Specialized components for specific features
- Configuration modals for settings
- Theme toggle and language selection
- Reusable UI components
- Two-column layout architecture for improved space utilization

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

### 4. Layout Architecture Pattern
**Pattern**: Responsive two-column layout design for optimal space utilization
**Implementation**:
- Dedicated panels for different functionality (ExistingProjectsPanel, ChatPanel)
- Mobile-responsive design with tab-based navigation
- Flexible component arrangement for different screen sizes
- Seamless Ask component integration within home page layout

**Files**: `src/app/page.tsx`, `src/components/ChatPanel.tsx`, `src/components/ExistingProjectsPanel.tsx`
**Benefits**: Better space utilization, improved user experience, cleaner component separation

## Backend Patterns

### 1. FastAPI Service Pattern
**Pattern**: RESTful API with async support and automatic documentation
**Implementation**:
- FastAPI application structure
- Pydantic models for validation
- Async endpoint handlers
- Automatic OpenAPI documentation

**Files**: `backend/api/`, `backend/main.py`

### 2. Client Factory Pattern
**Pattern**: Factory pattern for different AI service clients
**Implementation**:
- Base client interfaces
- Provider-specific implementations
- Configuration-driven client creation
- Error handling and fallbacks

**Files**: `backend/components/generator/providers/`

### 3. Data Pipeline Pattern
**Pattern**: Structured data processing with clear stages
**Implementation**:
- Repository cloning and analysis
- Code structure extraction
- Embedding generation
- Wiki content creation

**Files**: `backend/pipelines/`

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

## Testing Patterns

### 1. Component Testing Pattern
**Pattern**: Individual component testing with comprehensive coverage
**Implementation**:
- Dedicated test files for each component
- Mock dependencies for isolation
- Comprehensive test scenarios
- Performance and integration testing

**Files**: `backend/tests/`, organized by component type

### 2. Import Validation Pattern
**Pattern**: Automated import validation to prevent import errors
**Implementation**:
- AST-based import analysis
- Module resolution validation
- Circular import detection
- Automated validation scripts

**Files**: `tools/validate_imports.py`

## Pattern Benefits

### 1. Maintainability
- Clear separation of concerns
- Consistent implementation approaches
- Easy to understand and modify
- Modular architecture for focused changes

### 2. Scalability
- Provider-agnostic architecture
- Modular component design
- Efficient resource utilization
- Clear interfaces for extension

### 3. Flexibility
- Easy to add new AI providers
- Configurable behavior
- Runtime customization
- Pluggable component architecture

### 4. Reliability
- Comprehensive error handling
- Fallback mechanisms
- Robust validation
- Comprehensive testing coverage

## Pattern Evolution

These patterns have evolved based on:
- **User Requirements**: Multi-provider support, real-time features
- **Technical Constraints**: Performance, security, scalability
- **Best Practices**: Modern web development standards
- **AI Integration**: RAG, streaming, multi-model support
- **Architecture Restructure**: Modular design, clean separation of concerns
- **Testing Requirements**: Comprehensive testing infrastructure
- **Performance Optimization**: Better component organization and caching
- **User Experience**: Improved layout design and component integration
- **Mobile Responsiveness**: Better support for different screen sizes

## Future Pattern Considerations

- **Microservices**: Potential service decomposition
- **Event-Driven**: Enhanced real-time capabilities
- **Plugin System**: Extensible architecture
- **Advanced Caching**: Redis, CDN integration
- **API Versioning**: Structured API evolution
- **Monitoring**: Enhanced observability patterns
- **Security**: Advanced authentication and authorization patterns
- **Progressive Web App**: Enhanced mobile experience
- **Accessibility**: Improved accessibility patterns
- **Internationalization**: Enhanced multi-language support

## Post-Restructure Architecture Benefits

### 1. **Component Organization**
- Clear separation of concerns
- Logical module grouping
- Consistent naming conventions
- Easy navigation and understanding

### 2. **Dependency Management**
- Clean dependency injection
- Reduced circular dependencies
- Clear import hierarchies
- Better module isolation

### 3. **Testing Infrastructure**
- Comprehensive test coverage
- Isolated component testing
- Performance validation
- Quality assurance framework

### 4. **Performance Optimization**
- Better resource utilization
- Improved caching strategies
- Optimized import resolution
- Enhanced scalability

The restructure has successfully established a clean, maintainable architecture that preserves all original functionality while providing significant improvements in code organization, testability, and scalability.
