#!/usr/bin/env python3
"""
Test script to verify model configuration API returns defaultModel field
"""

import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.core.config.manager import get_config_manager
    from backend.models.config import Provider, Model, ModelConfig
    
    def test_model_config():
        """Test that model configuration includes defaultModel field"""
        print("Testing model configuration API response...")
        
        # Load dynamic generator configuration
        cfg_manager = get_config_manager()
        generator_cfg = cfg_manager.get_generator_config()

        providers_cfg = generator_cfg.get("providers", {}) or {}
        default_provider = generator_cfg.get("default_provider", "openai")

        # Friendly names for known providers; fallback to capitalized id
        provider_names = {
            "google": "Google",
            "openai": "OpenAI",
            "openrouter": "OpenRouter",
            "ollama": "Ollama",
            "bedrock": "Bedrock",
            "azure": "Azure AI",
            "dashscope": "DashScope",
        }

        providers = []
        for pid, pcfg in providers_cfg.items():
            models_cfg = (pcfg.get("models") or {})
            model_list = [
                Model(id=mid, name=mid) for mid in models_cfg.keys()
            ]
            
            # Get the default model for this provider
            default_model = pcfg.get("default_model")

            provider = Provider(
                id=pid,
                name=provider_names.get(pid, pid.capitalize()),
                supportsCustomModel=bool(pcfg.get("supportsCustomModel", False)),
                models=model_list,
                defaultModel=default_model,
            )
            providers.append(provider)

        model_config = ModelConfig(providers=providers, defaultProvider=default_provider)
        
        # Convert to dict for easier inspection
        config_dict = model_config.model_dump()
        
        print("\n=== Model Configuration Results ===")
        print(f"Default Provider: {config_dict['defaultProvider']}")
        
        print("\nProviders and their default models:")
        for provider in config_dict['providers']:
            print(f"  {provider['name']} ({provider['id']}): {provider.get('defaultModel', 'No default')}")
            if provider['id'] == 'openai':
                print(f"    Available models: {[m['id'] for m in provider['models']]}")
        
        # Test specifically for OpenAI
        openai_provider = next((p for p in config_dict['providers'] if p['id'] == 'openai'), None)
        if openai_provider:
            expected_default = 'gpt-4.1-mini'
            actual_default = openai_provider.get('defaultModel')
            
            print(f"\n=== OpenAI Provider Test ===")
            print(f"Expected default model: {expected_default}")
            print(f"Actual default model: {actual_default}")
            
            if actual_default == expected_default:
                print("✅ SUCCESS: OpenAI provider returns correct default model")
                return True
            else:
                print("❌ FAILURE: OpenAI provider does not return correct default model")
                return False
        else:
            print("❌ FAILURE: OpenAI provider not found")
            return False

    if __name__ == "__main__":
        success = test_model_config()
        sys.exit(0 if success else 1)
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Unable to run test due to missing dependencies")
    sys.exit(1)
except Exception as e:
    print(f"Test failed with error: {e}")
    sys.exit(1)
