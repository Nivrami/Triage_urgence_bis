"""
Modèles pour la gestion des conversations.
"""

from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class MessageRole(Enum):
    """Rôles possibles dans une conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    
    def to_openai_format(self) -> str:
        """Format pour l'API OpenAI."""
        pass


class Message(BaseModel):
    """Un message dans la conversation."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[dict] = Field(default_factory=dict)
    
    def to_llm_format(self) -> dict:
        """Format pour l'API LLM (OpenAI, etc.)."""
        pass
    
    def to_display_format(self) -> dict:
        """Format pour l'affichage dans l'interface."""
        pass


class ConversationHistory(BaseModel):
    """Historique complet d'une conversation de triage."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Métadonnées de session
    session_type: str = Field(default="interactive")  # "interactive" ou "simulation"
    is_complete: bool = Field(default=False)
    
    def add_message(self, role: MessageRole, content: str, metadata: Optional[dict] = None) -> None:
        """Ajoute un message à l'historique."""
        pass
    
    def add_system_message(self, content: str) -> None:
        """Ajoute un message système."""
        pass
    
    def add_user_message(self, content: str) -> None:
        """Ajoute un message utilisateur (patient)."""
        pass
    
    def add_assistant_message(self, content: str) -> None:
        """Ajoute un message assistant (infirmier/agent)."""
        pass
    
    def to_llm_format(self) -> list[dict]:
        """Convertit l'historique au format API LLM."""
        pass
    
    def to_display_format(self) -> list[dict]:
        """Format pour affichage Streamlit."""
        pass
    
    def get_last_n_messages(self, n: int) -> list[Message]:
        """Retourne les n derniers messages."""
        pass
    
    def get_messages_by_role(self, role: MessageRole) -> list[Message]:
        """Retourne tous les messages d'un rôle donné."""
        pass
    
    def get_full_text(self) -> str:
        """Retourne la conversation complète en texte."""
        pass
    
    def get_turn_count(self) -> int:
        """Retourne le nombre de tours de dialogue."""
        pass
    
    def clear(self) -> None:
        """Vide l'historique."""
        pass
