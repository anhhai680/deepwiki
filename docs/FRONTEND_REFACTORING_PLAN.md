# Frontend Refactoring Plan - DeepWiki

## Problem Analysis

The frontend codebase has several critical maintainability issues:

### Large Files Identified
1. **`/src/app/[owner]/[repo]/page.tsx`** - **2,357 lines** (Critical)
2. **`/src/app/[owner]/[repo]/slides/page.tsx`** - **1,299 lines** (Critical)
3. **`/src/components/Ask.tsx`** - **1,062 lines** (Critical)
4. **`/src/app/page.tsx`** - **707 lines** (High Priority)
5. **`/src/app/[owner]/[repo]/workshop/page.tsx`** - **625 lines** (High Priority)
6. **`/src/components/Mermaid.tsx`** - **624 lines** (High Priority)
7. **`/src/components/UserSelector.tsx`** - **533 lines** (Medium Priority)

### Key Issues
- **Monolithic components** with mixed responsibilities
- **Embedded business logic** in presentation components
- **Repeated utility functions** across multiple files
- **Complex state management** without proper separation
- **Inline styles and configuration** mixed with component logic
- **No custom hooks** for reusable logic
- **Large interface definitions** repeated across files

## Proposed Modular Architecture

### 1. Component Architecture Restructure

#### **A. Extract Page-Level Components**

**Before:**
```
src/app/[owner]/[repo]/page.tsx (2,357 lines)
```

**After:**
```
src/app/[owner]/[repo]/
├── page.tsx                     # Main page orchestrator (~100 lines)
├── components/
│   ├── WikiViewer/
│   │   ├── index.tsx           # Main wiki viewer
│   │   ├── WikiNavigation.tsx  # Tree navigation
│   │   ├── WikiContent.tsx     # Content display
│   │   └── WikiToolbar.tsx     # Action buttons
│   ├── RepositoryHeader/
│   │   ├── index.tsx           # Repository info header
│   │   ├── RepoActions.tsx     # Generate, download actions
│   │   └── RepoMetadata.tsx    # Type, URL, status info
│   └── WikiSidebar/
│       ├── index.tsx           # Collapsible sidebar
│       ├── SectionTree.tsx     # Section navigation
│       └── PageList.tsx        # Page listing
├── hooks/
│   ├── useWikiGeneration.ts    # Wiki generation logic
│   ├── useWikiCache.ts         # Cache management
│   ├── useRepositoryData.ts    # Repository data fetching
│   └── useWikiNavigation.ts    # Navigation state
└── utils/
    ├── wikiHelpers.ts          # Wiki-specific utilities
    ├── cacheHelpers.ts         # Cache utilities
    └── repositoryHelpers.ts    # Repository utilities
```

#### **B. Modularize Ask Component**

**Before:**
```
src/components/Ask.tsx (1,062 lines)
```

**After:**
```
src/components/Ask/
├── index.tsx                   # Main Ask component (~100 lines)
├── components/
│   ├── ChatInterface/
│   │   ├── index.tsx          # Chat UI container
│   │   ├── MessageList.tsx    # Message display
│   │   ├── MessageInput.tsx   # Input with controls
│   │   └── LoadingIndicator.tsx # Loading states
│   ├── ResearchMode/
│   │   ├── index.tsx          # Research controls
│   │   ├── StageNavigation.tsx # Stage navigation
│   │   ├── ResearchProgress.tsx # Progress display
│   │   └── ResearchResults.tsx # Results display
│   ├── RepositorySelector/
│   │   ├── index.tsx          # Repository selection
│   │   ├── SingleRepoMode.tsx # Single repo selector
│   │   └── MultiRepoMode.tsx  # Multi repo selector
│   └── ConfigurationPanel/
│       ├── index.tsx          # Config container
│       ├── ModelSelector.tsx  # Model selection
│       └── SettingsPanel.tsx  # Additional settings
├── hooks/
│   ├── useChatWebSocket.ts    # WebSocket management
│   ├── useResearchMode.ts     # Research functionality
│   ├── useRepositorySelection.ts # Repository selection logic
│   └── useModelConfiguration.ts # Model config
├── utils/
│   ├── chatHelpers.ts         # Chat utilities
│   ├── researchHelpers.ts     # Research utilities
│   └── urlHelpers.ts          # URL parsing utilities
└── types/
    ├── chat.ts                # Chat-related types
    ├── research.ts            # Research types
    └── repository.ts          # Repository types
```

#### **C. Break Down Home Page**

**Before:**
```
src/app/page.tsx (707 lines)
```

