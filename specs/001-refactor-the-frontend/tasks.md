# Tasks: Frontend Code Refactoring for Maintainability

**Input**: Design documents from `/Volumes/Data/Projects/AI/projects/deepwiki/specs/001-refactor-the-frontend/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
   → Tech stack: TypeScript, React 19, Next.js 15.3.1
   → Structure: Web app with frontend/backend separation
2. Load optional design documents ✓
   → data-model.md: 5 type categories extracted
   → contracts/: ask-component.md, repository-page.md
   → research.md: Component splitting strategies defined
3. Generate tasks by category:
   → Setup: TypeScript modules, shared utilities
   → Tests: Component behavior preservation tests
   → Core: Extract utilities, hooks, types, refactor components
   → Integration: Ensure all components work together
   → Polish: Bundle optimization, documentation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same component file = sequential (preservation critical)
   → Preserve behavior before refactoring (modified TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness ✓
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
**Web app**: Frontend at `src/`, Backend at `backend/src/` (existing structure maintained)

## Phase 3.1: Setup and Foundation
- [ ] T001 Create shared type definitions structure in `src/types/`
- [ ] T002 [P] Initialize shared utilities directory `src/utils/shared/`
- [ ] T003 [P] Initialize shared hooks directory `src/hooks/shared/`
- [ ] T004 [P] Initialize shared constants directory `src/constants/shared/`

## Phase 3.2: Behavior Preservation Tests (MUST COMPLETE BEFORE REFACTORING) ⚠️
**CRITICAL: These tests MUST validate existing functionality before ANY refactoring**
- [ ] T005 [P] Create component behavior test for Ask component in `src/tests/Ask.behavior.test.tsx`
- [ ] T006 [P] Create component behavior test for Repository page in `src/tests/RepositoryPage.behavior.test.tsx`
- [ ] T007 [P] Create component behavior test for Mermaid component in `src/tests/Mermaid.behavior.test.tsx`
- [ ] T008 [P] Create component behavior test for Home page in `src/tests/HomePage.behavior.test.tsx`
- [ ] T009 [P] Create component behavior test for UserSelector in `src/tests/UserSelector.behavior.test.tsx`
- [ ] T010 [P] Create component behavior test for Slides page in `src/tests/SlidesPage.behavior.test.tsx`
- [ ] T011 [P] Create component behavior test for Workshop page in `src/tests/WorkshopPage.behavior.test.tsx`

## Phase 3.3: Extract Shared Modules (ONLY after behavior tests pass)
- [ ] T012 [P] Extract Chat & AI Model types to `src/types/chat.ts`
- [ ] T013 [P] Extract Wiki Content types to `src/types/wiki.ts`
- [ ] T014 [P] Extract Repository & Project types to `src/types/repository.ts`
- [ ] T015 [P] Extract Component Props types to `src/types/components.ts`
- [ ] T016 [P] Extract Mermaid Diagram types to `src/types/diagrams.ts`
- [ ] T017 [P] Create consolidated type exports in `src/types/index.ts`
- [ ] T018 [P] Extract WebSocket utilities to `src/utils/shared/websocket.ts`
- [ ] T019 [P] Extract URL processing utilities to `src/utils/shared/urlUtils.ts`
- [ ] T020 [P] Extract validation utilities to `src/utils/shared/validation.ts`
- [ ] T021 [P] Extract Mermaid theme configuration to `src/constants/shared/mermaidThemes.ts`

## Phase 3.4: Component Refactoring - Ask Component (Sequential due to same file)
- [ ] T022 Extract chat message utilities from `src/components/Ask.tsx` to `src/utils/chat/messageUtils.ts`
- [ ] T023 Extract model selection logic from `src/components/Ask.tsx` to `src/hooks/chat/useModelSelection.ts`
- [ ] T024 Extract WebSocket chat logic from `src/components/Ask.tsx` to `src/hooks/chat/useChatWebSocket.ts`
- [ ] T025 Extract multi-repository handling from `src/components/Ask.tsx` to `src/hooks/chat/useMultiRepository.ts`
- [ ] T026 Create ChatMessage component in `src/components/chat/ChatMessage.tsx`
- [ ] T027 Create ModelSelector component in `src/components/chat/ModelSelector.tsx`
- [ ] T028 Create RepositoryContext component in `src/components/chat/RepositoryContext.tsx`
- [ ] T029 Refactor main Ask component to use extracted modules (preserve all props/behavior)
- [ ] T030 Validate Ask component behavior test still passes

## Phase 3.5: Component Refactoring - Repository Page (Sequential due to same file)
- [ ] T031 Extract wiki navigation utilities from `src/app/[owner]/[repo]/page.tsx` to `src/utils/wiki/navigationUtils.ts`
- [ ] T032 Extract repository metadata logic from `src/app/[owner]/[repo]/page.tsx` to `src/hooks/wiki/useRepositoryMetadata.ts`
- [ ] T033 Extract wiki content management from `src/app/[owner]/[repo]/page.tsx` to `src/hooks/wiki/useWikiContent.ts`
- [ ] T034 Create RepositoryHeader component in `src/components/wiki/RepositoryHeader.tsx`
- [ ] T035 Create WikiNavigation component in `src/components/wiki/WikiNavigation.tsx`
- [ ] T036 Create WikiContentArea component in `src/components/wiki/WikiContentArea.tsx`
- [ ] T037 Create ExportControls component in `src/components/wiki/ExportControls.tsx`
- [ ] T038 Refactor repository page to use extracted layout components (preserve all functionality)
- [ ] T039 Validate Repository page behavior test still passes

## Phase 3.6: Component Refactoring - Mermaid Component (Sequential due to same file)
- [ ] T040 Extract Mermaid configuration logic from `src/components/Mermaid.tsx` to `src/utils/diagrams/mermaidConfig.ts`
- [ ] T041 Extract diagram rendering utilities from `src/components/Mermaid.tsx` to `src/utils/diagrams/renderingUtils.ts`
- [ ] T042 Create DiagramRenderer component in `src/components/diagrams/DiagramRenderer.tsx`
- [ ] T043 Create DiagramControls component in `src/components/diagrams/DiagramControls.tsx`
- [ ] T044 Refactor main Mermaid component to use extracted modules (preserve all props/behavior)
- [ ] T045 Validate Mermaid component behavior test still passes

## Phase 3.7: Component Refactoring - Home Page (Sequential due to same file)
- [ ] T046 Extract repository form logic from `src/app/page.tsx` to `src/hooks/home/useRepositoryForm.ts`
- [ ] T047 Extract project management from `src/app/page.tsx` to `src/hooks/home/useProjectManagement.ts`
- [ ] T048 Create RepositoryForm component in `src/components/home/RepositoryForm.tsx`
- [ ] T049 Create ProjectsOverview component in `src/components/home/ProjectsOverview.tsx`
- [ ] T050 Create HomePageLayout component in `src/components/home/HomePageLayout.tsx`
- [ ] T051 Refactor home page to use extracted components (preserve all functionality)
- [ ] T052 Validate Home page behavior test still passes

## Phase 3.8: Component Refactoring - Remaining Large Components (Parallel per component)
- [ ] T053 [P] Extract user/model selection logic from `src/components/UserSelector.tsx` to `src/hooks/config/useUserSelection.ts`
- [ ] T054 [P] Extract slides presentation logic from `src/app/[owner]/[repo]/slides/page.tsx` to `src/hooks/presentation/useSlidePresentation.ts`
- [ ] T055 [P] Extract workshop logic from `src/app/[owner]/[repo]/workshop/page.tsx` to `src/hooks/workshop/useWorkshopMode.ts`
- [ ] T056 [P] Refactor UserSelector component to use extracted logic (preserve all props/behavior)
- [ ] T057 [P] Refactor Slides page to use extracted logic (preserve all functionality)
- [ ] T058 [P] Refactor Workshop page to use extracted logic (preserve all functionality)
- [ ] T059 [P] Validate UserSelector behavior test still passes
- [ ] T060 [P] Validate Slides page behavior test still passes
- [ ] T061 [P] Validate Workshop page behavior test still passes

## Phase 3.9: Integration and Backward Compatibility
- [ ] T062 Add re-export statements to maintain existing import paths
- [ ] T063 Update all internal imports to use new modular structure
- [ ] T064 Create index files for clean public APIs in each module directory
- [ ] T065 Run full application integration test following quickstart.md
- [ ] T066 Verify no TypeScript compilation errors
- [ ] T067 Verify no ESLint warnings introduced

## Phase 3.10: Optimization and Polish
- [ ] T068 [P] Analyze bundle size impact and optimize imports
- [ ] T069 [P] Add JSDoc documentation to all extracted utilities and hooks
- [ ] T070 [P] Update component documentation with new architecture
- [ ] T071 [P] Create migration guide for future developers
- [ ] T072 Remove any unused code and consolidate duplicates
- [ ] T073 Run performance validation tests
- [ ] T074 Final validation: all behavior tests pass and file sizes under 500 lines

## Dependencies
- **Setup (T001-T004)** before all other phases
- **Behavior Tests (T005-T011)** before any refactoring (T012+)
- **Shared Modules (T012-T021)** before component refactoring (T022+)
- **Component Refactoring** phases are sequential within each component but parallel between components:
  - Ask Component (T022-T030) sequential internally
  - Repository Page (T031-T039) sequential internally  
  - Mermaid Component (T040-T045) sequential internally
  - Home Page (T046-T052) sequential internally
  - Remaining Components (T053-T061) can run parallel
- **Integration (T062-T067)** after all component refactoring
- **Polish (T068-T074)** after integration complete

## Parallel Execution Examples

### Phase 3.2: Behavior Tests (All Parallel)
```bash
# Launch T005-T011 together:
Task: "Create component behavior test for Ask component in src/tests/Ask.behavior.test.tsx"
Task: "Create component behavior test for Repository page in src/tests/RepositoryPage.behavior.test.tsx"
Task: "Create component behavior test for Mermaid component in src/tests/Mermaid.behavior.test.tsx"
Task: "Create component behavior test for Home page in src/tests/HomePage.behavior.test.tsx"
Task: "Create component behavior test for UserSelector in src/tests/UserSelector.behavior.test.tsx"
Task: "Create component behavior test for Slides page in src/tests/SlidesPage.behavior.test.tsx"
Task: "Create component behavior test for Workshop page in src/tests/WorkshopPage.behavior.test.tsx"
```

### Phase 3.3: Shared Module Extraction (All Parallel)
```bash
# Launch T012-T021 together:
Task: "Extract Chat & AI Model types to src/types/chat.ts"
Task: "Extract Wiki Content types to src/types/wiki.ts"
Task: "Extract Repository & Project types to src/types/repository.ts"
Task: "Extract Component Props types to src/types/components.ts"
Task: "Extract Mermaid Diagram types to src/types/diagrams.ts"
Task: "Extract WebSocket utilities to src/utils/shared/websocket.ts"
Task: "Extract URL processing utilities to src/utils/shared/urlUtils.ts"
Task: "Extract validation utilities to src/utils/shared/validation.ts"
Task: "Extract Mermaid theme configuration to src/constants/shared/mermaidThemes.ts"
```

### Phase 3.8: Remaining Components (Parallel per component)
```bash
# Launch T053, T054, T055 together (different components):
Task: "Extract user/model selection logic from src/components/UserSelector.tsx"
Task: "Extract slides presentation logic from src/app/[owner]/[repo]/slides/page.tsx"  
Task: "Extract workshop logic from src/app/[owner]/[repo]/workshop/page.tsx"
```

## Notes
- **[P] tasks** = different files/components, no dependencies
- **Behavior preservation** is critical - tests must pass before and after refactoring
- **Zero breaking changes** - all existing imports and usage patterns must continue working
- **File size target** - each refactored component must be under 500 lines
- Commit after completing each component refactoring phase
- Use backward compatibility re-exports during transition period

## Critical Success Criteria
1. All behavior tests pass before and after refactoring
2. No existing imports are broken (backward compatibility maintained)
3. All 7 critical files reduced to under 500 lines each
4. TypeScript compilation clean with no new errors
5. ESLint passes with no new warnings
6. Application functionality identical to pre-refactoring state
7. Bundle size maintained or improved
