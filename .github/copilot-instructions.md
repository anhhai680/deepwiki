# DeepWiki Copilot Instructions

## Repository Overview

**DeepWiki** is a full-stack web application that automatically generates interactive wikis for GitHub, GitLab, and BitBucket repositories using AI-powered analysis. The project combines a Python FastAPI backend with a Next.js TypeScript frontend to create comprehensive documentation with visual diagrams and intelligent Q&A capabilities.

**Repository Size**: ~21MB with 55+ source files
**Project Type**: Full-stack web application with AI integration
**Languages**: Python 3.11+, TypeScript/JavaScript, HTML/CSS
**Frameworks**: FastAPI (Python), Next.js 15.3.1 (React 19), Tailwind CSS
**Target Runtimes**: Python 3.11+, Node.js 20+, Docker

## Build and Validation Instructions

### Prerequisites
- **Python**: 3.11+ (required for FastAPI backend)
- **Node.js**: 20+ (required for Next.js frontend)
- **npm/yarn**: Package managers for JavaScript dependencies
- **Docker**: For containerized deployment (optional)

### Environment Setup
**Always create a `.env` file in the project root before building:**
```bash
# Required for embeddings (even if not using OpenAI models)
OPENAI_API_KEY=your_openai_api_key

# Optional - only required for specific model providers
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
LOG_FILE_PATH=backend/logs/application.log
```

### Build Commands (Always run in this order)

#### 1. Install Dependencies
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Install JavaScript dependencies
npm install
# or
yarn install
```

#### 2. Build Frontend
```bash
npm run build
# or
yarn build
```

#### 3. Start Backend
```bash
# Start the FastAPI server
python -m backend.main
# or use the run script
./run.sh
```

#### 4. Start Frontend (Development)
```bash
npm run dev
# or
yarn dev
```

### Docker Build (Alternative)
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t deepwiki .
docker run -p 8001:8001 -p 3000:3000 deepwiki
```

### Testing
```bash
# Run Python tests
cd test
python -m pytest

# Run JavaScript linting
npm run lint
# or
yarn lint
```

### Validation Steps
1. **Backend Health Check**: `curl http://localhost:8001/health`
2. **Frontend Access**: Open http://localhost:3000 in browser
3. **API Endpoints**: Verify FastAPI docs at http://localhost:8001/docs

## Project Architecture

### Directory Structure
```
deepwiki/
├── backend/                      # Python FastAPI backend
│   ├── main.py                   # Entry point (port 8001)
│   ├── app.py                    # FastAPI app definition
│   ├── api/                      # API route handlers
│   ├── config/                   # Configuration files
│   │   ├── generator.json        # AI model configurations
│   │   ├── embedder.json         # Embedding model settings
│   │   └── repo.json             # Repository filters
│   ├── core/                     # Core business logic
│   ├── services/                 # Service layer
│   ├── tests/                    # Python tests suite
│   ├── pipelines/                # Data processing pipelines
│   ├── models/                   # Data models and schemas
│   ├── utils/                    # Utility functions
│   └── requirements.txt          # Python dependencies
├── src/                          # Next.js frontend
│   ├── app/                      # App router pages
│   ├── components/               # React components
│   ├── contexts/                 # React contexts
│   └── types/                    # TypeScript type definitions
├── public/                       # Static assets
├── package.json                  # Node.js dependencies
├── next.config.ts                # Next.js configuration
├── tailwind.config.js            # Tailwind CSS config
├── tsconfig.json                 # TypeScript config
├── docker-compose.yml            # Docker orchestration
└── Dockerfile                    # Multi-stage Docker build
```

### Key Configuration Files
- **`backend/config/generator.json`**: AI model provider configurations
- **`backend/config/embedder.json`**: Vector embedding settings
- **`backend/config/repo.json`**: Repository processing filters
- **`next.config.ts`**: Next.js build and proxy configuration
- **`tailwind.config.js`**: CSS framework configuration
- **`eslint.config.mjs`**: Code quality rules

