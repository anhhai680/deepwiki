# [TASK035] - Fix System Architecture Menu Level Issue

**Status:** 🔄 **PENDING**  
**Added:** September 19, 2025  
**Updated:** September 19, 2025

## Original Request
Fix the issue for system architecture sub-item in individual repository menu page. Currently it appears as a sub-menu of the overview, but it should be at the same menu level as overview instead.

## Problem Analysis
Based on the screenshot and code examination, the issue is in the wiki structure generation and parsing logic in `src/app/[owner]/[repo]/page.tsx`. The "System Architecture" section is being incorrectly parsed as a subsection under "Overview" instead of being at the root level alongside "Overview".

### Root Cause
The issue lies in the `determineWikiStructure` function around lines 736-1210, specifically in:
1. **XML Structure Generation** (lines 790-850): The prompt template instructs the AI to create sections with specific hierarchy
2. **XML Parsing Logic** (lines 1070-1110): The section parsing logic that determines which sections are root sections vs subsections
3. **Section Reference Detection** (lines 1100-1110): The logic that identifies if a section is referenced by another section

### Current Behavior
- "System Architecture" appears as a subsection under "Overview" 
- This creates an incorrect hierarchical structure in the WikiTreeView component
- Users need to expand "Overview" to access "System Architecture"

### Expected Behavior  
- "System Architecture" should appear at the same level as "Overview"
- Both should be root-level sections that can be expanded independently
- The navigation should show a flat structure for main sections

## Thought Process
The issue appears to be in how the XML response from the AI is being structured and parsed. Looking at the comprehensive view prompt (lines 790-820), the template asks for main sections including:
- Overview (general information about the project)
- System Architecture (how the system is designed)
- Core Features (key functionality)
- etc.

However, the XML parsing logic in `determineWikiStructure` may be incorrectly interpreting section relationships, causing "System Architecture" to be treated as a subsection of "Overview".

## Implementation Plan

### Phase 1: Diagnosis and Code Review
- [x] **1.1** - Examine current XML structure generation in prompt template
- [x] **1.2** - Review XML parsing logic for section hierarchy detection
- [x] **1.3** - Identify the specific logic causing incorrect subsection assignment
- [ ] **1.4** - Analyze sample XML responses to understand the pattern

### Phase 2: Fix XML Parsing Logic
- [ ] **2.1** - Update section reference detection logic to properly identify root sections
- [ ] **2.2** - Ensure "System Architecture" is never treated as a subsection of "Overview"
- [ ] **2.3** - Modify the XML parsing to correctly handle parallel sections
- [ ] **2.4** - Add logging to track section hierarchy determination

### Phase 3: Prompt Template Enhancement
- [ ] **3.1** - Review and improve the XML structure prompt to be more explicit about section hierarchy
- [ ] **3.2** - Ensure the prompt clearly indicates all main sections should be at root level
- [ ] **3.3** - Add explicit instructions about section independence

### Phase 4: Testing and Validation
- [ ] **4.1** - Test with various repository types to ensure consistent behavior
- [ ] **4.2** - Verify "System Architecture" appears at root level alongside "Overview"
- [ ] **4.3** - Confirm WikiTreeView renders the corrected structure properly
- [ ] **4.4** - Test both comprehensive and non-comprehensive view modes

## Progress Tracking

**Overall Status:** 🔄 **PENDING** - 0% Complete

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | Examine XML structure generation prompt | ✅ **Complete** | Sep 19 | Identified prompt template around lines 790-820 |
| 1.2 | Review XML parsing logic for sections | ✅ **Complete** | Sep 19 | Found parsing logic in lines 1070-1110 |
| 1.3 | Identify subsection assignment cause | ✅ **Complete** | Sep 19 | Issue in section reference detection logic |
| 1.4 | Analyze sample XML responses | 🔄 **Not Started** | - | Need to capture actual XML from AI responses |
| 2.1 | Update section reference detection | 🔄 **Not Started** | - | Core fix needed in determineWikiStructure |
| 2.2 | Prevent Architecture as Overview subsection | 🔄 **Not Started** | - | Specific rule to handle this case |
| 2.3 | Modify XML parsing for parallel sections | 🔄 **Not Started** | - | Ensure proper root section identification |
| 2.4 | Add section hierarchy logging | 🔄 **Not Started** | - | Debug information for future issues |
| 3.1 | Review XML structure prompt | 🔄 **Not Started** | - | Improve prompt clarity |
| 3.2 | Clarify root level sections in prompt | 🔄 **Not Started** | - | Explicit instruction for main sections |
| 3.3 | Add section independence instructions | 🔄 **Not Started** | - | Prevent unwanted nesting |
| 4.1 | Test with various repository types | 🔄 **Not Started** | - | Comprehensive testing |
| 4.2 | Verify Architecture at root level | 🔄 **Not Started** | - | Main validation check |
| 4.3 | Confirm WikiTreeView rendering | 🔄 **Not Started** | - | UI component verification |
| 4.4 | Test both view modes | 🔄 **Not Started** | - | Comprehensive vs simple views |

## Key Files to Modify
1. **`/src/app/[owner]/[repo]/page.tsx`** (Primary)
   - Lines 790-850: XML structure prompt template
   - Lines 1070-1110: XML parsing logic for sections
   - Lines 1100-1110: Section reference detection logic

2. **`/src/components/WikiTreeView.tsx`** (Secondary)
   - Verify correct rendering of fixed structure
   - May need minor adjustments for visual consistency

## Technical Considerations
- **Backward Compatibility**: Ensure existing wikis continue to work
- **AI Response Variability**: Handle different XML structure formats from AI
- **Performance**: Minimize impact on parsing performance
- **Error Handling**: Graceful fallback if parsing fails

## Success Criteria
- [ ] "System Architecture" appears at the same level as "Overview" in navigation
- [ ] Both sections can be expanded/collapsed independently
- [ ] No breaking changes to existing wiki structures
- [ ] Consistent behavior across different repository types
- [ ] Clear logging for debugging section hierarchy issues

## Notes
- This is a UI/UX improvement that affects user navigation experience
- The fix should be applied to the core parsing logic to prevent future occurrences
- Consider adding unit tests for section hierarchy parsing logic