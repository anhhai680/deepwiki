# Data Model: Frontend Refactoring

**Date**: September 9, 2025  
**Context**: Type definitions and interfaces extracted from oversized frontend components

## Core Type Categories

### 1. Chat & AI Model Types
*Extracted from Ask.tsx (1,062 lines)*

#### Model Configuration
```typescript
interface Model {
  id: string;
  name: string;
}

interface Provider {
  id: string;
  name: string;
  models: Model[];
  supportsCustomModel?: boolean;
  defaultModel?: string;
}
```

#### Chat System
```typescript
interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface ResearchStage {
  title: string;
  content: string;
  iteration: number;
  type: 'plan' | 'update' | 'conclusion';
}

interface AskProps {
  repoInfo: RepoInfo | RepoInfo[];
  projects?: ProcessedProject[];
}
```

### 2. Wiki Content Types
*Extracted from [owner]/[repo]/page.tsx (2,357 lines)*

#### Wiki Structure
```typescript
interface WikiPage {
  id: string;
  title: string;
  content: string;
  filePaths: string[];
  importance: 'high' | 'medium' | 'low';
  relatedPages: string[];
  parentId?: string;
  isSection?: boolean;
  children?: string[];
}

interface WikiSection {
  id: string;
  title: string;
  pages: string[];
  subsections?: string[];
}

interface WikiStructure {
  id: string;
  title: string;
  description: string;
  pages: WikiPage[];
  sections: WikiSection[];
  rootSections: string[];
}
```

### 3. Repository & Project Types
*Currently scattered across multiple components*

#### Repository Information
```typescript
interface RepoInfo {
  owner: string;
  repo: string;
  type: 'github' | 'gitlab' | 'bitbucket';
  url: string;
  branch?: string;
}

interface ProcessedProject {
  id: string;
  owner: string;
  repo: string;
  name: string;
  repo_type: string;
  submittedAt: number;
  language: string;
}
```

### 4. UI Component Props Types
*To be extracted from various large components*

#### Modal and Selection Components
```typescript
interface ModelSelectionProps {
  provider: string;
  setProvider: (value: string) => void;
  model: string;
  setModel: (value: string) => void;
  isCustomModel: boolean;
  setIsCustomModel: (value: boolean) => void;
  customModel: string;
  setCustomModel: (value: string) => void;
}

interface FileFilterProps {
  excludedDirs?: string;
  setExcludedDirs?: (value: string) => void;
  excludedFiles?: string;
  setExcludedFiles?: (value: string) => void;
  includedDirs?: string;
  setIncludedDirs?: (value: string) => void;
  includedFiles?: string;
  setIncludedFiles?: (value: string) => void;
}
```

### 5. Mermaid Diagram Types
*Extracted from Mermaid.tsx (624 lines)*

#### Diagram Configuration
```typescript
interface MermaidConfig {
  theme: string;
  securityLevel: 'strict' | 'loose';
  suppressErrorRendering: boolean;
  logLevel: string;
  maxTextSize: number;
  htmlLabels: boolean;
}

interface DiagramProps {
  chart: string;
  config?: Partial<MermaidConfig>;
  className?: string;
  id?: string;
}
```

## Type Organization Strategy

### 1. Shared Types Module
**Location**: `src/types/index.ts`  
**Purpose**: Central exports for commonly used types  
**Contents**: RepoInfo, ProcessedProject, Message, Model, Provider

### 2. Domain-Specific Type Modules
- `src/types/wiki.ts` - Wiki-related interfaces
- `src/types/chat.ts` - Chat and AI model types  
- `src/types/components.ts` - Component prop interfaces
- `src/types/diagrams.ts` - Mermaid and visualization types

### 3. Backward Compatibility Layer
**Strategy**: Re-export all existing types from their original locations  
**Implementation**: Add re-export statements to maintain existing imports  
**Timeline**: Gradual migration over multiple releases

## Validation Rules

### 1. Type Safety Requirements
- All extracted types must maintain existing type contracts
- No `any` types introduced during refactoring
- Strict TypeScript mode compliance maintained

### 2. Runtime Validation
- Preserve existing runtime validation logic
- Extract validation functions alongside type definitions
- Maintain error handling behavior

### 3. API Contract Preservation
- Component props interfaces unchanged from consumer perspective
- Internal type improvements only
- No breaking changes to public APIs

## Migration Path

### Phase 1: Extract and Consolidate
1. Create new type modules with consolidated definitions
2. Add re-exports from original locations
3. Update internal usage gradually

### Phase 2: Optimize and Clean
1. Remove duplicate type definitions
2. Improve type relationships and inheritance
3. Add better JSDoc documentation

### Phase 3: Standardize
1. Establish naming conventions
2. Create type utility functions where beneficial
3. Document best practices for future development

## Dependencies and Relationships

### External Dependencies
- React types (@types/react)
- Next.js types (next)
- Mermaid types (mermaid)

### Internal Relationships
- Chat types depend on Repository types
- Wiki types depend on Repository types
- Component prop types depend on domain types

### Breaking Change Prevention
- All type changes must be additive only
- Deprecated types maintained until major version
- Migration guides provided for internal usage
