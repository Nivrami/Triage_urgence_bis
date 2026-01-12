"""
Composant chat réutilisable.
"""

import streamlit as st
from typing import Callable, Optional


class ChatInterface:
    """
    Composant de chat réutilisable pour Streamlit.
    
    Utilisé par les deux pages (simulation et interactive).
    """
    
    def __init__(
        self,
        on_message_submit: Optional[Callable[[str], None]] = None,
        placeholder: str = "Votre réponse...",
        disabled: bool = False
    ) -> None:
        """
        Initialise l'interface de chat.
        
        Args:
            on_message_submit: Callback quand un message est soumis
            placeholder: Texte placeholder de l'input
            disabled: Désactive l'input
        """
        pass
    
    def render(self, messages: list[dict]) -> None:
        """
        Affiche le chat complet.
        
        Args:
            messages: [{"role": "user"|"assistant", "content": str}]
        """
        pass
    
    def render_message(self, role: str, content: str) -> None:
        """Affiche un seul message."""
        pass
    
    def render_input(self) -> Optional[str]:
        """
        Affiche l'input et retourne le message soumis.
        
        Returns:
            Message soumis ou None
        """
        pass
    
    def render_typing_indicator(self) -> None:
        """Affiche un indicateur 'en train d'écrire'."""
        pass
    
    def scroll_to_bottom(self) -> None:
        """Scroll vers le bas du chat."""
        pass
    
    @staticmethod
    def format_message_for_display(message: dict) -> dict:
        """Formate un message pour l'affichage."""
        pass
