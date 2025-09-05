# [TASK028] - Fix Repository Selection Dropdown Not Appearing in Multi-Repository Mode

**Status:** Pending  
**Added:** September 5, 2025  
**Updated:** September 5, 2025

## Original Request
Create task to fix the repository selection does not appear the list of repository for selection when multi-repository mode enabled on home page as shown in screenshot.

## Problem Analysis
Based on the screenshot and code analysis, when multi-repository mode is enabled on the home page, the MultiRepositorySelector component is not displaying the dropdown list of available repositories. The user can see:

1. A search input field with "Search and select repositories..." placeholder
2. A dropdown chevron icon that should trigger the repository list
3. However, clicking the dropdown does not show the list of available processed repositories

## Root Cause Investigation
Several potential causes identified:

1. **Dropdown State Management**: The dropdown `isOpen` state might not be properly toggled when clicking the chevron button
2. **Projects Data**: The `projects` array passed to MultiRepositorySelector might be empty or not loaded
3. **Styling/Z-index Issues**: The dropdown might be rendered but hidden behind other elements
4. **Event Handler Issues**: Click events on the dropdown toggle might not be properly bound
5. **Filtering Logic**: The `availableProjects` filtering might be excluding all repositories

## Implementation Plan

### Phase 1: Debug Data Flow (30 minutes)
1. **Verify Projects Loading**
   - Add console logging in `useProcessedProjects` hook to check if projects are loaded
   - Verify the `/api/wiki/projects` endpoint is returning repository data
   - Check if the backend is running and accessible

2. **Debug MultiRepositorySelector Props**
   - Add console logging in MultiRepositorySelector to verify `projects` prop contains data
   - Log the `availableProjects` filtered array to ensure repositories are available

### Phase 2: Fix Dropdown Interaction (45 minutes)
3. **Investigate Dropdown Toggle**
   - Review the dropdown button click handler in MultiRepositorySelector
   - Ensure `isOpen` state is properly toggled when clicking the chevron
   - Add debugging logs to track dropdown state changes

4. **Fix Event Handlers**
   - Verify click events are properly bound to dropdown toggle button
   - Ensure the button is not disabled or blocked by other elements
   - Check for any event propagation issues

### Phase 3: UI/Styling Fixes (30 minutes)  
5. **Resolve Visual Issues**
   - Check CSS z-index values for dropdown menu positioning
   - Verify dropdown menu styling and visibility
   - Ensure dropdown doesn't get clipped by parent containers
   - Test responsive behavior

6. **Improve User Experience**
   - Add loading states while projects are being fetched
   - Show appropriate messages when no repositories are available
   - Ensure proper placeholder text and empty states

### Phase 4: Testing & Validation (15 minutes)
7. **Comprehensive Testing**
   - Test multi-repository mode toggle functionality
   - Verify repository selection and removal works correctly
   - Test manual URL input as fallback
   - Validate with different screen sizes and devices

## Expected Outcome
- Multi-repository mode dropdown shows list of available processed repositories
- Users can search and filter repositories in the dropdown
- Repository selection and removal works correctly
- Proper fallback behavior when no repositories are available
- Smooth user experience with appropriate loading and empty states

## Files to Modify
- `src/components/MultiRepositorySelector.tsx` - Main component with dropdown logic
- `src/hooks/useProcessedProjects.ts` - Data loading hook (if needed)
- `src/app/api/wiki/projects/route.ts` - Backend API route (if needed)
- Testing files as needed

## Progress Tracking

**Overall Status:** Not Started - 0%

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | Debug projects data loading and API connectivity | Not Started | | |
| 1.2 | Add console logging to MultiRepositorySelector component | Not Started | | |
| 2.1 | Investigate and fix dropdown toggle functionality | Not Started | | |
| 2.2 | Verify click event handlers and state management | Not Started | | |
| 3.1 | Fix dropdown styling and z-index issues | Not Started | | |
| 3.2 | Improve empty states and loading indicators | Not Started | | |
| 4.1 | Test complete multi-repository workflow | Not Started | | |
| 4.2 | Validate responsive behavior and edge cases | Not Started | | |

## Progress Log
### September 5, 2025
- Created task based on user screenshot showing repository selection dropdown not appearing
- Analyzed codebase and identified potential root causes
- Developed comprehensive debugging and fix plan
- Task ready for implementation with clear phases and expected outcomes
