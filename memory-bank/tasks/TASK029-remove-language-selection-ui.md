# [TASK029] - Remove Language Selection UI

**Status:** Pending  
**Added:** 2025-01-27  
**Updated:** 2025-01-27  
**Priority:** 🟡 Medium  
**Type:** Cleanup/Simplification  

## Original Request
Remove language selection on DeepWiki UI because we only support English language. Therefore, users does not need choosing the Language when generating or processing a repository.

## Thought Process
The current implementation includes a comprehensive language selection system with:
- Language context provider for multi-language support
- Language dropdown in ConfigurationModal
- API endpoints for supported languages configuration
- Browser language detection functionality
- Language preference storage in localStorage

However, since DeepWiki only supports English, this adds unnecessary complexity to the UI and user experience. Users should not be presented with language options when only one language is available.

### Current Language Implementation Analysis
1. **Frontend Components:**
   - `LanguageContext.tsx` - Context provider with full language switching logic
   - `ConfigurationModal.tsx` - Contains language selection dropdown
   - `page.tsx` - Uses selectedLanguage state and syncs with context
   - **Multiple components use `useLanguage` hook** - Found 12+ components importing it
   - Language switching functionality throughout the app

2. **Backend Components:**
   - `/api/lang/config` endpoint returning supported languages (inconsistent with actual config)
   - `backend/config/lang.json` - Contains only English support
   - Language configuration in various config files
   - Multi-language support in chat services and pipelines

3. **Language Files:**
   - Only `src/messages/en.json` exists, confirming single language support
   - `src/i18n.ts` defines only 'en' locale
   - **Inconsistency found**: API endpoint returns ["en", "vi"] but no vi.json exists

4. **Usage Analysis:**
   - **25+ files use `useLanguage` hook** - mostly for `messages` (translations)
   - **URL parameters**: Language passed in query strings to various routes
   - **Backend processing**: Language parameter used in chat services and wiki generation

### Approach Strategy
Since only English is supported, we should:
1. **Remove UI Language Selection** - Remove language dropdown from user interface
2. **Simplify Language Context** - Remove language switching UI logic, always default to English
3. **Keep Backend Unchanged** - Backend language processing works fine, no changes needed
4. **Maintain Internationalization Structure** - Keep the i18n framework and all existing functionality
5. **Remove User-Facing State Management** - Remove selectedLanguage state from UI components

## Implementation Plan

