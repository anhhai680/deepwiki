# TASK034 - Update Private Model Configuration to Use Environment Variable

**Status:** 🔄 **PENDING**  
**Added:** September 12, 2025  
**Updated:** September 12, 2025  
**Priority:** 🟡 Medium  
**Phase:** Configuration Enhancement  

## Original Request
Create a task to use `PRIVATE_MODEL_BASE_URL` from environment setting instead of `base_url` in generator.json for Private Model.

## Problem Analysis
Currently, the privatemodel provider in `backend/config/generator.json` has a hardcoded `url_base` field:

```json
"privatemodel": {
  "client_class": "PrivateModelGenerator",
  "default_model": "GPT-4o-mini",
  "url_base": "https://aiportalapi.stu-platform.live/jpe",
  "supportsCustomModel": true,
  "models": {
    "GPT-4o-mini": {
      "temperature": 0.7,
      "top_p": 0.8
    }
  }
}
```

However, the `.env` file already contains the `PRIVATE_MODEL_BASE_URL` environment variable:
```
PRIVATE_MODEL_BASE_URL=https://aiportalapi.stu-platform.live/jpe
```

This creates a configuration inconsistency where the URL is defined in two places, and the environment variable is not being used.

## Implementation Plan

### Phase 1: Configuration File Update
1. **Remove hardcoded URL from generator.json**
   - Remove the `url_base` field from the privatemodel provider configuration
   - Ensure the configuration remains valid without hardcoded URL

### Phase 2: Code Implementation Update
2. **Update PrivateModelGenerator class**
   - Locate the PrivateModelGenerator implementation
   - Modify it to read `PRIVATE_MODEL_BASE_URL` from environment variables
   - Add proper error handling for missing environment variable
   - Ensure backward compatibility if needed

### Phase 3: Validation and Testing
3. **Test the changes**
   - Verify that the private model provider works with environment variable
   - Test error handling when environment variable is missing
   - Confirm no regression in existing functionality

## Progress Tracking

**Overall Status:** Not Started - 0%

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 34.1 | Remove url_base from generator.json privatemodel config | Not Started | - | Keep other config intact |
| 34.2 | Locate PrivateModelGenerator implementation | Not Started | - | Find the actual class file |
| 34.3 | Update PrivateModelGenerator to use env variable | Not Started | - | Use PRIVATE_MODEL_BASE_URL |
| 34.4 | Add error handling for missing env variable | Not Started | - | Graceful fallback or clear error |
| 34.5 | Test private model functionality | Not Started | - | Verify end-to-end operation |
| 34.6 | Update documentation if needed | Not Started | - | Document env variable requirement |

## Technical Considerations

### Environment Variable Handling
- Use standard Python `os.environ.get()` with appropriate default/error handling
- Consider using the existing environment configuration patterns in the codebase
- Ensure the change is consistent with how other providers handle configuration

### Error Handling Strategy
- Provide clear error message if `PRIVATE_MODEL_BASE_URL` is not set
- Consider whether to fall back to a default URL or fail fast
- Log configuration loading for debugging purposes

### Testing Strategy
- Test with environment variable set correctly
- Test with missing environment variable
- Test with malformed URL in environment variable
- Verify integration with existing private model functionality

## Expected Files to Modify
1. `backend/config/generator.json` - Remove hardcoded url_base
2. Backend PrivateModelGenerator class (location TBD)
3. Potentially environment loading/validation code

## Success Criteria
- ✅ Private model provider reads URL from `PRIVATE_MODEL_BASE_URL` environment variable
- ✅ Configuration is no longer duplicated between files
- ✅ Proper error handling when environment variable is missing
- ✅ No regression in existing private model functionality
- ✅ Code follows existing patterns for environment variable usage

## Progress Log
### September 12, 2025
- Task created with comprehensive analysis
- Identified the configuration inconsistency issue
- Developed implementation plan with clear phases
- Ready to begin implementation once prioritized