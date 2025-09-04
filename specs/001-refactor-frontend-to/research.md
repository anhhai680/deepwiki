# Research: Quick Access Ask UI from Home Page

## Research Tasks Completed

### 1. Home Page Integration Approach
**Decision**: Embed Ask UI directly into home page as a new section
**Rationale**: 
- User specification clearly states "embedded directly in home page"
- Provides immediate access without modal overlay
- Maintains visual consistency with existing home page design
- Leverages existing page layout structure

**Alternatives considered**:
- Modal overlay approach (rejected - user preference for embedded)
- Separate /ask route (rejected - reduces "quick access" benefit)
- Floating widget (rejected - potential UI conflicts)

### 2. Repository Selection Method
**Decision**: Repository selector with previously indexed repositories + manual URL input
**Rationale**:
- User specification: "Required the users select one of repository has been indexed"
- Leverages existing RepositorySelector.tsx component
- Provides fallback for new repositories via manual URL input
- Maintains consistency with current repository selection patterns

**Alternatives considered**:
- Only previously indexed repositories (rejected - limits user flexibility)
- Only manual URL input (rejected - doesn't leverage indexed repositories)
- Auto-suggestion without restriction (rejected - user specified indexed requirement)

### 3. Component Reuse Strategy
**Decision**: Reuse existing Ask.tsx component without modifications
**Rationale**:
- User requirement: "utilize the Ask.tsx and existing frontend tech stack"
- Ask.tsx is already implemented in `src/components/Ask.tsx` with full functionality
- Currently used in repository pages (`src/app/[owner]/[repo]/page.tsx`) via modal
- Already supports multi-repository functionality and all required features
- Maintains feature parity and consistency

**Implementation approach**:
- Create HomePageAsk wrapper component in `src/components/HomePageAsk.tsx`
- Pass repository context from RepositorySelector to Ask.tsx
- Reuse existing props interface for Ask component
- Maintain existing Ask.tsx usage patterns from repository pages

**Existing Ask.tsx Analysis**:
- Located: `src/components/Ask.tsx`
- Props: `repoInfo: RepoInfo | RepoInfo[]`, `projects?: ProcessedProject[]`, etc.
- Features: Multi-repository support, deep research, conversation history
- Dependencies: MultiRepositorySelector, ModelSelectionModal, websocket client

### 4. State Management for Repository Context
**Decision**: Local component state with repository info passed to Ask component
**Rationale**:
- Simple state management for single-page feature
- Consistent with existing Ask.tsx usage patterns
- No global state needed for this isolated feature
- Easier to maintain and debug

**Alternatives considered**:
- Global state management (rejected - overkill for single feature)
- URL-based state (rejected - complicates home page routing)
- LocalStorage direct manipulation (rejected - component should own state)

### 5. Integration with Existing Home Page Layout
**Decision**: Add Ask section between repository input form and demo charts section
**Rationale**:
- Logical flow: repository input form → Ask functionality → demo visualizations
- Current home page structure in `src/app/page.tsx` has clear sections
- Maintains existing page hierarchy and visual balance
- Non-breaking addition to existing layout structure
- Preserves existing conditional rendering for projects vs welcome content

**Home Page Structure Analysis**:
- Header: Logo, title, repository input form with RepositorySelector
- Main: Conditional rendering based on `projects.length > 0`
- Existing sections: ProcessedProjects, Quick Start info, Visualization demos
- Footer: Copyright and social links
- Uses Tailwind CSS with CSS variables for theming

### 6. Multi-Repository Support on Home Page
**Decision**: Support both single and multi-repository selection
**Rationale**:
- Ask.tsx already supports multi-repository functionality
- Provides feature parity with repository page Ask
- Leverages existing MultiRepositorySelector component
- User scenarios include multi-repository querying

### 7. Authentication Handling
**Decision**: Pass through existing authentication state and tokens
**Rationale**:
- Reuse existing auth flow from home page
- Repository-specific tokens handled by existing Ask.tsx logic
- No additional authentication complexity needed
- Maintains security model consistency

## Technical Decisions Summary

| Aspect | Decision | Key Dependencies |
|--------|----------|------------------|
| Integration | New section in home page after header | src/app/page.tsx |
| Repository Selection | RepositorySelector + useProcessedProjects | src/components/RepositorySelector.tsx, src/hooks/useProcessedProjects.ts |
| Component Architecture | HomePageAsk wrapper around Ask.tsx | src/components/Ask.tsx |
| State Management | Local component state with RepoInfo context | React useState, existing RepoInfo type |
| Layout Position | Between repository form and demo content | Existing home page layout structure |
| Multi-repo Support | Full support via existing Ask.tsx features | src/components/MultiRepositorySelector.tsx |
| Authentication | Pass through existing auth from home page | Existing auth state management |

## Risk Assessment

**Low Risk**:
- Component reuse (Ask.tsx proven stable)
- Layout integration (additive, non-breaking)
- Repository selection (existing patterns)

**Medium Risk**:
- State synchronization between home page and Ask component
- Repository context handling for non-indexed repositories

**Mitigation Strategies**:
- Comprehensive component testing
- Integration testing with existing Ask.tsx
- Fallback handling for repository selection edge cases
