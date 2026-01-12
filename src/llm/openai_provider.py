"""
Implémentation du provider OpenAI.

JUSTIFIER: Pourquoi OpenAI?
- API stable et bien documentée
- Bons modèles pour le français
- Pricing transparent
- Compatible avec d'autres providers (Azure, etc.)
"""

from typing import Optional
import time
from .base_llm import BaseLLMProvider


# Coûts par 1000 tokens (à mettre à jour selon les prix actuels)
OPENAI_PRICING = {
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "gpt-3.5-turbo-16k": {"input": 0.001, "output": 0.002},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
}


class OpenAIProvider(BaseLLMProvider):
    """Provider pour l'API OpenAI."""
    
    def __init__(
        self, 
        model_name: str = "gpt-3.5-turbo",
        api_key: str = "",
        temperature: float = 0.7,
        **kwargs
    ) -> None:
        """
        Initialise le client OpenAI.
        
        JUSTIFIER le choix du modèle:
        - gpt-3.5-turbo: Bon rapport qualité/prix pour du triage simple
        - gpt-4o-mini: Meilleur raisonnement, prix raisonnable
        - gpt-4o: Meilleur mais plus cher
        """
        pass
    
    def generate(
        self, 
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Génère une réponse."""
        pass
    
    def generate_with_metadata(
        self, 
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> dict:
        """
        Génère une réponse avec métadonnées complètes.
        
        Implémentation:
        1. Mesurer le temps avant/après l'appel
        2. Extraire les tokens depuis response.usage
        3. Calculer le coût avec get_cost_per_token()
        """
        pass
    
    def count_tokens(self, text: str) -> int:
        """
        Compte les tokens avec tiktoken.
        
        Utiliser: tiktoken.encoding_for_model(self.model_name)
        """
        pass
    
    def get_cost_per_token(self) -> dict:
        """Retourne le coût par token selon le modèle."""
        pass
    
    def get_model_info(self) -> dict:
        """Informations sur le modèle."""
        pass
    
    def _handle_api_error(self, error: Exception) -> None:
        """Gestion des erreurs API."""
        pass
