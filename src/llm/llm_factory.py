"""
Factory pour créer les providers LLM.

JUSTIFIER: Pourquoi le pattern Factory?
- Centralise la création des providers
- Facilite l'ajout de nouveaux providers
- Permet de changer de provider via config
- Principe SOLID: Open/Closed
"""

from typing import Optional
from .base_llm import BaseLLMProvider
from .openai_provider import OpenAIProvider


class LLMFactory:
    """Factory pour créer le bon provider LLM."""
    
    # Registry des providers disponibles
    _providers: dict[str, type] = {
        "openai": OpenAIProvider,
        # "mistral": MistralProvider,  # À implémenter si besoin
        # "ollama": OllamaProvider,    # Pour les modèles locaux
    }
    
    @classmethod
    def create(
        cls, 
        provider: str, 
        model_name: str,
        api_key: str = "",
        **kwargs
    ) -> BaseLLMProvider:
        """
        Crée le provider approprié.
        
        Args:
            provider: Nom du provider ("openai", "mistral", etc.)
            model_name: Nom du modèle
            api_key: Clé API
            **kwargs: Paramètres additionnels
            
        Returns:
            Instance du provider
            
        Raises:
            ValueError: Si le provider n'existe pas
        """
        pass
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """Retourne la liste des providers disponibles."""
        pass
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type) -> None:
        """
        Enregistre un nouveau provider.
        Utile pour ajouter des providers custom.
        """
        pass
    
    @classmethod
    def get_default_model(cls, provider: str) -> str:
        """Retourne le modèle par défaut pour un provider."""
        pass