**After:**
```
src/app/
├── page.tsx                    # Main home page (~100 lines)
├── components/
│   ├── HomeLayout/
│   │   ├── index.tsx          # Two-column layout
│   │   ├── DesktopLayout.tsx  # Desktop view
│   │   └── MobileLayout.tsx   # Mobile responsive
│   ├── RepositorySection/
│   │   ├── index.tsx          # Repository input section
│   │   ├── RepositoryInput.tsx # URL input
│   │   ├── GenerationForm.tsx # Generation controls
│   │   └── ValidationDisplay.tsx # Input validation
│   └── ProjectsSection/
│       ├── index.tsx          # Existing projects
│       ├── ProjectGrid.tsx    # Grid display
│       ├── ProjectFilters.tsx # Search/filter
│       └── ProjectActions.tsx # Bulk actions
├── hooks/
│   ├── useHomePageState.ts    # Home page state
│   ├── useRepositoryInput.ts  # Input handling
│   ├── useProjectManagement.ts # Project operations
│   └── useAuthStatus.ts       # Authentication
└── utils/
    ├── repositoryValidation.ts # Input validation
    ├── configurationHelpers.ts # Config management
    └── homePageHelpers.ts     # Home page utilities
```

### 2. Shared Components Refactoring

#### **A. Extract Mermaid Component**

**Before:**
```
src/components/Mermaid.tsx (624 lines)
```

**After:**
```
src/components/Mermaid/
├── index.tsx                  # Main Mermaid component (~100 lines)
├── components/
│   ├── DiagramContainer.tsx   # Diagram wrapper
│   ├── DiagramToolbar.tsx     # Zoom, fullscreen controls  
│   ├── FullScreenModal.tsx    # Fullscreen view
│   └── DiagramPreprocessor.tsx # Syntax processing
├── hooks/
│   ├── useMermaidRendering.ts # Rendering logic
│   ├── useDiagramControls.ts  # Zoom, pan controls
│   └── useDiagramPreprocessing.ts # Syntax preprocessing
├── utils/
│   ├── mermaidConfig.ts       # Mermaid configuration
│   ├── diagramSanitization.ts # Syntax cleaning
│   └── themeHelpers.ts        # Theme management
└── styles/
    ├── mermaid.css           # Mermaid-specific styles
    └── themes.css            # Theme definitions
```

#### **B. Modularize UserSelector**

**Before:**
```
src/components/UserSelector.tsx (533 lines)
```

**After:**
```
src/components/UserSelector/
├── index.tsx                  # Main selector component (~80 lines)
├── components/
│   ├── ProviderSelector.tsx   # AI provider selection
│   ├── ModelSelector.tsx      # Model selection
│   ├── CustomModelInput.tsx   # Custom model input
│   ├── FileFilters/
│   │   ├── index.tsx         # Filter container
│   │   ├── FilterModeToggle.tsx # Include/exclude toggle
│   │   ├── DirectoryFilters.tsx # Directory filters
│   │   ├── FileFilters.tsx   # File filters
│   │   └── DefaultValuesDisplay.tsx # Default values
│   └── ConfigurationDisplay/
│       ├── index.tsx         # Config summary
│       └── ConfigPreview.tsx # Configuration preview
├── hooks/
│   ├── useModelConfiguration.ts # Model config logic
│   ├── useFileFilters.ts     # File filtering logic
│   └── useProviderDefaults.ts # Provider defaults
└── utils/
    ├── modelHelpers.ts       # Model utilities
    ├── filterHelpers.ts      # Filter utilities
    └── providerHelpers.ts    # Provider utilities
```

### 3. Shared Infrastructure

#### **A. Custom Hooks Library**

```
src/hooks/
├── api/
│   ├── useApiCall.ts         # Generic API call hook
│   ├── useWebSocket.ts       # WebSocket management
│   ├── useModelConfig.ts     # Model configuration
│   └── useProjectData.ts     # Project data fetching
├── state/
│   ├── useLocalStorage.ts    # Local storage management
│   ├── useSessionState.ts    # Session state
│   ├── useFormState.ts       # Form state management
│   └── useAsyncState.ts      # Async state management
├── ui/
│   ├── useModal.ts           # Modal state management
│   ├── useNotification.ts    # Notification system
│   ├── useTheme.ts           # Theme management
│   └── useResponsive.ts      # Responsive utilities
└── business/
    ├── useRepositoryOps.ts   # Repository operations
    ├── useWikiGeneration.ts  # Wiki generation
    ├── useChatOps.ts         # Chat operations
    └── useFileFiltering.ts   # File filtering logic
```

#### **B. Utilities Library**

