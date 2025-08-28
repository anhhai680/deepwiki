# DeepWiki Frontend

This directory contains the Next.js frontend application for DeepWiki, providing an intuitive interface for generating and exploring AI-powered wikis from GitHub, GitLab, and Bitbucket repositories.

## 🏗️ Architecture Overview

The frontend follows Next.js 15 App Router architecture with modern React patterns:

```
src/
├── app/                    # Next.js App Router
│   ├── [owner]/           # Dynamic route for repository owners
│   │   └── [repo]/        # Dynamic route for repositories
│   │       ├── page.tsx   # Repository wiki page
│   │       ├── loading.tsx # Loading state
│   │       └── error.tsx  # Error handling
│   ├── api/               # API route handlers
│   ├── favicon.ico        # Site icon
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout component
│   ├── page.tsx           # Homepage
│   └── wiki/              # Wiki-specific routes
│       └── page.tsx       # Wiki generation page
├── components/             # Reusable React components
│   ├── Ask.tsx            # AI chat interface
│   ├── ConfigurationModal.tsx # Settings configuration
│   ├── Markdown.tsx       # Markdown renderer
│   ├── Mermaid.tsx        # Diagram renderer
│   ├── ModelSelectionModal.tsx # AI model selection
│   ├── ProcessedProjects.tsx # Project list display
│   ├── theme-toggle.tsx   # Dark/light theme switcher
│   ├── TokenInput.tsx     # Access token input
│   ├── UserSelector.tsx   # User selection interface
│   ├── WikiTreeView.tsx   # Wiki navigation tree
│   └── WikiTypeSelector.tsx # Repository type selection
├── contexts/               # React contexts
│   └── LanguageContext.tsx # Internationalization context
├── hooks/                  # Custom React hooks
│   └── useProcessedProjects.ts # Project data management
├── i18n.ts                 # Internationalization setup
├── messages/               # Localization files
│   ├── en.json            # English
│   ├── es.json            # Spanish
│   ├── fr.json            # French
│   ├── ja.json            # Japanese
│   ├── kr.json            # Korean
│   ├── pt-br.json         # Portuguese (Brazil)
│   ├── ru.json            # Russian
│   ├── vi.json            # Vietnamese
│   ├── zh.json            # Chinese (Simplified)
│   └── zh-tw.json         # Chinese (Traditional)
├── types/                  # TypeScript type definitions
│   ├── repoinfo.tsx       # Repository information types
│   └── wiki/              # Wiki-specific types
│       ├── index.tsx      # Wiki type exports
│       └── types.tsx      # Wiki data structures
└── utils/                  # Utility functions
    ├── getRepoUrl.tsx     # Repository URL utilities
    ├── urlDecoder.tsx     # URL decoding utilities
    └── websocketClient.ts # WebSocket client utilities
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm, yarn, or pnpm package manager
- Backend API server running (see [Backend README](../backend/README.md))

### Installation

```bash
# Install dependencies
npm install
# or
yarn install
# or
pnpm install
```

### Development

```bash
# Start development server
npm run dev
# or
yarn dev
# or
pnpm dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000)

### Building for Production

```bash
# Build the application
npm run build
# or
yarn build
# or
pnpm build

# Start production server
npm start
# or
yarn start
# or
pnpm start
```

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the project root:

```bash
# Backend API configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8001

# Feature flags
NEXT_PUBLIC_ENABLE_DEEP_RESEARCH=true
NEXT_PUBLIC_ENABLE_MULTI_PROVIDER=true
NEXT_PUBLIC_ENABLE_AUTH_MODE=false
```

### Backend Connection

The frontend connects to the backend API server. Ensure the backend is running and accessible at the URL specified in `NEXT_PUBLIC_API_BASE_URL`.

## 🎨 Key Features

### 1. Repository Input & Processing
- **Multi-Platform Support**: GitHub, GitLab, and Bitbucket repositories
- **Private Repository Access**: Secure token-based authentication
- **Real-Time Processing**: Live progress updates during wiki generation

### 2. AI-Powered Wiki Generation
- **Smart Analysis**: AI-driven code structure understanding
- **Visual Diagrams**: Automatic Mermaid diagram generation
- **Comprehensive Documentation**: Context-aware documentation generation

### 3. Interactive Wiki Interface
- **Tree Navigation**: Hierarchical wiki structure navigation
- **Search & Filter**: Find specific content quickly
- **Responsive Design**: Works on desktop and mobile devices

### 4. AI Chat & Research
- **Ask Feature**: Chat with your repository using RAG
- **DeepResearch**: Multi-turn research for complex topics
- **Context Awareness**: AI responses based on actual codebase

