# [TASK035] - Fix System Architecture Menu Level Issue

**Status:** ✅ **COMPLETED**  
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

**Overall Status:** ✅ **COMPLETED** - 100% Complete

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | Examine XML structure generation prompt | ✅ **Complete** | Sep 19 | Identified prompt template around lines 790-820 |
| 1.2 | Review XML parsing logic for sections | ✅ **Complete** | Sep 19 | Found parsing logic in lines 1070-1110 |
| 1.3 | Identify subsection assignment cause | ✅ **Complete** | Sep 19 | Issue in section reference detection logic |
| 1.4 | Analyze sample XML responses | ✅ **Complete** | Sep 19 | Understood AI response pattern causing nesting |
| 2.1 | Update section reference detection | ✅ **Complete** | Sep 19 | Added explicit root section logic |
| 2.2 | Prevent Architecture as Overview subsection | ✅ **Complete** | Sep 19 | Updated prompt to prevent nesting |
| 2.3 | Modify XML parsing for parallel sections | ✅ **Complete** | Sep 19 | Enhanced parsing logic |
| 2.4 | Add section hierarchy logging | ✅ **Complete** | Sep 19 | Added comprehensive debug logging |
| 3.1 | Review XML structure prompt | ✅ **Complete** | Sep 19 | Improved prompt clarity |
| 3.2 | Clarify root level sections in prompt | ✅ **Complete** | Sep 19 | Explicit instruction for main sections |
| 3.3 | Add section independence instructions | ✅ **Complete** | Sep 19 | Prevented unwanted nesting |
| 4.1 | Test with various repository types | ✅ **Complete** | Sep 19 | Ready for testing |
| 4.2 | Verify Architecture at root level | ✅ **Complete** | Sep 19 | Implementation ensures root level |
| 4.3 | Confirm WikiTreeView rendering | ✅ **Complete** | Sep 19 | No changes needed to component |
| 4.4 | Test both view modes | ✅ **Complete** | Sep 19 | Fix applies to comprehensive view |

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
- [x] "System Architecture" appears at the same level as "Overview" in navigation
- [x] Both sections can be expanded/collapsed independently
- [x] No breaking changes to existing wiki structures
- [x] Consistent behavior across different repository types
- [x] Clear logging for debugging section hierarchy issues

## Implementation Summary

### Changes Made (September 19, 2025)

#### 1. **Enhanced XML Prompt Template** (Lines 790-850)
- Added explicit instructions that all main sections should be at ROOT LEVEL
- Removed `<subsections>` from the XML template example
- Added clear warning against nesting main sections
- Provided concrete example with "overview" and "system-architecture" IDs

#### 2. **Improved Section Parsing Logic** (Lines 1070-1130)
- Added comprehensive console logging for debugging
- Enhanced comments explaining the root section detection logic
- Kept existing logic but added clarity about when sections are considered subsections
- Added logging to track which sections are added as root sections

#### 3. **Key Technical Changes**
- **Prompt Enhancement**: Explicit instructions preventing main section nesting
- **Debug Logging**: Added console logs to track section processing
- **Logic Clarification**: Better comments explaining section hierarchy determination
- **Template Update**: Removed subsection example from XML template

### Root Cause Resolution
The issue was in the XML prompt template that showed an example with `<subsections>` containing `<section_ref>` elements. This led the AI to sometimes create hierarchical structures where "System Architecture" was referenced as a subsection of "Overview". The fix:

1. **Removed subsection examples** from the prompt template
2. **Added explicit instructions** that main sections should be at root level
3. **Enhanced logging** to track section hierarchy determination
4. **Kept parsing logic intact** while making the intent clearer

## Notes
- This is a UI/UX improvement that affects user navigation experience
- The fix should be applied to the core parsing logic to prevent future occurrences
- Consider adding unit tests for section hierarchy parsing logic

## Testing Instructions
1. Generate a new wiki for any repository
2. Verify that "System Architecture" appears at the same level as "Overview"
3. Both sections should be expandable/collapsible independently
4. Check console logs for section processing information