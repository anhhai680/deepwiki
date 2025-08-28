"""
Base Repository Class

Provides common data access patterns and operations for repositories.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from adalflow.core.types import Document

logger = logging.getLogger(__name__)

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """
    Abstract base class for repositories providing common data access patterns.
    
    This class defines the interface that all repositories must implement,
    ensuring consistent data access patterns across the system.
    """
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the repository and establish connections.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_initialized(self) -> bool:
        """
        Check if the repository is properly initialized.
        
        Returns:
            bool: True if initialized, False otherwise
        """
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """
        Retrieve an entity by its unique identifier.
        
        Args:
            id (str): The unique identifier
            
        Returns:
            Optional[T]: The entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[T]:
        """
        Retrieve all entities from the repository.
        
        Returns:
            List[T]: List of all entities
        """
        pass
    
    @abstractmethod
    def save(self, entity: T) -> bool:
        """
        Save an entity to the repository.
        
        Args:
            entity (T): The entity to save
            
        Returns:
            bool: True if save successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """
        Delete an entity by its unique identifier.
        
        Args:
            id (str): The unique identifier
            
        Returns:
            bool: True if delete successful, False otherwise
        """
        pass
    
    @abstractmethod
    def exists(self, id: str) -> bool:
        """
        Check if an entity exists by its unique identifier.
        
        Args:
            id (str): The unique identifier
            
        Returns:
            bool: True if entity exists, False otherwise
        """
        pass
    
    def get_by_ids(self, ids: List[str]) -> List[T]:
        """
        Retrieve multiple entities by their unique identifiers.
        
        Args:
            ids (List[str]): List of unique identifiers
            
        Returns:
            List[T]: List of found entities
        """
        entities = []
        for id in ids:
            entity = self.get_by_id(id)
            if entity:
                entities.append(entity)
        return entities
    
    def save_all(self, entities: List[T]) -> bool:
        """
        Save multiple entities to the repository.
        
        Args:
            entities (List[T]): List of entities to save
            
        Returns:
            bool: True if all saves successful, False otherwise
        """
        try:
            for entity in entities:
                if not self.save(entity):
                    return False
            return True
        except Exception as e:
            logger.error(f"Error saving multiple entities: {e}")
            return False
    
    def delete_all(self, ids: List[str]) -> bool:
        """
        Delete multiple entities by their unique identifiers.
        
        Args:
            ids (List[str]): List of unique identifiers
            
        Returns:
            bool: True if all deletes successful, False otherwise
        """
        try:
            for id in ids:
                if not self.delete(id):
                    return False
            return True
        except Exception as e:
            logger.error(f"Error deleting multiple entities: {e}")
            return False
    
    def count(self) -> int:
        """
        Get the total count of entities in the repository.
        
        Returns:
            int: Total count of entities
        """
        return len(self.get_all())
    
    def clear_cache(self) -> None:
        """
        Clear the internal cache.
        """
        self._cache.clear()
        logger.debug("Repository cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the internal cache.
        
        Returns:
            Dict[str, Any]: Cache information
        """
        return {
            "cache_size": len(self._cache),
            "cache_keys": list(self._cache.keys()),
            "initialized": self._initialized
        }
    
    def validate_entity(self, entity: T) -> bool:
        """
        Validate an entity before saving.
        
        Args:
            entity (T): The entity to validate
            
        Returns:
            bool: True if entity is valid, False otherwise
        """
        # Default implementation - subclasses can override
        return entity is not None
    
    def pre_save_hook(self, entity: T) -> T:
        """
        Hook called before saving an entity.
        
        Args:
            entity (T): The entity to be saved
            
        Returns:
            T: The entity (potentially modified)
        """
        # Default implementation - subclasses can override
        return entity
    
    def post_save_hook(self, entity: T) -> None:
        """
        Hook called after saving an entity.
        
        Args:
            entity (T): The entity that was saved
        """
        # Default implementation - subclasses can override
        pass
    
    def pre_delete_hook(self, id: str) -> bool:
        """
        Hook called before deleting an entity.
        
        Args:
            id (str): The ID of the entity to be deleted
            
        Returns:
            bool: True if deletion should proceed, False to cancel
        """
        # Default implementation - subclasses can override
        return True
    
    def post_delete_hook(self, id: str) -> None:
        """
        Hook called after deleting an entity.
        
        Args:
            id (str): The ID of the entity that was deleted
        """
        # Default implementation - subclasses can override
        pass
    
    def __enter__(self):
        """
        Context manager entry point.
        """
        if not self.is_initialized():
            self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point.
        """
        self.clear_cache()
        return False  # Don't suppress exceptions