### Phase 1: Frontend Language Context Simplification
- **1.1** Simplify `LanguageContext.tsx` to always use English
  - Remove browser language detection (unnecessary complexity)
  - Remove localStorage language persistence (users can't change it anyway)
  - Remove setLanguage functionality from context (no switching needed)
  - Remove supportedLanguages state and API calls (not used in UI)
  - **KEEP**: Always load English messages and maintain hook interface
- **1.2** Update `useLanguage` hook interface
  - Remove setLanguage and supportedLanguages from return type
  - Keep only language ('en') and messages for compatibility
  - **CRITICAL**: 25+ components depend on this interface

### Phase 2: Remove Language Selection UI
- **2.1** Update `ConfigurationModal.tsx`
  - Remove language selection dropdown section
  - Remove selectedLanguage and setSelectedLanguage from props interface
  - Remove supportedLanguages from props interface
  - Update layout to remove language selection area
- **2.2** Update `page.tsx`
  - Remove selectedLanguage state
  - Remove setSelectedLanguage state setter
  - Remove language syncing useEffect
  - Remove language-related props passed to ConfigurationModal
  - **KEEP**: Pass 'en' directly to API calls instead of selectedLanguage

### Phase 3: Testing & Validation
- **3.1** Test application functionality
  - Verify English messages load correctly
  - Confirm no language-related errors
  - Test wiki generation and chat functionality
  - **ESSENTIAL**: Test all 25+ components using useLanguage
- **3.2** Update any related tests
  - Update component tests that reference language selection
  - Verify all existing functionality still works

### Phase 3: Backend Cleanup (Optional)
- **3.1** Fix `/api/lang/config` endpoint inconsistency
  - Currently returns ["en", "vi"] but only "en" is actually supported
  - Update to match `backend/config/lang.json` (only English)
  - **RISK ASSESSMENT**: Check if any external tools depend on this endpoint
- **3.2** Update language configuration
  - Verify `backend/config/lang.json` is correctly used
  - Update any remaining multi-language logic
  - **PRESERVE**: Backend language processing for future extensibility

### Phase 4: Testing & Validation
- **4.1** Test application functionality
  - Verify English messages load correctly
  - Confirm no language-related errors
  - Test wiki generation and chat functionality
- **4.2** Update any related tests
  - Update component tests that reference language selection
  - Verify backend tests still pass

## Progress Tracking

**Overall Status:** Not Started - 0%

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | Simplify LanguageContext.tsx | Not Started | 2025-01-27 | **UI ONLY**: Remove language switching UI logic |
| 1.2 | Update useLanguage hook interface | Not Started | 2025-01-27 | Remove setLanguage/supportedLanguages, keep language/messages |
| 2.1 | Remove language dropdown from ConfigurationModal | Not Started | 2025-01-27 | Clean up props interface and UI |
| 2.2 | Update page.tsx to remove language state | Not Started | 2025-01-27 | Remove selectedLanguage state, use 'en' directly |
| 3.1 | Test application functionality | Not Started | 2025-01-27 | **ESSENTIAL**: Test all 25+ components using useLanguage |
| 3.2 | Update related tests | Not Started | 2025-01-27 | Fix any broken tests due to interface changes |

## Technical Considerations

### Compatibility Requirements
- **Maintain i18n Structure:** Keep the messages system and basic i18n setup for potential future multi-language support
- **Non-Breaking Changes:** Ensure existing functionality continues to work
- **Clean Interface:** Remove language selection UI without affecting other configuration options

### Files to Modify
1. `src/contexts/LanguageContext.tsx` - Simplify to English-only (UI logic only)
2. `src/components/ConfigurationModal.tsx` - Remove language selection UI
3. `src/app/page.tsx` - Remove language state management
4. **NO BACKEND CHANGES** - Keep all backend language processing unchanged

### Critical Components Using Language (25+ files)
- **Components with `useLanguage`**: TokenInput, WikiTypeSelector, MultiRepositorySelector, ModelSelectionModal, RepositorySelector, ConfigurationModal, UserSelector, Ask, and 15+ more
- **Pages using language params**: All repo pages, workshop, slides  
- **API usage**: Chat services, wiki generation services - **KEEP UNCHANGED**

### Non-Breaking Requirements
1. **Maintain `useLanguage` hook interface** - Return `{ language: 'en', messages: {...} }`
2. **Preserve message loading system** - Keep English translations working
3. **Keep language parameter handling** - Backend still processes language='en' 
4. **Maintain URL compatibility** - Routes can still accept language params (defaulted to 'en')
5. **Preserve context provider structure** - Keep LanguageProvider for consistency
6. **NO BACKEND CHANGES** - All backend functionality remains exactly the same

### Risk Assessment & Critical Dependencies
**Critical Dependencies Found:**
1. **25+ Components** use `useLanguage` hook - primarily for `messages` object
2. **URL routing** includes language parameters in multiple pages  
3. **Backend services** process language parameter in chat and wiki generation - **KEEP UNCHANGED**
4. **API endpoints** return language config - **NO CHANGES NEEDED**

**Risk Levels:**
- **LOW Risk:** UI simplification (removing dropdown)
- **LOW Risk:** Context interface changes (maintaining compatibility)  
- **NO Risk:** Backend changes (none planned)
- **Guaranteed:** Backward compatibility maintained

### Risk Assessment
- **Low Risk:** Changes are primarily UI simplification
- **Backward Compatibility:** Maintain message loading system for consistency
- **Future Extensibility:** Keep core i18n structure for potential future expansion

## Success Criteria
1. ✅ Language selection dropdown removed from all UI components
2. ✅ Application defaults to English without user configuration
3. ✅ No language-related errors in console or application
4. ✅ Wiki generation and chat functionality work correctly (unchanged)
5. ✅ Simplified UI with reduced user confusion
6. ✅ All existing functionality preserved (no backend changes)
7. ✅ Core i18n structure maintained for future expansion

## Progress Log
### 2025-01-27
- Created task to remove language selection UI
- Analyzed current language implementation across frontend and backend
- **DISCOVERED CRITICAL DEPENDENCIES**: 25+ components use useLanguage hook
- **REFINED SCOPE**: Focus on UI-only changes, keep backend unchanged per user feedback
- **SIMPLIFIED APPROACH**: Remove confusing language selection without affecting functionality
- Developed implementation plan with frontend-only focus
- Updated task with UI-focused risk assessment and dependency analysis
- **ZERO BACKEND CHANGES**: All backend language processing remains exactly the same
- Set task as Pending status, ready for UI-only implementation
