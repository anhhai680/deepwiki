"""
Provider configuration management.

This module will contain provider-specific configurations
extracted from the existing config.py file during the restructure.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class ProviderConfig(BaseModel):
    """Base configuration for AI providers."""
    
    name: str
    enabled: bool = True
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    
    class Config:
        extra = "allow"


class ProviderManager:
    """
    Manager for AI provider configurations.
    
    This class will be populated with provider management logic
    extracted from the existing config.py file during the restructure.
    """
    
    def __init__(self):
        self.providers: Dict[str, ProviderConfig] = {}
    
    def add_provider(self, name: str, config: Dict[str, Any]) -> None:
        """Add a provider configuration."""
        self.providers[name] = ProviderConfig(name=name, **config)
    
    def get_provider(self, name: str) -> Optional[ProviderConfig]:
        """Get a provider configuration by name."""
        return self.providers.get(name)
    
    def get_enabled_providers(self) -> Dict[str, ProviderConfig]:
        """Get all enabled providers."""
        return {name: config for name, config in self.providers.items() 
                if config.enabled}


# Global provider manager instance
provider_manager = ProviderManager()


def get_provider_manager() -> ProviderManager:
    """Get the global provider manager instance."""
    return provider_manager
