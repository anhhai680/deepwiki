# [TASK033] - Implement Private Model LLM Support

**Status:** Pending  
**Added:** September 11, 2025  
**Updated:** September 11, 2025

## Original Request
Implement privatemodel LLM functionality based on the existing `privatemodel` object in `generator.json`. The solution should support private model deployments with configurable endpoints and avoid hardcoding any environment settings in the codebase.

## Analysis of Current State

### Existing Configuration
The `privatemodel` provider is already defined in `backend/config/generator.json`:
```json
"privatemodel": {
  "client_class": "PrivateModelClient",
  "default_model": "custom-model",
  "url_base": "http://localhost:8000/v1",
  "supportsCustomModel": true,
  "models": {
    "custom-model": {
      "temperature": 0.7,
      "top_p": 0.8
    }
  }
}
```

### Missing Implementation
1. **PrivateModelClient class** - Referenced in config but doesn't exist
2. **Generator registration** - Not included in GeneratorManager or provider enums
3. **Configuration loading** - Not mapped in client_classes dictionary

### System Architecture Pattern
DeepWiki follows a consistent pattern for AI providers:
- **Generator classes** inherit from `BaseGenerator` (e.g., `OpenAIGenerator`, `AzureAIGenerator`)
- **Provider registration** in `GeneratorManager` with `ProviderType` enum
- **Configuration loading** through `load_generator_config()` with client_classes mapping
- **Environment-based settings** avoiding hardcoded values

## Implementation Plan

### Phase 1: Create PrivateModel Generator (Core Implementation)
- **1.1** Create `backend/components/generator/providers/private_model_generator.py`
  - Inherit from `BaseGenerator`
  - Implement OpenAI-compatible API interface
  - Support configurable base URL through environment variables
  - Handle custom authentication mechanisms
  
- **1.2** Implement required BaseGenerator methods:
  - `init_sync_client()` and `init_async_client()`
  - `convert_inputs_to_api_kwargs()`
  - `call()` and `acall()` for sync/async operations
  - `parse_chat_completion()` for response processing

### Phase 2: System Integration (Registration and Routing)
- **2.1** Update `GeneratorManager`:
  - Add `PRIVATEMODEL = "privatemodel"` to `ProviderType` enum
  - Register `PrivateModelGenerator` in `_provider_classes` mapping
  
- **2.2** Update configuration loading:
  - Add `PrivateModelGenerator` to client_classes in `backend/core/config/manager.py`
  - Update `load_generator_config()` to handle privatemodel provider
  - Ensure proper mapping in both `backend/utils/config_utils.py` and `backend/core/config/utils.py`

- **2.3** Update module exports:
  - Add imports in `backend/components/generator/providers/__init__.py`
  - Export class in `backend/components/generator/__init__.py`

### Phase 3: Configuration and Environment Support
- **3.1** Environment variable configuration:
  - `PRIVATE_MODEL_API_KEY` - Authentication key (only sensitive data not in config)
  
- **3.2** Configuration-driven setup:
  - Use `url_base` from `generator.json` for API endpoint
  - Use `default_model` from `generator.json` for default model
  - Validate endpoint connectivity on initialization

- **3.3** Error handling and validation:
  - Connection validation
  - Authentication verification
  - Model availability checks
  - Graceful fallback mechanisms

## Technical Implementation Details

### Generator Class Structure
```python
class PrivateModelGenerator(BaseGenerator):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        env_api_key_name: str = "PRIVATE_MODEL_API_KEY",
        **kwargs
    ):
        # api_key from environment variable
        # base_url from generator.json config
        # OpenAI-compatible client initialization
```

### Configuration Pattern
- **Config-first**: Use `url_base` and `default_model` from `generator.json`
- **Environment for secrets**: Only API key from environment variable
- **Validation**: Verify connectivity and authentication on startup
- **Error handling**: Clear error messages for configuration issues

### API Compatibility
- **OpenAI-compatible**: Leverage existing OpenAI client patterns
- **Standard endpoints**: Support `/chat/completions` and similar
- **Authentication**: Flexible auth header support
- **Response parsing**: Consistent with other providers

## Progress Tracking

**Overall Status:** Pending - 0%

### Subtasks
| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 3.1 | Create PrivateModelGenerator class file | Not Started | - | Core implementation foundation |
| 3.2 | Implement BaseGenerator interface methods | Not Started | - | Essential for system compatibility |
| 3.3 | Add provider type enum and registration | Not Started | - | Required for GeneratorManager |
| 3.4 | Update configuration loading utilities | Not Started | - | Enable discovery by config system |
| 3.5 | Add environment variable support | Not Started | - | Only API key needed from environment |
| 3.6 | Implement error handling and validation | Not Started | - | Production readiness |
| 3.7 | Update module exports and imports | Not Started | - | System-wide availability |
| 3.8 | Test integration with existing system | Not Started | - | Verify functionality |

## Environment Variables Design

```bash
# Only required environment variable (for authentication)
PRIVATE_MODEL_API_KEY=your_api_key_here

# All other configuration comes from generator.json:
# - url_base: "http://localhost:8000/v1" 
# - default_model: "custom-model"
# - model parameters: temperature, top_p, etc.
```

## Success Criteria
- [ ] PrivateModelGenerator successfully integrates with GeneratorManager
- [ ] Configuration loads correctly from both environment and config files
- [ ] API calls work with OpenAI-compatible private model endpoints
- [ ] Error handling provides clear feedback for configuration issues
- [ ] No hardcoded values in codebase - all configuration external
- [ ] Supports custom models and standard chat completion interface
- [ ] Maintains consistency with existing provider patterns

## Notes
- **OpenAI Compatibility**: Most private model deployments (vLLM, Ollama, LocalAI) provide OpenAI-compatible APIs
- **Flexible Authentication**: Support both API key and custom header authentication
- **Runtime Configuration**: Allow URL and model switching without code changes
- **Production Ready**: Include proper error handling and connection validation