# Tasks: Quick Access Ask UI from Home Page

**Input**: Design documents from `/specs/001-refactor-frontend-to/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → Tech stack: Next.js 15.3.1, React 19, TypeScript, Tailwind CSS
   → Structure: Frontend modifications within existing Next.js app
2. Load design documents:
   → data-model.md: HomePageAskState, RepositoryContext entities
   → contracts/: Component contracts for ExistingProjectsPanel, ChatPanel
   → research.md: Component reuse strategy, two-column layout approach
3. Generate tasks by category:
   → Setup: test infrastructure, component structure
   → Tests: component contract tests, integration tests
   → Core: ExistingProjectsPanel, ChatPanel, layout restructuring
   → Integration: Ask.tsx embedding, responsive behavior
   → Polish: unit tests, performance validation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Frontend Structure**: `src/app/`, `src/components/` at repository root
- Tests follow existing pattern in repository structure

## Phase 3.1: Setup
- [ ] T001 Verify existing test infrastructure for React components supports new component testing
- [ ] T002 Create component test structure for ExistingProjectsPanel and ChatPanel
- [ ] T003 [P] Configure TypeScript interfaces for two-column layout components

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T004 [P] Component contract test for ExistingProjectsPanel in `src/components/ExistingProjectsPanel.test.tsx`
- [ ] T005 [P] Component contract test for ChatPanel in `src/components/ChatPanel.test.tsx`
- [ ] T006 [P] Integration test for two-column home page layout in `src/app/page.test.tsx`
- [ ] T007 [P] Integration test for existing projects preservation in `src/app/page.test.tsx`
- [ ] T008 [P] Integration test for Ask.tsx embedding in ChatPanel in `src/components/ChatPanel.test.tsx`
- [ ] T009 [P] Responsive behavior test for mobile/desktop layout in `src/app/page.test.tsx`

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T010 [P] Extract ExistingProjectsPanel component from current home page in `src/components/ExistingProjectsPanel.tsx`
- [ ] T011 [P] Create ChatPanel component wrapper for Ask.tsx in `src/components/ChatPanel.tsx`
- [ ] T012 Restructure home page to two-column layout (40%/60%) in `src/app/page.tsx`
- [ ] T013 Integrate ExistingProjectsPanel into left column (40%) in `src/app/page.tsx`
- [ ] T014 Integrate ChatPanel into right column (60%) in `src/app/page.tsx`
- [ ] T015 Implement responsive behavior for mobile devices in `src/app/page.tsx`

## Phase 3.4: Integration
- [ ] T016 Connect ChatPanel with existing Ask.tsx component props and state management
- [ ] T017 Ensure repository selection from left column updates ChatPanel context
- [ ] T018 Preserve existing header and footer layout positioning
- [ ] T019 Verify existing processed projects integration with new layout

## Phase 3.5: Polish
- [ ] T020 [P] Unit tests for ExistingProjectsPanel repository search functionality in `src/components/ExistingProjectsPanel.test.tsx`
- [ ] T021 [P] Unit tests for ChatPanel Ask.tsx integration in `src/components/ChatPanel.test.tsx`
- [ ] T022 Performance validation: ensure <100ms UI response time for layout changes
- [ ] T023 [P] Verify no breaking changes to existing Ask.tsx functionality on repository pages
- [ ] T024 Cross-browser testing for two-column layout support
- [ ] T025 Run quickstart.md validation tests for complete feature verification

## Dependencies
- Tests (T004-T009) before implementation (T010-T015)
- T010 (ExistingProjectsPanel extraction) before T013 (left column integration)
- T011 (ChatPanel creation) before T014 (right column integration)
- T012 (layout restructuring) blocks T013, T014
- T016-T019 (integration) require T010-T015 complete
- Implementation before polish (T020-T025)

## Parallel Example
```bash
# Launch T004-T008 together (different test files):
Task: "Component contract test for ExistingProjectsPanel in src/components/ExistingProjectsPanel.test.tsx"
Task: "Component contract test for ChatPanel in src/components/ChatPanel.test.tsx"
Task: "Integration test for two-column layout in src/app/page.test.tsx"
Task: "Integration test for Ask.tsx embedding in src/components/ChatPanel.test.tsx"

# Launch T010-T011 together (different component files):
Task: "Extract ExistingProjectsPanel component in src/components/ExistingProjectsPanel.tsx"
Task: "Create ChatPanel component wrapper in src/components/ChatPanel.tsx"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing components
- Preserve all existing functionality during restructuring
- Maintain responsive design for mobile devices
- Header/footer layouts must remain unchanged
- Repository search and grid/list toggle functionality must be preserved
- Ask.tsx integration must maintain all existing features

## Task Generation Rules
- Each component contract → component test task [P]
- Each layout modification → integration test
- Different components → parallel implementation [P]
- Same file modifications → sequential execution
- Existing functionality preservation → validation tasks

## Key File Paths
- **Main Layout**: `src/app/page.tsx` (restructure to two-column)
- **Left Column**: `src/components/ExistingProjectsPanel.tsx` (extract existing projects section)
- **Right Column**: `src/components/ChatPanel.tsx` (Ask.tsx wrapper)
- **Tests**: `src/components/*.test.tsx`, `src/app/page.test.tsx`
- **Existing Components**: `src/components/Ask.tsx` (preserve unchanged)

## Success Criteria
- ✅ Two-column layout (40%/60%) implemented
- ✅ Existing projects section preserved in left column
- ✅ Ask.tsx embedded in right column, always visible
- ✅ All existing functionality maintained
- ✅ Responsive design works across devices
- ✅ No breaking changes to repository pages or Ask.tsx usage
- ✅ Performance goals met (<100ms UI response)
