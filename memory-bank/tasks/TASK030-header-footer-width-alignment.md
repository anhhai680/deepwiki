# [TASK030] - Header and Footer Full Width Alignment with Body Content

**Status:** Pending  
**Added:** September 6, 2025  
**Updated:** September 6, 2025

## Original Request
Create task to display header and footer of DeepWiki full wide aligns with body content.

## Thought Process
Currently, there's an inconsistency in the layout width constraints between different pages in the DeepWiki application:

1. **Home Page (`src/app/page.tsx`)**: 
   - Header: Uses `max-w-7xl` (equivalent to 1280px)
   - Footer: Uses `max-w-7xl` (equivalent to 1280px)
   - Main Content: Uses `w-96` for sidebar and flexible main area

2. **Repository Page (`src/app/[owner]/[repo]/page.tsx`)**:
   - Header: Uses `max-w-[90%] xl:max-w-[1400px]`
   - Main: Uses `max-w-[90%] xl:max-w-[1400px]`
   - Footer: Uses `max-w-[90%] xl:max-w-[1400px]`

This inconsistency creates a visual misalignment where the header and footer widths don't match across different pages. To create a cohesive user experience, we need to standardize the maximum width constraints across all pages while ensuring the content remains properly aligned.

The better approach would be to:
1. Use a consistent maximum width across all pages
2. Ensure header, main content, and footer all align perfectly
3. Maintain responsive behavior on smaller screens
4. Consider the optimal reading width for content

Based on the repository page's approach of `max-w-[90%] xl:max-w-[1400px]`, this seems to provide better space utilization on larger screens while maintaining readability.

## Implementation Plan
- [ ] **1. Analyze Current Layout Structure** 
  - [ ] 1.1 Review home page layout constraints
  - [ ] 1.2 Review repository page layout constraints  
  - [ ] 1.3 Document the differences and visual impact
  
- [ ] **2. Standardize Width Constraints**
  - [ ] 2.1 Update home page header to use consistent max-width
  - [ ] 2.2 Update home page footer to use consistent max-width
  - [ ] 2.3 Ensure main content area aligns with header/footer
  
- [ ] **3. Test Responsive Behavior**
  - [ ] 3.1 Verify alignment on mobile devices (320px-768px)
  - [ ] 3.2 Verify alignment on tablet devices (768px-1024px)
  - [ ] 3.3 Verify alignment on desktop devices (1024px+)
  - [ ] 3.4 Verify alignment on large screens (1400px+)
  
- [ ] **4. Cross-Page Consistency Check**
  - [ ] 4.1 Compare home page and repository page alignment
  - [ ] 4.2 Ensure visual consistency across all page types
  - [ ] 4.3 Test navigation between pages for smooth visual transition

## Progress Tracking

**Overall Status:** Not Started - 0%

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | Review home page layout constraints | Not Started | 2025-09-06 | Current: max-w-7xl for header/footer |
| 1.2 | Review repository page layout constraints | Not Started | 2025-09-06 | Current: max-w-[90%] xl:max-w-[1400px] |
| 1.3 | Document differences and visual impact | Not Started | 2025-09-06 | Inconsistent width creates misalignment |
| 2.1 | Update home page header width constraint | Not Started | 2025-09-06 | Target: max-w-[90%] xl:max-w-[1400px] |
| 2.2 | Update home page footer width constraint | Not Started | 2025-09-06 | Target: max-w-[90%] xl:max-w-[1400px] |
| 2.3 | Align main content area with header/footer | Not Started | 2025-09-06 | Ensure sidebar and content align properly |
| 3.1 | Test mobile responsiveness (320px-768px) | Not Started | 2025-09-06 | Verify 90% width works on mobile |
| 3.2 | Test tablet responsiveness (768px-1024px) | Not Started | 2025-09-06 | Verify responsive behavior |
| 3.3 | Test desktop responsiveness (1024px+) | Not Started | 2025-09-06 | Verify max-width constraint |
| 3.4 | Test large screen responsiveness (1400px+) | Not Started | 2025-09-06 | Verify 1400px max constraint |
| 4.1 | Cross-page alignment verification | Not Started | 2025-09-06 | Home page vs repository page |
| 4.2 | Visual consistency validation | Not Started | 2025-09-06 | Ensure seamless user experience |
| 4.3 | Navigation transition testing | Not Started | 2025-09-06 | Smooth visual flow between pages |

## Progress Log
### September 6, 2025 - Initial Task Creation
- Created task to address header and footer alignment inconsistency
- Identified the root cause: different max-width constraints between home page (max-w-7xl) and repository page (max-w-[90%] xl:max-w-[1400px])
- Documented current state and implementation approach
- Set target to use repository page's width constraints as the standard due to better space utilization
- Outlined comprehensive testing plan for responsive behavior across all device sizes

## Technical Notes
- **Current Home Page**: `max-w-7xl` = 1280px maximum width
- **Current Repository Page**: `max-w-[90%] xl:max-w-[1400px]` = 90% width up to 1400px maximum
- **Target Approach**: Standardize on `max-w-[90%] xl:max-w-[1400px]` for better space utilization
- **Key Files**: 
  - `/src/app/page.tsx` (home page header and footer)
  - `/src/app/[owner]/[repo]/page.tsx` (repository page - reference implementation)

## Acceptance Criteria
- [ ] Header, main content, and footer widths are consistent across all pages
- [ ] Layout maintains responsive behavior on all device sizes
- [ ] Visual alignment is perfect when navigating between pages
- [ ] No horizontal scrolling issues introduced
- [ ] Content remains readable and well-structured