```
src/utils/
├── api/
│   ├── apiClient.ts          # API client setup
│   ├── requestHelpers.ts     # Request utilities
│   ├── responseHelpers.ts    # Response processing
│   └── errorHandling.ts      # Error handling
├── data/
│   ├── cacheManager.ts       # Cache management
│   ├── dataTransformers.ts   # Data transformation
│   ├── validators.ts         # Input validation
│   └── serializers.ts        # Data serialization
├── ui/
│   ├── formatters.ts         # Data formatting
│   ├── classNameHelpers.ts   # CSS utilities
│   ├── themeUtils.ts         # Theme utilities
│   └── responsiveUtils.ts    # Responsive helpers
└── business/
    ├── repositoryUtils.ts    # Repository utilities
    ├── wikiUtils.ts          # Wiki utilities
    ├── chatUtils.ts          # Chat utilities
    └── configUtils.ts        # Configuration utilities
```

#### **C. Shared Types Library**

```
src/types/
├── api/
│   ├── requests.ts           # API request types
│   ├── responses.ts          # API response types
│   └── websocket.ts          # WebSocket types
├── data/
│   ├── repository.ts         # Repository data types
│   ├── wiki.ts               # Wiki data types
│   ├── chat.ts               # Chat data types
│   └── project.ts            # Project data types
├── ui/
│   ├── components.ts         # Component prop types
│   ├── forms.ts              # Form types
│   └── modals.ts             # Modal types
└── config/
    ├── models.ts             # Model configuration types
    ├── providers.ts          # Provider types
    └── settings.ts           # Settings types
```

## Implementation Strategy

### Phase 1: Critical Files (Week 1)
**Priority: Critical Impact**

1. **Refactor Ask Component** (`src/components/Ask.tsx`)
   - Extract chat interface components
   - Create custom hooks for WebSocket and research logic
   - Separate repository selection logic
   - **Target: Reduce from 1,062 to ~100 lines**

2. **Break down Repository Page** (`src/app/[owner]/[repo]/page.tsx`)
   - Extract wiki viewer components
   - Create wiki generation hooks
   - Separate navigation and content display
   - **Target: Reduce from 2,357 to ~100 lines**

### Phase 2: High Priority Files (Week 2)
**Priority: High Impact**

3. **Modularize Home Page** (`src/app/page.tsx`)
   - Extract layout components
   - Create repository input components
   - Separate project management logic
   - **Target: Reduce from 707 to ~100 lines**

4. **Refactor Mermaid Component** (`src/components/Mermaid.tsx`)
   - Extract rendering logic
   - Create diagram control components
   - Separate preprocessing utilities
   - **Target: Reduce from 624 to ~100 lines**

### Phase 3: Medium Priority Files (Week 3)
**Priority: Medium Impact**

5. **Modularize Slides Page** (`src/app/[owner]/[repo]/slides/page.tsx`)
   - Extract slide generation logic
   - Create slide viewer components
   - Separate export functionality
   - **Target: Reduce from 1,299 to ~100 lines**

6. **Break down UserSelector** (`src/components/UserSelector.tsx`)
   - Extract filter components
   - Create model selection components
   - Separate configuration logic
   - **Target: Reduce from 533 to ~80 lines**

### Phase 4: Infrastructure & Polish (Week 4)
**Priority: Foundation**

7. **Create Shared Infrastructure**
   - Build custom hooks library
   - Create utilities library
   - Establish shared types library
   - Set up component documentation

8. **Testing & Validation**
   - Add unit tests for all new components
   - Integration testing for complex flows
   - Performance testing and optimization
   - Documentation and examples

## Expected Benefits

### Maintainability Improvements
- **90% reduction** in average file size
- **Clear separation** of concerns
- **Reusable components** across the application
- **Consistent patterns** for state management
- **Easier debugging** with smaller, focused components

### Developer Experience
- **Faster development** with reusable hooks and utilities
- **Better IDE support** with smaller files
- **Easier testing** with isolated components
- **Clearer code review** process
- **Onboarding simplification** for new developers

### Performance Benefits
- **Better code splitting** with modular architecture
- **Improved bundle optimization** with tree shaking
- **Reduced re-renders** with focused state management
- **Lazy loading** of complex components
- **Memory optimization** with proper component lifecycle

## Risk Mitigation

### Testing Strategy
- **Comprehensive unit tests** for all extracted components
- **Integration tests** for complex workflows
- **Visual regression tests** for UI components
- **End-to-end tests** for critical user paths

### Incremental Migration
- **Feature flags** for new components during development
- **Parallel development** of old and new components
- **Gradual rollout** with rollback capabilities
- **User acceptance testing** at each phase

### Team Coordination
- **Clear naming conventions** for new components
- **Documentation standards** for all new code
- **Code review guidelines** for refactored components
- **Migration guides** for existing functionality

This refactoring plan will transform the DeepWiki frontend from a collection of monolithic files into a modern, maintainable, and scalable component architecture while preserving all existing functionality.
