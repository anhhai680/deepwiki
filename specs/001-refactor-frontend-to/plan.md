# Implementation Plan: Quick Access Ask UI from Home Page

**Branch**: `001-refactor-frontend-to` | **Date**: September 4, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-refactor-frontend-to/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Enable direct access to Ask UI functionality from the DeepWiki home page by creating a new section that embeds the existing Ask.tsx component. Users can select repositories from the existing ProcessedProjects or via RepositorySelector, then ask questions without navigating to individual repository pages. The implementation reuses existing components and follows the current Next.js App Router structure.

## Technical Context
**Language/Version**: TypeScript with Next.js 15.3.1 (App Router), React 19, Node.js 20+  
**Primary Dependencies**: Existing Ask.tsx, RepositorySelector.tsx, MultiRepositorySelector.tsx, useProcessedProjects hook  
**Storage**: Browser localStorage for repository configurations, existing API endpoints for Ask functionality  
**Testing**: Jest/Testing Library for React components, existing test infrastructure  
**Target Platform**: Web browsers (modern browsers supporting ES2020+)
**Project Type**: web (frontend modification of existing Next.js app)  
**Performance Goals**: <100ms UI response time, maintain existing Ask UI performance  
**Constraints**: No breaking changes to existing functionality, reuse existing components and patterns, follow current app structure  
**Scale/Scope**: Modify existing src/app/page.tsx, create 1-2 new components, integrate with existing component ecosystem

**User-Provided Technical Details**: Utilize the Ask.tsx and existing frontend tech stack. Do not make the deepwiki break when implement the new feature.

**Current Architecture Analysis**:
- **Frontend Structure**: Next.js 15.3.1 App Router (`src/app/`), React 19, TypeScript, Tailwind CSS with custom properties
- **Home page**: `src/app/page.tsx` (319 lines) with repository input form, demo sections, processed projects integration
- **Ask component**: `src/components/Ask.tsx` (159 lines, full-featured with multi-repository support)
- **Repository selection**: `src/components/RepositorySelector.tsx`, `src/components/MultiRepositorySelector.tsx`
- **Current Ask usage**: Repository pages (`src/app/[owner]/[repo]/page.tsx`) via floating button + modal
- **API Integration**: WebSocket primary (`ws://localhost:8001/api/ws/chat`), HTTP fallback (`/api/chat/stream`)
- **Backend**: FastAPI on port 8001 with endpoints `/api/chat/completions/stream`, `/api/ws/chat`
- **Data flow**: Ask.tsx → websocketClient.ts → Backend FastAPI → AI models
- **Multi-repository support**: Already implemented in Ask.tsx with proper request format
- Projects hook: `src/hooks/useProcessedProjects.ts` provides processed repository list
- Layout structure: Uses Tailwind CSS with CSS variables for theming

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 1 (frontend modification only)
- Using framework directly? Yes (Next.js/React directly, no wrapper classes)
- Single data model? Yes (repository context, existing models)
- Avoiding patterns? Yes (direct component composition, no unnecessary abstractions)

**Architecture**:
- EVERY feature as library? N/A (UI component modification)
- Libraries listed: Reusing existing Ask.tsx, RepositorySelector.tsx components
- CLI per library: N/A (frontend-only feature)
- Library docs: N/A (component documentation via JSDoc)

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? Yes (component tests first)
- Git commits show tests before implementation? Will enforce
- Order: Contract→Integration→E2E→Unit strictly followed? Yes
- Real dependencies used? Yes (actual React components, real API calls)
- Integration tests for: component integration, repository selection, Ask UI embedding
- FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:
- Structured logging included? Yes (existing console logging, error boundaries)
- Frontend logs → backend? Yes (existing error reporting)
- Error context sufficient? Yes (React error boundaries, user feedback)

**Versioning**:
- Version number assigned? Will increment BUILD version
- BUILD increments on every change? Yes
- Breaking changes handled? No breaking changes (additive only)

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure]
```

**Structure Decision**: Web application (Option 2) - frontend modifications within existing Next.js structure

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - HomePageAsk component interface and props
   - Repository selection state management
   - Integration points with existing Ask.tsx
   - User interaction flow and state transitions

2. **Generate API contracts** from functional requirements:
   - Component interfaces (HomePageAsk, integration with Ask.tsx)
   - Props and callback interfaces
   - TypeScript type definitions
   - Component composition patterns

3. **Generate contract tests** from contracts:
   - Component integration tests (HomePageAsk + Ask.tsx)
   - Repository selection functionality tests
   - API communication tests
   - Tests must fail initially (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Home page integration test scenario
   - Repository selection user flow
   - Ask functionality embedding scenario
   - Multi-repository conversation testing

5. **Update agent file incrementally** (O(1) operation):
   - Run `/scripts/update-agent-context.sh [claude|gemini|copilot]` for your AI assistant
   - Add React/Next.js patterns, component composition approach
   - Update with Ask.tsx integration patterns and WebSocket communication
   - Keep focused on frontend component integration
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing component tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Focus on modifying existing `src/app/page.tsx` to add Ask UI section
- Create HomePageAsk component in `src/components/HomePageAsk.tsx`
- Integrate with existing components: Ask.tsx, RepositorySelector.tsx, MultiRepositorySelector.tsx
- Add tests following existing test patterns in the codebase
- Each contract requirement → component test task [P]
- Each user story → integration test task

**Ordering Strategy**:
- TDD order: Tests before implementation 
- Dependency order: 
  1. Component test setup for HomePageAsk
  2. HomePageAsk component tests (failing)
  3. HomePageAsk component implementation
  4. Home page integration tests
  5. Modify `src/app/page.tsx` to include Ask section
  6. Integration testing with existing Ask.tsx
  7. End-to-end validation
- Mark [P] for parallel execution (independent files)

**File-Specific Tasks**:
- **src/components/HomePageAsk.tsx**: New component to wrap Ask with repository selection
- **src/components/HomePageAsk.test.tsx**: Component tests
- **src/app/page.tsx**: Add Ask section between repository form and demo charts
- **src/app/page.test.tsx**: Integration tests for home page modifications

**Estimated Output**: 8-12 numbered, ordered tasks in tasks.md covering:
- Component test creation (2-3 tasks)
- Component implementation (2-3 tasks) 
- Home page integration (2-3 tasks)
- Testing and validation (2-3 tasks)

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

No constitutional violations identified. The implementation follows all constitutional principles:
- Simple component architecture (reusing existing components)
- Direct framework usage (Next.js/React without wrappers)  
- TDD approach enforced
- Non-breaking additive changes only
- Single web project structure maintained


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - Architecture analysis complete
- [x] Phase 1: Design complete (/plan command) - Ready for /tasks command
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS  
- [x] All NEEDS CLARIFICATION resolved: Full codebase architecture analyzed
- [x] Technical Context complete: Ask.tsx integration patterns identified
- [x] API Integration verified: WebSocket + HTTP fallback architecture confirmed
- [x] Component ecosystem mapped: Ask.tsx, Repository selectors, processed projects
- [x] Complexity deviations documented (none)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*