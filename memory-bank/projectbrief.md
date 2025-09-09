# DeepWiki Project Brief

## Project Overview
**DeepWiki** is an AI-powered documentation generator that automatically creates comprehensive, interactive wikis for any GitHub, GitLab, or BitBucket repository. The system analyzes code structure, generates documentation, creates visual diagrams, and organizes everything into an easy-to-navigate wiki interface.

## Core Purpose
Transform any code repository into a comprehensive, AI-generated wiki with:
- Automated code analysis and documentation generation
- Visual diagrams (Mermaid charts) for architecture and data flow
- Interactive navigation and exploration
- AI-powered Q&A capabilities through RAG (Retrieval Augmented Generation)
- Multi-language support and internationalization

## Key Features
1. **Instant Documentation**: Turn repositories into wikis in seconds
2. **Private Repository Support**: Secure access with personal access tokens
3. **Smart Analysis**: AI-powered understanding of code structure and relationships
4. **Beautiful Diagrams**: Automatic Mermaid diagrams for visualization
5. **Easy Navigation**: Intuitive interface for wiki exploration
6. **Ask Feature**: Chat with repository using RAG-powered AI
7. **DeepResearch**: Multi-turn research process for complex topics
8. **Multiple Model Providers**: Support for Google Gemini, OpenAI, OpenRouter, Azure, and local Ollama models

## Technical Architecture
- **Frontend**: Next.js 15 with React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python) with async support
- **AI Integration**: Multiple LLM providers with configurable model selection
- **Vector Database**: FAISS for code embeddings and retrieval
- **Real-time Communication**: WebSocket support for streaming responses
- **Containerization**: Docker and Docker Compose support

## Target Users
- **Developers**: Quick understanding of unfamiliar codebases
- **Teams**: Shared documentation and knowledge sharing
- **Open Source Contributors**: Onboarding and contribution guidance
- **Technical Writers**: Automated documentation generation
- **Enterprise**: Private repository documentation and knowledge management

## Success Criteria
- Generate comprehensive wikis from any repository type
- Provide accurate, context-aware AI responses
- Create meaningful visual representations of code structure
- Support both public and private repositories securely
- Maintain high performance and reliability
- Enable seamless switching between different AI model providers

## Project Status
**Active Development** - Core functionality implemented, ongoing feature enhancements and optimization.

## Repository Information
- **Name**: deepwiki
- **Type**: Open source AI documentation tool
- **License**: MIT
- **Primary Language**: TypeScript/JavaScript (Frontend), Python (Backend)
- **Architecture**: Full-stack web application with AI integration
