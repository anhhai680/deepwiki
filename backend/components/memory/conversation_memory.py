"""
Conversation memory component for managing chat history and context.

This module provides a conversation memory component that handles
conversation state and memory across interactions.
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from uuid import uuid4

from adalflow.core.component import DataComponent

logger = logging.getLogger(__name__)


@dataclass
class UserQuery:
    """Represents a user query in the conversation."""
    query_str: str


@dataclass
class AssistantResponse:
    """Represents an assistant response in the conversation."""
    response_str: str


@dataclass
class DialogTurn:
    """Represents a single turn in the conversation."""
    id: str
    user_query: UserQuery
    assistant_response: AssistantResponse


class CustomConversation:
    """Custom implementation of Conversation to fix the list assignment index out of range error."""

    def __init__(self):
        self.dialog_turns = []

    def append_dialog_turn(self, dialog_turn):
        """Safely append a dialog turn to the conversation."""
        if not hasattr(self, 'dialog_turns'):
            self.dialog_turns = []
        self.dialog_turns.append(dialog_turn)


class ConversationMemory(DataComponent):
    """
    Simple conversation management with a list of dialog turns.
    
    This component manages conversation history and provides
    methods for adding and retrieving dialog turns.
    """

    def __init__(self, **kwargs):
        """Initialize the conversation memory."""
        super().__init__()
        
        # Use our custom implementation instead of the original Conversation class
        self.current_conversation = CustomConversation()
        
        # Configuration options
        self._max_turns = kwargs.get("max_turns", 100)
        self._auto_cleanup = kwargs.get("auto_cleanup", True)
    
    def call(self) -> Dict:
        """
        Return the conversation history as a dictionary.
        
        Returns:
            Dict: Dictionary mapping turn IDs to dialog turns
        """
        all_dialog_turns = {}
        try:
            # Check if dialog_turns exists and is a list
            if hasattr(self.current_conversation, 'dialog_turns'):
                if self.current_conversation.dialog_turns:
                    logger.info(f"Memory content: {len(self.current_conversation.dialog_turns)} turns")
                    for i, turn in enumerate(self.current_conversation.dialog_turns):
                        if hasattr(turn, 'id') and turn.id is not None:
                            all_dialog_turns[turn.id] = turn
                            logger.info(f"Added turn {i+1} with ID {turn.id} to memory")
                        else:
                            logger.warning(f"Skipping invalid turn object in memory: {turn}")
                else:
                    logger.info("Dialog turns list exists but is empty")
            else:
                logger.info("No dialog_turns attribute in current_conversation")
                # Try to initialize it
                self.current_conversation.dialog_turns = []
        except Exception as e:
            logger.error(f"Error accessing dialog turns: {str(e)}")
            # Try to recover
            try:
                self.current_conversation = CustomConversation()
                logger.info("Recovered by creating new conversation")
            except Exception as e2:
                logger.error(f"Failed to recover: {str(e2)}")

        logger.info(f"Returning {len(all_dialog_turns)} dialog turns from memory")
        return all_dialog_turns

    def add_dialog_turn(self, user_query: str, assistant_response: str) -> bool:
        """
        Add a dialog turn to the conversation history.

        Args:
            user_query: The user's query
            assistant_response: The assistant's response

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a new dialog turn using our custom implementation
            dialog_turn = DialogTurn(
                id=str(uuid4()),
                user_query=UserQuery(query_str=user_query),
                assistant_response=AssistantResponse(response_str=assistant_response),
            )

            # Make sure the current_conversation has the append_dialog_turn method
            if not hasattr(self.current_conversation, 'append_dialog_turn'):
                logger.warning("current_conversation does not have append_dialog_turn method, creating new one")
                # Initialize a new conversation if needed
                self.current_conversation = CustomConversation()

            # Ensure dialog_turns exists
            if not hasattr(self.current_conversation, 'dialog_turns'):
                logger.warning("dialog_turns not found, initializing empty list")
                self.current_conversation.dialog_turns = []

            # Safely append the dialog turn
            self.current_conversation.dialog_turns.append(dialog_turn)
            
            # Auto-cleanup if enabled and we exceed max turns
            if self._auto_cleanup and len(self.current_conversation.dialog_turns) > self._max_turns:
                self._cleanup_old_turns()
            
            logger.info(f"Successfully added dialog turn, now have {len(self.current_conversation.dialog_turns)} turns")
            return True

        except Exception as e:
            logger.error(f"Error adding dialog turn: {str(e)}")
            # Try to recover by creating a new conversation
            try:
                self.current_conversation = CustomConversation()
                dialog_turn = DialogTurn(
                    id=str(uuid4()),
                    user_query=UserQuery(query_str=user_query),
                    assistant_response=AssistantResponse(response_str=assistant_response),
                )
                self.current_conversation.dialog_turns.append(dialog_turn)
                logger.info("Recovered from error by creating new conversation")
                return True
            except Exception as e2:
                logger.error(f"Failed to recover from error: {str(e2)}")
                return False
    
    def get_conversation_history(self, max_turns: Optional[int] = None) -> List[DialogTurn]:
        """
        Get the conversation history.
        
        Args:
            max_turns: Maximum number of turns to return (None for all)
            
        Returns:
            List[DialogTurn]: List of dialog turns
        """
        try:
            if not hasattr(self.current_conversation, 'dialog_turns'):
                return []
            
            turns = self.current_conversation.dialog_turns
            
            if max_turns is not None and max_turns > 0:
                turns = turns[-max_turns:]
            
            return turns
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    def get_last_turn(self) -> Optional[DialogTurn]:
        """
        Get the last dialog turn in the conversation.
        
        Returns:
            DialogTurn: The last turn if available, None otherwise
        """
        try:
            if (hasattr(self.current_conversation, 'dialog_turns') and 
                self.current_conversation.dialog_turns):
                return self.current_conversation.dialog_turns[-1]
            return None
            
        except Exception as e:
            logger.error(f"Error getting last turn: {str(e)}")
            return None
    
    def get_turn_by_id(self, turn_id: str) -> Optional[DialogTurn]:
        """
        Get a specific dialog turn by ID.
        
        Args:
            turn_id: The ID of the turn to retrieve
            
        Returns:
            DialogTurn: The turn if found, None otherwise
        """
        try:
            if not hasattr(self.current_conversation, 'dialog_turns'):
                return None
            
            for turn in self.current_conversation.dialog_turns:
                if turn.id == turn_id:
                    return turn
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting turn by ID: {str(e)}")
            return None
    
    def remove_turn(self, turn_id: str) -> bool:
        """
        Remove a specific dialog turn by ID.
        
        Args:
            turn_id: The ID of the turn to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not hasattr(self.current_conversation, 'dialog_turns'):
                return False
            
            turns = self.current_conversation.dialog_turns
            for i, turn in enumerate(turns):
                if turn.id == turn_id:
                    del turns[i]
                    logger.info(f"Removed turn with ID {turn_id}")
                    return True
            
            logger.warning(f"Turn with ID {turn_id} not found")
            return False
            
        except Exception as e:
            logger.error(f"Error removing turn: {str(e)}")
            return False
    
    def clear_conversation(self) -> bool:
        """
        Clear all conversation history.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if hasattr(self.current_conversation, 'dialog_turns'):
                self.current_conversation.dialog_turns.clear()
                logger.info("Cleared all conversation history")
                return True
            return True
            
        except Exception as e:
            logger.error(f"Error clearing conversation: {str(e)}")
            return False
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the conversation.
        
        Returns:
            Dict[str, Any]: Summary information about the conversation
        """
        try:
            if not hasattr(self.current_conversation, 'dialog_turns'):
                return {
                    "total_turns": 0,
                    "user_queries": 0,
                    "assistant_responses": 0,
                    "conversation_length": 0
                }
            
            turns = self.current_conversation.dialog_turns
            total_turns = len(turns)
            
            # Calculate conversation length (total characters)
            conversation_length = sum(
                len(turn.user_query.query_str) + len(turn.assistant_response.response_str)
                for turn in turns
            )
            
            return {
                "total_turns": total_turns,
                "user_queries": total_turns,
                "assistant_responses": total_turns,
                "conversation_length": conversation_length,
                "last_turn_id": turns[-1].id if turns else None
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation summary: {str(e)}")
            return {
                "total_turns": 0,
                "user_queries": 0,
                "assistant_responses": 0,
                "conversation_length": 0,
                "error": str(e)
            }
    
    def _cleanup_old_turns(self) -> None:
        """Remove old turns to stay within max_turns limit."""
        try:
            if not hasattr(self.current_conversation, 'dialog_turns'):
                return
            
            turns = self.current_conversation.dialog_turns
            if len(turns) > self._max_turns:
                # Keep only the most recent turns
                turns_to_remove = len(turns) - self._max_turns
                del turns[:turns_to_remove]
                logger.info(f"Cleaned up {turns_to_remove} old turns, now have {len(turns)} turns")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    def set_max_turns(self, max_turns: int) -> None:
        """
        Set the maximum number of turns to keep in memory.
        
        Args:
            max_turns: Maximum number of turns
        """
        if max_turns > 0:
            self._max_turns = max_turns
            logger.info(f"Set max turns to {max_turns}")
    
    def set_auto_cleanup(self, enabled: bool) -> None:
        """
        Enable or disable automatic cleanup of old turns.
        
        Args:
            enabled: Whether to enable auto-cleanup
        """
        self._auto_cleanup = enabled
        logger.info(f"Auto-cleanup {'enabled' if enabled else 'disabled'}")