### 5. Multi-Provider AI Support
- **Google Gemini**: High-quality AI responses
- **OpenAI**: GPT models for text generation
- **OpenRouter**: Access to multiple AI providers
- **Azure OpenAI**: Enterprise AI solutions
- **Ollama**: Local AI model support

## 🧩 Component Architecture

### Core Components

#### `Ask.tsx`
AI chat interface with support for:
- Real-time streaming responses
- Conversation history
- DeepResearch mode
- File context selection

#### `WikiTreeView.tsx`
Hierarchical wiki navigation with:
- Expandable/collapsible sections
- Search functionality
- Breadcrumb navigation
- Responsive design

#### `Mermaid.tsx`
Diagram rendering component supporting:
- Mermaid.js syntax
- Auto-sizing and scaling
- Error handling and fallbacks
- Interactive features

#### `ModelSelectionModal.tsx`
AI provider selection interface with:
- Provider-specific model lists
- Configuration options
- Real-time validation
- Settings persistence

### Layout Components

#### `layout.tsx`
Root application layout providing:
- Global navigation
- Theme management
- Internationalization
- Error boundaries

#### `page.tsx`
Homepage with:
- Repository input form
- Model selection
- Recent projects
- Feature highlights

## 🌐 Internationalization

DeepWiki supports 10+ languages through the `next-intl` library:

### Adding New Languages

1. Create a new language file in `messages/`
2. Add the language to `i18n.ts`
3. Update language selection components

### Language Context

The `LanguageContext.tsx` provides:
- Current language state
- Language switching functionality
- Locale-aware formatting
- RTL language support

## 🔌 API Integration

### REST API Calls

The frontend communicates with the backend through:
- **Repository Processing**: POST requests for wiki generation
- **Chat Completions**: Streaming chat responses
- **Project Management**: CRUD operations for projects
- **Configuration**: Settings management

### WebSocket Communication

Real-time features use WebSocket connections for:
- Progress updates during processing
- Live chat responses
- Status notifications
- Real-time collaboration

## 🎯 Development Guidelines

### Code Style
- **TypeScript**: Strict type checking enabled
- **ESLint**: Code quality and consistency
- **Prettier**: Code formatting
- **Component Structure**: Functional components with hooks

### State Management
- **React Context**: Global state (language, theme)
- **Custom Hooks**: Local state and side effects
- **Server State**: API data management
- **Form State**: Controlled form inputs

### Performance
- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js Image component
- **Bundle Analysis**: Webpack bundle analyzer
- **Lazy Loading**: Component and route lazy loading

## 🧪 Testing

### Test Setup

```bash
# Run tests
npm run test
# or
yarn test

# Run tests with coverage
npm run test:coverage
# or
yarn test:coverage
```

### Testing Strategy
- **Unit Tests**: Component and utility testing
- **Integration Tests**: API integration testing
- **E2E Tests**: User workflow testing
- **Accessibility Tests**: Screen reader and keyboard navigation

## 📱 Responsive Design

### Breakpoints
- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

### Design Principles
- **Mobile First**: Design for mobile, enhance for larger screens
- **Touch Friendly**: Appropriate touch targets and gestures
- **Accessibility**: WCAG 2.1 AA compliance
- **Performance**: Fast loading and smooth interactions

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Deploy to Vercel
npm run deploy
# or
vercel --prod
```

### Docker

```bash
# Build Docker image
docker build -t deepwiki-frontend .

# Run container
docker run -p 3000:3000 deepwiki-frontend
```

### Static Export

```bash
# Build static files
npm run build
npm run export

# Deploy static files to any hosting service
```

## 🔍 Troubleshooting

### Common Issues

#### Build Errors
- Check Node.js version compatibility
- Clear `.next` cache directory
- Verify all dependencies are installed

#### API Connection Issues
- Ensure backend server is running
- Check `NEXT_PUBLIC_API_BASE_URL` configuration
- Verify CORS settings on backend

#### Performance Issues
- Use React DevTools Profiler
- Check bundle size with `npm run analyze`
- Optimize images and assets

### Debug Mode

```bash
# Enable debug logging
DEBUG=* npm run dev

# Check browser console for errors
# Use React DevTools for component debugging
```

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Backend API Documentation](../backend/README.md)
- [Main Project README](../README.md)

## 🤝 Contributing

### Development Workflow
1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation
4. Submit pull request
5. Code review and merge

### Code Standards
- Follow TypeScript best practices
- Write comprehensive tests
- Update documentation
- Maintain accessibility standards
- Follow component naming conventions

## 📄 License

This frontend is part of the DeepWiki project and follows the same MIT license terms.
