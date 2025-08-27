"""
Dependency Injection Container Configuration.

This module configures the dependency injection container for the API,
managing component dependencies and lifecycle.
"""

from dependency_injector import containers, providers
from typing import Dict, Any


class Container(containers.DeclarativeContainer):
    """
    Main dependency injection container for the DeepWiki API.
    
    This container manages all component dependencies and provides
    a centralized way to configure and access application components.
    """
    
    # Configuration providers
    config = providers.Configuration()
    
    # Core components will be added here as the restructure progresses
    # For now, this is a placeholder structure
    
    # Example structure (to be implemented):
    # embedder_manager = providers.Singleton(
    #     EmbedderManager,
    #     config=config.embedder
    # )
    # 
    # generator_manager = providers.Singleton(
    #     GeneratorManager,
    #     config=config.generator
    # )
    # 
    # retriever = providers.Singleton(
    #     FAISSRetriever,
    #     vector_store=vector_store
    # )
    
    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """Initialize the container with configuration."""
        super().__init__()
        self.config.from_dict(kwargs)
    
    def wire(self, modules: list) -> None:
        """Wire the container to specified modules."""
        self.wire(modules=modules)
    
    def unwire(self) -> None:
        """Unwire the container from all modules."""
        self.unwire()


# Global container instance
container = Container()

def get_container() -> Container:
    """Get the global container instance."""
    return container

def configure_container(config_dict: Dict[str, Any]) -> None:
    """Configure the global container with settings."""
    container.config.from_dict(config_dict)
