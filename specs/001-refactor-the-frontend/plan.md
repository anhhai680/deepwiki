# Implementation Plan: Frontend Code Refactoring for Maintainability

**Branch**: `001-refactor-the-frontend` | **Date**: September 9, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Volumes/Data/Projects/AI/projects/deepwiki/specs/001-refactor-the-frontend/spec.md`

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
Refactor 7 critical oversized frontend files (533-2,357 lines each) into maintainable modules under 500 lines each while preserving all existing functionality. Focus on extracting shared utilities, custom hooks, type definitions, and separating concerns without breaking existing component interfaces or behavioral contracts.

## Technical Context
**Language/Version**: TypeScript with React 19, Next.js 15.3.1, Node.js 20+  
**Primary Dependencies**: Next.js (App Router), React 19, Tailwind CSS, Mermaid.js, React Icons  
**Storage**: Browser localStorage/sessionStorage, no database changes required  
**Testing**: Next.js built-in ESLint, TypeScript compiler, existing test suite (maintain coverage)  
**Target Platform**: Web browsers (modern ES2017+), SSR/SSG via Next.js  
**Project Type**: web - frontend React application with existing backend  
**Performance Goals**: Maintain current performance, reduce bundle size via better tree-shaking  
**Constraints**: Zero breaking changes to existing APIs, preserve all current functionality, maintain SEO  
**Scale/Scope**: 7 critical files (7,200+ lines), ~40 total frontend files, maintain existing user flows

**User Requirements Integration**: 
- DO NOT automatically change existing behaviors, business logic, or flows
- Ensure any changes won't break the current system
- Preserve all component interfaces and prop contracts
- Maintain backward compatibility with existing imports and usage patterns

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 1 (frontend refactoring only - backend unchanged)
- Using framework directly? YES (React/Next.js components, no unnecessary wrappers)
- Single data model? YES (existing TypeScript interfaces, consolidate duplicates)
- Avoiding patterns? YES (no over-engineering, simple module extraction)

**Architecture**:
- EVERY feature as library? N/A (refactoring existing code, not new features)
- Libraries listed: Component modules, utility modules, hook modules, type modules
- CLI per library: N/A (React components, not CLI libraries)
- Library docs: Component documentation via JSDoc/README

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? YES (existing tests must pass, new tests for extracted modules)
- Git commits show tests before implementation? YES (test existing functionality before refactoring)
- Order: Contract→Integration→E2E→Unit strictly followed? YES (preserve contracts, then refactor internals)
- Real dependencies used? YES (actual React components, not mocks)
- Integration tests for: Component interfaces, prop contracts, behavioral preservation
- FORBIDDEN: Breaking existing functionality, changing component APIs

**Observability**:
- Structured logging included? MAINTAIN EXISTING (preserve current error handling)
- Frontend logs → backend? MAINTAIN EXISTING (no changes to logging flow)
- Error context sufficient? YES (preserve error boundaries and handling)

**Versioning**:
- Version number assigned? NO CHANGE (refactoring only, no API changes)
- BUILD increments on every change? YES (standard development process)
- Breaking changes handled? NO BREAKING CHANGES ALLOWED (strict requirement)

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

**Structure Decision**: Option 2 (Web application - existing Next.js frontend with FastAPI backend)

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
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `/scripts/update-agent-context.sh [claude|gemini|copilot]` for your AI assistant
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Each critical file (7 total) → analysis + extraction + refactor task series
- Each shared module (types, utils, hooks) → creation task [P]
- Each component contract → validation test task
- Integration tasks to ensure all refactored components work together

**File-Specific Task Approach**:
1. **Repository Page (2,357 lines)**: 
   - Extract layout components, feature modules, API calls
   - Split into: RepoPageLayout, WikiDisplay, Navigation, Export logic
2. **Ask Component (1,062 lines)**:
   - Separate: ChatUI, ModelSelection, WebSocket logic, MultiRepo handling
3. **Mermaid Component (624 lines)**:
   - Extract: Theme configuration, Rendering engine, Configuration types
4. **Home Page (707 lines)**:
   - Split: RepositoryForm, ProjectsPanel, Configuration sections
5. **Slides/Workshop Pages**: Extract shared presentation logic

**Ordering Strategy**:
- **Phase 1**: Extract shared utilities and types first (low risk, foundation)
- **Phase 2**: Refactor individual components with contract preservation
- **Phase 3**: Integrate and test all refactored components together
- Mark [P] for parallel execution (independent extractions)
- Maintain backward compatibility throughout

**Risk Management**:
- Each task includes rollback plan
- Preserve existing functionality at every step
- Test component contracts after each major change
- Incremental commits with working states

**Estimated Output**: 35-40 numbered, ordered tasks in tasks.md
- 7 tasks for shared module extraction [P]
- 21 tasks for component refactoring (3 per major component)
- 7 tasks for contract validation
- 5 tasks for integration and cleanup

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS (no new violations introduced)
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented: NONE (refactoring maintains simplicity)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*