"""
Workflow pour la page interactive.

L'utilisateur joue le rôle du patient et répond aux questions de l'agent.
"""

from typing import Optional
from ..agents.triage_agent import TriageAgent
from ..metrics.metrics_aggregator import MetricsAggregator
from ..models.patient import Patient
from ..models.conversation import ConversationHistory, MessageRole
from ..models.triage import TriageResult


class InteractiveWorkflow:
    """
    Workflow pour la page 2: mode interactif.
    
    L'utilisateur est le patient:
    1. L'agent pose une question
    2. L'utilisateur répond
    3. Répéter jusqu'à avoir assez d'infos
    4. Afficher le résultat du triage
    """
    
    def __init__(
        self,
        triage_agent: TriageAgent,
        metrics_aggregator: MetricsAggregator,
        max_turns: int = 15
    ) -> None:
        """
        Initialise le workflow.
        
        Args:
            triage_agent: Agent de triage
            metrics_aggregator: Agrégateur de métriques
            max_turns: Nombre max de tours
        """
        pass
    
    def initialize_session(self) -> dict:
        """
        Initialise une nouvelle session interactive.
        
        Returns:
            {
                "session_id": str,
                "welcome_message": str,
                "first_question": str
            }
        """
        pass
    
    def process_user_input(self, user_message: str) -> dict:
        """
        Traite un message de l'utilisateur (patient).
        
        Args:
            user_message: Réponse de l'utilisateur
            
        Returns:
            {
                "agent_response": str,
                "is_question": bool,     # True si c'est une question
                "is_complete": bool,     # True si triage terminé
                "patient_data": Patient, # Données extraites
                "triage_result": Optional[TriageResult]
            }
        """
        pass
    
    def get_next_question(self) -> str:
        """Retourne la prochaine question de l'agent."""
        pass
    
    def is_session_complete(self) -> bool:
        """Vérifie si le triage est terminé."""
        pass
    
    def get_result(self) -> Optional[TriageResult]:
        """Retourne le résultat (None si pas terminé)."""
        pass
    
    def get_conversation_history(self) -> list[dict]:
        """
        Historique formaté pour affichage.
        
        Returns:
            [{"role": "user"|"assistant", "content": str}, ...]
        """
        pass
    
    def get_current_patient_data(self) -> Patient:
        """Données patient extraites jusqu'à présent."""
        pass
    
    def get_session_metrics(self) -> dict:
        """Métriques de la session actuelle."""
        pass
    
    def force_triage(self) -> TriageResult:
        """
        Force le triage avec les infos disponibles.
        
        Utile si l'utilisateur veut un résultat avant la fin normale.
        """
        pass
    
    def reset(self) -> None:
        """Remet à zéro pour une nouvelle session."""
        pass
    
    def get_completeness_info(self) -> dict:
        """
        Infos sur la complétude des données.
        
        Returns:
            {
                "score": float,
                "missing": list[str],
                "collected": list[str]
            }
        """
        pass
