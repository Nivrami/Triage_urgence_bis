"""
Classe abstraite pour tous les agents.

JUSTIFIER: Pourquoi une classe abstraite?
- Garantit une interface commune
- Facilite l'extension (nouveaux agents)
- Permet le polymorphisme
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
from ..llm.base_llm import BaseLLMProvider
from ..models.conversation import ConversationHistory, MessageRole


class BaseAgent(ABC):
    """Classe abstraite pour tous les agents du système."""
    
    def __init__(
        self, 
        llm_provider: BaseLLMProvider, 
        system_prompt: str,
        name: str = "Agent"
    ) -> None:
        """
        Initialise l'agent.
        
        Args:
            llm_provider: Provider LLM à utiliser
            system_prompt: Prompt système définissant le comportement
            name: Nom de l'agent (pour le logging)
        """
        pass
    
    @abstractmethod
    def run(self, input_data: Any) -> dict:
        """
        Exécute l'agent avec les données d'entrée.
        
        Args:
            input_data: Données d'entrée (format dépend de l'agent)
            
        Returns:
            Résultat de l'exécution
        """
        pass
    
    def _build_messages(
        self, 
        user_input: str, 
        history: Optional[ConversationHistory] = None
    ) -> list[dict]:
        """
        Construit la liste des messages pour le LLM.
        
        Args:
            user_input: Message utilisateur actuel
            history: Historique de conversation optionnel
            
        Returns:
            Liste de messages au format LLM
        """
        pass
    
    def _parse_response(self, response: str) -> dict:
        """
        Parse la réponse du LLM.
        
        Override cette méthode pour un parsing custom.
        
        Args:
            response: Réponse brute du LLM
            
        Returns:
            Réponse parsée
        """
        pass
    
    def _extract_json_from_response(self, response: str) -> dict:
        """
        Extrait le JSON d'une réponse.
        Utile quand le LLM doit retourner du JSON.
        """
        pass
    
    def get_system_prompt(self) -> str:
        """Retourne le prompt système."""
        pass
    
    def update_system_prompt(self, new_prompt: str) -> None:
        """Met à jour le prompt système."""
        pass
