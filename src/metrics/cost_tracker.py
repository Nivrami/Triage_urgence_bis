"""
Suivi des coûts API.

Important pour le projet: justifier la sobriété des ressources utilisées.
"""

from datetime import datetime
from typing import Optional


# Pricing par 1000 tokens (à mettre à jour)
PRICING = {
    "openai": {
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "text-embedding-3-small": {"input": 0.00002, "output": 0},
    },
    "mistral": {
        "mistral-small": {"input": 0.001, "output": 0.003},
        "mistral-medium": {"input": 0.0027, "output": 0.0081},
    },
}


class CostTracker:
    """
    Suivi des coûts API.
    
    Track chaque requête et calcule les coûts cumulés.
    """
    
    def __init__(self) -> None:
        """Initialise le tracker."""
        pass
    
    def log_request(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        request_type: str = "completion"
    ) -> float:
        """
        Log une requête API.
        
        Args:
            provider: Nom du provider (openai, mistral)
            model: Nom du modèle
            input_tokens: Tokens en entrée
            output_tokens: Tokens en sortie
            request_type: Type de requête (completion, embedding)
            
        Returns:
            Coût de cette requête
        """
        pass
    
    def calculate_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calcule le coût d'une requête.
        
        Returns:
            Coût en dollars
        """
        pass
    
    def get_total_cost(self) -> float:
        """Retourne le coût total cumulé."""
        pass
    
    def get_cost_by_model(self) -> dict[str, float]:
        """Coût par modèle."""
        pass
    
    def get_cost_by_request_type(self) -> dict[str, float]:
        """Coût par type de requête."""
        pass
    
    def get_cost_breakdown(self) -> dict:
        """
        Détail complet des coûts.
        
        Returns:
            {
                "total": float,
                "by_model": {...},
                "by_type": {...},
                "total_tokens": {"input": int, "output": int},
                "request_count": int
            }
        """
        pass
    
    def get_average_cost_per_request(self) -> float:
        """Coût moyen par requête."""
        pass
    
    def get_session_cost(self, session_id: str) -> float:
        """Coût pour une session spécifique."""
        pass
    
    def reset(self) -> None:
        """Remet les compteurs à zéro."""
        pass
    
    def export_to_dict(self) -> dict:
        """Exporte pour sauvegarde/affichage."""
        pass
    
    def get_cost_history(self) -> list[dict]:
        """Historique des coûts par requête."""
        pass
