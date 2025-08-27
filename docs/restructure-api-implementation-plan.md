# API Restructure Implementation Plan

## Overview

This document outlines the comprehensive plan for restructuring the `api/` folder to implement a clean, maintainable, and RAG-optimized architecture. The new structure follows modern Python project best practices and is inspired by successful RAG applications like the [knowledge-base-agent repository](https://github.com/anhhai680/knowledge-base-agent/tree/main/src).

## Current State Analysis

### Existing Structure Issues
- **Monolithic files**: `api.py` (634 lines), `rag.py` (445 lines), `simple_chat.py` (690 lines)
- **Mixed responsibilities**: Business logic, API endpoints, and external client management in single files
- **Poor separation of concerns**: RAG components, chat logic, and configuration mixed together
- **Difficult testing**: Large files make unit testing challenging
- **Maintenance overhead**: Changes require navigating large, complex files

### Current File Distribution
```
api/
├── api.py (634 lines) - FastAPI app + endpoints + models
├── rag.py (445 lines) - RAG logic + conversation management
├── simple_chat.py (690 lines) - Chat functionality
├── config.py (334 lines) - Configuration + client management
├── openai_client.py (630 lines) - OpenAI integration
├── azureai_client.py (488 lines) - Azure AI integration
├── bedrock_client.py (318 lines) - AWS Bedrock integration
├── dashscope_client.py (914 lines) - DashScope integration
├── openrouter_client.py (523 lines) - OpenRouter integration
├── ollama_patch.py (105 lines) - Ollama integration
├── data_pipeline.py (842 lines) - Data processing
├── websocket_wiki.py (770 lines) - WebSocket handling
├── prompts.py (192 lines) - Prompt templates
├── tools/embedder.py (20 lines) - Embedding utilities
└── config/ - JSON configuration files
```

## Target Architecture

### New RAG-Optimized Structure
```
api/
├── __init__.py
├── main.py                 # Entry point
├── app.py                  # FastAPI app configuration
├── core/                   # Core application components
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── logging.py         # Logging configuration
│   └── exceptions.py      # Custom exception classes
├── agents/                 # AI Agent layer
│   ├── __init__.py
│   ├── base.py            # Base agent interface
│   ├── chat_agent.py      # Chat conversation agent
│   ├── wiki_agent.py      # Wiki generation agent
│   └── rag_agent.py       # RAG processing agent
├── components/             # RAG pipeline components
│   ├── __init__.py
│   ├── retriever/         # Retrieval components
│   │   ├── __init__.py
│   │   ├── base.py        # Base retriever interface
│   │   ├── faiss_retriever.py
│   │   └── vector_store.py
│   ├── embedder/          # Embedding components
│   │   ├── __init__.py
│   │   ├── base.py        # Base embedder interface
│   │   ├── openai_embedder.py
│   │   ├── ollama_embedder.py
│   │   └── embedder_manager.py
│   ├── generator/         # Text generation components
│   │   ├── __init__.py
│   │   ├── base.py        # Base generator interface
│   │   ├── openai_generator.py
│   │   ├── azure_generator.py
│   │   ├── bedrock_generator.py
│   │   ├── dashscope_generator.py
│   │   ├── openrouter_generator.py
│   │   ├── ollama_generator.py
│   │   └── generator_manager.py
│   └── memory/            # Conversation memory
│       ├── __init__.py
│       ├── base.py        # Base memory interface
│       └── conversation_memory.py
├── pipelines/              # RAG pipeline orchestration
│   ├── __init__.py
│   ├── base_pipeline.py   # Base pipeline interface
│   ├── chat_pipeline.py   # Chat conversation pipeline
│   ├── wiki_pipeline.py   # Wiki generation pipeline
│   └── rag_pipeline.py    # RAG query pipeline
├── models/                 # Data models
│   ├── __init__.py
│   ├── chat.py            # Chat models
│   ├── wiki.py            # Wiki models
│   ├── rag.py             # RAG models
│   └── common.py          # Shared models
├── api/                    # API endpoints
│   ├── __init__.py
│   ├── v1/                # API versioning
│   │   ├── __init__.py
│   │   ├── chat.py        # Chat endpoints
│   │   ├── wiki.py        # Wiki endpoints
│   │   └── projects.py    # Project endpoints
│   └── dependencies.py    # Shared dependencies
├── services/               # Business logic services
│   ├── __init__.py
│   ├── chat_service.py    # Chat orchestration
│   ├── wiki_service.py    # Wiki generation
│   ├── project_service.py # Project management
│   └── cache_service.py   # Caching layer
├── data/                   # Data management
│   ├── __init__.py
│   ├── database.py        # Database management
│   ├── vector_store.py    # Vector database operations
│   └── repositories/      # Data access layer
│       ├── __init__.py
│       ├── wiki_repo.py   # Wiki data access
│       └── project_repo.py # Project data access
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── text_processing.py # Text preprocessing
│   ├── file_utils.py      # File operations
│   └── validation.py      # Data validation
├── config/                 # Configuration files
│   ├── embedder.json
│   ├── generator.json
│   ├── lang.json
│   └── repo.json
├── websocket/              # WebSocket handling
│   ├── __init__.py
│   └── wiki_handler.py    # Wiki WebSocket logic
└── tests/                  # Test files
    ├── __init__.py
    ├── test_agents.py
    ├── test_components.py
    ├── test_pipelines.py
    └── test_services.py
```

## Implementation Phases

### Phase 1: Foundation Setup (Week 1)

#### 1.1 Create New Directory Structure
- [ ] Create all new directories
- [ ] Set up `__init__.py` files
- [ ] Create placeholder files for new structure

#### 1.2 Core Infrastructure
- [ ] Implement `core/config.py` with Pydantic settings
- [ ] Implement `core/logging.py` with structured logging
- [ ] Implement `core/exceptions.py` with custom exception classes
- [ ] Create base interfaces and abstract classes

#### 1.3 Configuration Management
- [ ] Refactor configuration loading from `config.py`
- [ ] Implement environment variable management
- [ ] Create component-specific configuration classes

### Phase 2: Component Extraction (Week 2)

#### 2.1 Generator Components
- [ ] Extract generator logic from client files
- [ ] Implement `components/generator/base.py`
- [ ] Create individual generator implementations:
  - [ ] `openai_generator.py` from `openai_client.py`
  - [ ] `azure_generator.py` from `azureai_client.py`
  - [ ] `bedrock_generator.py` from `bedrock_client.py`
  - [ ] `dashscope_generator.py` from `dashscope_client.py`
  - [ ] `openrouter_generator.py` from `openrouter_client.py`
  - [ ] `ollama_generator.py` from `ollama_patch.py`
- [ ] Implement `components/generator/generator_manager.py`

#### 2.2 Embedder Components
- [ ] Extract embedder logic from `tools/embedder.py`
- [ ] Implement `components/embedder/base.py`
- [ ] Create `components/embedder/embedder_manager.py`
- [ ] Implement provider-specific embedders

#### 2.3 Retriever Components
- [ ] Extract retriever logic from `rag.py`
- [ ] Implement `components/retriever/base.py`
- [ ] Create `components/retriever/faiss_retriever.py`
- [ ] Implement `components/retriever/vector_store.py`

#### 2.4 Memory Components
- [ ] Extract conversation memory from `rag.py`
- [ ] Implement `components/memory/base.py`
- [ ] Create `components/memory/conversation_memory.py`

### Phase 3: Pipeline Implementation (Week 3)

#### 3.1 Base Pipeline
- [ ] Implement `pipelines/base_pipeline.py`
- [ ] Create pipeline interfaces and abstract methods
- [ ] Implement pipeline configuration management

#### 3.2 RAG Pipeline
- [ ] Implement `pipelines/rag_pipeline.py`
- [ ] Extract RAG logic from `rag.py`
- [ ] Implement query processing flow
- [ ] Add error handling and validation

#### 3.3 Chat Pipeline
- [ ] Implement `pipelines/chat_pipeline.py`
- [ ] Extract chat logic from `simple_chat.py`
- [ ] Implement conversation flow management
- [ ] Add streaming support

#### 3.4 Wiki Pipeline
- [ ] Implement `pipelines/wiki_pipeline.py`
- [ ] Extract wiki generation logic
- [ ] Implement document processing flow

### Phase 4: Agent Layer (Week 4)

#### 4.1 Base Agent
- [ ] Implement `agents/base.py`
- [ ] Create agent interfaces and abstract methods
- [ ] Implement agent configuration management

#### 4.2 RAG Agent
- [ ] Implement `agents/rag_agent.py`
- [ ] Orchestrate RAG pipeline components
- [ ] Implement query processing and response generation

#### 4.3 Chat Agent
- [ ] Implement `agents/chat_agent.py`
- [ ] Manage conversation state and flow
- [ ] Implement chat history and context management

#### 4.4 Wiki Agent
- [ ] Implement `agents/wiki_agent.py`
- [ ] Orchestrate wiki generation pipeline
- [ ] Manage wiki structure and content

### Phase 5: Service Layer (Week 5)

#### 5.1 Chat Service
- [ ] Implement `services/chat_service.py`
- [ ] Extract business logic from `simple_chat.py`
- [ ] Implement chat orchestration and state management

#### 5.2 Wiki Service
- [ ] Implement `services/wiki_service.py`
- [ ] Extract wiki business logic
- [ ] Implement wiki generation and management

#### 5.3 Project Service
- [ ] Implement `services/project_service.py`
- [ ] Extract project management logic
- [ ] Implement project processing and caching

#### 5.4 Cache Service
- [ ] Implement `services/cache_service.py`
- [ ] Implement caching layer for responses
- [ ] Add cache invalidation and management

### Phase 6: API Layer Refactoring (Week 6)

#### 6.1 API Models
- [ ] Extract models from `api.py` to `models/` directory
- [ ] Organize models by domain (chat, wiki, rag)
- [ ] Implement proper validation and serialization

#### 6.2 API Endpoints
- [ ] Split `api.py` into domain-specific endpoint files
- [ ] Implement `api/v1/chat.py`
- [ ] Implement `api/v1/wiki.py`
- [ ] Implement `api/v1/projects.py`
- [ ] Create `api/dependencies.py` for shared dependencies

#### 6.3 FastAPI App Configuration
- [ ] Create `app.py` for FastAPI configuration
- [ ] Implement middleware and CORS configuration
- [ ] Set up route registration and error handling

### Phase 7: Data Layer (Week 7)

#### 7.1 Database Management
- [ ] Implement `data/database.py`
- [ ] Extract database logic from `data_pipeline.py`
- [ ] Implement connection management and pooling

#### 7.2 Vector Store
- [ ] Implement `data/vector_store.py`
- [ ] Extract vector operations from RAG components
- [ ] Implement vector database abstraction

#### 7.3 Repositories
- [ ] Implement `data/repositories/wiki_repo.py`
- [ ] Implement `data/repositories/project_repo.py`
- [ ] Create data access layer abstractions

### Phase 8: Utility and Support (Week 8)

#### 8.1 Utility Functions
- [ ] Implement `utils/text_processing.py`
- [ ] Implement `utils/file_utils.py`
- [ ] Implement `utils/validation.py`
- [ ] Extract utility functions from existing files

#### 8.2 WebSocket Handling
- [ ] Move `websocket_wiki.py` to `websocket/wiki_handler.py`
- [ ] Refactor WebSocket logic for new structure
- [ ] Implement proper error handling and connection management

#### 8.3 Prompt Management
- [ ] Move `prompts.py` to appropriate location
- [ ] Organize prompts by component and use case
- [ ] Implement prompt versioning and management

### Phase 9: Testing and Validation (Week 9)

#### 9.1 Test Infrastructure
- [ ] Set up test directory structure
- [ ] Implement test configuration and fixtures
- [ ] Create mock objects for external dependencies

#### 9.2 Component Tests
- [ ] Implement `tests/test_components.py`
- [ ] Test individual RAG components
- [ ] Validate component interfaces and contracts

#### 9.3 Pipeline Tests
- [ ] Implement `tests/test_pipelines.py`
- [ ] Test RAG pipeline integration
- [ ] Validate end-to-end workflows

#### 9.4 Service Tests
- [ ] Implement `tests/test_services.py`
- [ ] Test business logic services
- [ ] Validate service orchestration

#### 9.5 Integration Tests
- [ ] Test API endpoints with new structure
- [ ] Validate WebSocket functionality
- [ ] Test complete user workflows

### Phase 10: Migration and Cleanup (Week 10)

#### 10.1 Update Main Entry Point
- [ ] Refactor `main.py` to use new structure
- [ ] Update import statements
- [ ] Implement proper startup sequence

#### 10.2 Import Statement Updates
- [ ] Update all import statements throughout codebase
- [ ] Fix circular import issues
- [ ] Validate import paths

#### 10.3 Remove Old Files
- [ ] Remove original monolithic files
- [ ] Clean up unused imports and dependencies
- [ ] Update documentation and README files

#### 10.4 Final Validation
- [ ] Run comprehensive test suite
- [ ] Validate all functionality works as expected
- [ ] Performance testing and optimization
- [ ] Documentation updates

## File Migration Mapping

### Current → New Location
| Current File | New Location | Action |
|--------------|--------------|---------|
| `api.py` | `api/api/v1/` + `models/` + `app.py` | Split into multiple files |
| `rag.py` | `components/` + `pipelines/` + `agents/` | Extract components |
| `simple_chat.py` | `services/chat_service.py` + `pipelines/chat_pipeline.py` | Extract service and pipeline |
| `config.py` | `core/config.py` | Refactor and move |
| `openai_client.py` | `components/generator/openai_generator.py` | Extract generator logic |
| `azureai_client.py` | `components/generator/azure_generator.py` | Extract generator logic |
| `bedrock_client.py` | `components/generator/bedrock_generator.py` | Extract generator logic |
| `dashscope_client.py` | `components/generator/dashscope_generator.py` | Extract generator logic |
| `openrouter_client.py` | `components/generator/openrouter_generator.py` | Extract generator logic |
| `ollama_patch.py` | `components/generator/ollama_generator.py` | Extract generator logic |
| `data_pipeline.py` | `data/` + `services/` | Split into data and service layers |
| `websocket_wiki.py` | `websocket/wiki_handler.py` | Move and refactor |
| `prompts.py` | `utils/prompts.py` | Move and organize |
| `tools/embedder.py` | `components/embedder/embedder_manager.py` | Refactor and enhance |

## Risk Assessment and Mitigation

### High-Risk Areas
1. **Breaking Changes**: API endpoints may change during refactoring
   - **Mitigation**: Maintain backward compatibility during transition
   - **Mitigation**: Implement feature flags for gradual rollout

2. **Import Dependencies**: Complex import relationships may cause issues
   - **Mitigation**: Use dependency injection and interfaces
   - **Mitigation**: Implement comprehensive testing

3. **Performance Impact**: New structure may introduce overhead
   - **Mitigation**: Profile and optimize critical paths
   - **Mitigation**: Implement caching where appropriate

### Medium-Risk Areas
1. **Configuration Management**: New config structure may break existing setups
   - **Mitigation**: Provide migration scripts
   - **Mitigation**: Maintain backward compatibility

2. **Testing Coverage**: New structure requires comprehensive testing
   - **Mitigation**: Implement test-driven development
   - **Mitigation**: Maintain high test coverage

## Success Criteria

### Functional Requirements
- [ ] All existing functionality preserved
- [ ] API endpoints work identically
- [ ] WebSocket functionality maintained
- [ ] RAG pipeline performance maintained or improved

### Quality Requirements
- [ ] Code coverage > 90%
- [ ] All tests passing
- [ ] No circular import issues
- [ ] Clean dependency graph

### Performance Requirements
- [ ] Response times within 10% of current performance
- [ ] Memory usage optimized
- [ ] Startup time improved

## Rollback Plan

### Rollback Triggers
- Critical functionality broken
- Performance degradation > 20%
- Test coverage drops below 80%

### Rollback Procedure
1. Revert to previous Git commit
2. Restore original file structure
3. Validate functionality
4. Document issues for future iteration

## Post-Implementation Tasks

### Documentation Updates
- [ ] Update API documentation
- [ ] Create component usage guides
- [ ] Update README files
- [ ] Create architecture diagrams

### Team Training
- [ ] Conduct code walkthroughs
- [ ] Create development guidelines
- [ ] Document best practices
- [ ] Provide examples and templates

### Monitoring and Maintenance
- [ ] Set up performance monitoring
- [ ] Implement health checks
- [ ] Create maintenance schedules
- [ ] Plan future enhancements

## Timeline Summary

| Week | Phase | Focus | Deliverables |
|------|-------|-------|--------------|
| 1 | Foundation | Directory structure, core infrastructure | New folder structure, base classes |
| 2 | Components | Extract generator, embedder, retriever | Component implementations |
| 3 | Pipelines | RAG, chat, wiki pipelines | Pipeline orchestration |
| 4 | Agents | AI agent layer | Agent implementations |
| 5 | Services | Business logic services | Service layer |
| 6 | API Layer | Endpoints and models | API refactoring |
| 7 | Data Layer | Database and repositories | Data access layer |
| 8 | Utilities | Support functions and WebSocket | Utility implementations |
| 9 | Testing | Comprehensive testing | Test suite |
| 10 | Migration | Final migration and cleanup | Production-ready code |

## Conclusion

This restructure will transform the API folder from a monolithic, hard-to-maintain structure into a clean, modular, and RAG-optimized architecture. The new structure will improve code maintainability, enable better testing, and provide a solid foundation for future enhancements.

The phased approach minimizes risk while ensuring all functionality is preserved. Each phase builds upon the previous one, allowing for incremental validation and early detection of issues.

Upon completion, the codebase will be significantly more maintainable, testable, and scalable, following modern Python project best practices and RAG application patterns.