### Main Entry Points
- **Backend**: `backend/main.py` (FastAPI server on port 8001)
- **Frontend**: `src/app/page.tsx` (Next.js main page)
- **API Routes**: `backend/api/` (FastAPI endpoints)

## Development Workflow

### Pre-commit Checks
- **Linting**: `npm run lint` (ESLint + Next.js rules)
- **Type Checking**: TypeScript compilation via `tsc`
- **Python Formatting**: Follow PEP 8 standards

### Continuous Integration
- **GitHub Actions**: `.github/workflows/docker-build-push.yml`
- **Docker Builds**: Multi-platform builds for AMD64/ARM64
- **Automated Testing**: Runs on pull requests and main branch

### Code Quality Standards
- **TypeScript**: Strict mode enabled, no implicit any
- **Python**: Type hints, Pydantic models for validation
- **React**: Functional components with hooks, TypeScript interfaces
- **API**: FastAPI with automatic OpenAPI documentation

## Common Issues and Solutions

### Build Failures
1. **Missing .env file**: Always create `.env` with required API keys
2. **Python version mismatch**: Ensure Python 3.11+ is installed
3. **Node.js version**: Requires Node.js 20+ for Next.js 15
4. **Memory issues**: Docker build uses 6GB memory limit

### Runtime Issues
1. **Port conflicts**: Backend uses 8001, frontend uses 3000
2. **API key errors**: Verify all required environment variables
3. **CORS issues**: Backend configured to allow all origins
4. **Docker networking**: Ensure proper port mapping

### Performance Considerations
- **Large repositories**: May timeout during processing
- **Memory usage**: Backend processes large codebases
- **Build time**: Docker builds can take 5-10 minutes
- **Hot reload**: Disabled in production for stability

## Dependencies and Integration

### External Services
- **OpenAI API**: Required for embeddings, optional for generation
- **Google Gemini**: Optional AI model provider
- **OpenRouter**: Optional multi-model provider
- **Azure OpenAI**: Optional enterprise provider
- **Ollama**: Optional local model hosting

### Key Libraries
- **Python**: FastAPI, uvicorn, google-generativeai, openai, faiss-cpu
- **JavaScript**: Next.js, React 19, Tailwind CSS, Mermaid.js
- **AI/ML**: adalflow, tiktoken, numpy, langid

## Trust These Instructions

**Only search the codebase if the information above is incomplete or found to be in error.** These instructions have been validated and contain the correct build sequences, configuration details, and architectural information needed for efficient development.

### Current Feature Development
**Active Feature**: Frontend Code Refactoring for Maintainability (Branch: `001-refactor-the-frontend`)
- **Goal**: Refactor 7 critical oversized files (533-2,357 lines each) into maintainable modules <500 lines
- **Critical Files**: 
  - `src/app/[owner]/[repo]/page.tsx` (2,357 lines) - Main repository page
  - `src/components/Ask.tsx` (1,062 lines) - Chat/Q&A interface  
  - `src/components/Mermaid.tsx` (624 lines) - Diagram rendering
  - `src/app/page.tsx` (707 lines) - Home page
  - Plus 3 other large page components (625, 1,299, 533 lines)
- **Approach**: Extract utilities, types, hooks while preserving ALL existing functionality
- **Requirements**: Zero breaking changes, maintain all APIs, preserve user experience
- **Specs Location**: `/specs/001-refactor-the-frontend/` (spec.md, plan.md, research.md, data-model.md, contracts/, quickstart.md)

### Quick Reference
- **Backend**: `python -m backend.main` (port 8001)
- **Frontend**: `npm run dev` (port 3000)
- **Docker**: `docker-compose up --build`
- **Testing**: `python -m pytest` (Python), `npm run lint` (JS)
- **Config**: `backend/config/` directory for AI model settings
