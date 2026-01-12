"""
Workflow pour la page simulation.

Orchestre le dialogue entre l'agent de triage et le patient simulé.
"""

from typing import Optional
from ..agents.triage_agent import TriageAgent
from ..agents.patient_simulator import PatientSimulator
from ..metrics.metrics_aggregator import MetricsAggregator
from ..models.patient import Patient, GravityLevel
from ..models.conversation import ConversationHistory
from ..models.triage import TriageResult, TriageEvaluation


class SimulationWorkflow:
    """
    Workflow pour la page 1: simulation automatique.
    
    Scénario:
    1. Générer/sélectionner un profil patient
    2. Boucle de dialogue (agent pose question, patient répond)
    3. Prédiction de gravité
    4. Évaluation (comparaison avec vraie gravité)
    """
    
    def __init__(
        self,
        triage_agent: TriageAgent,
        patient_simulator: PatientSimulator,
        metrics_aggregator: MetricsAggregator,
        max_turns: int = 10
    ) -> None:
        """
        Initialise le workflow.
        
        Args:
            triage_agent: Agent de triage
            patient_simulator: Simulateur de patient
            metrics_aggregator: Agrégateur de métriques
            max_turns: Nombre max de tours de dialogue
        """
        pass
    
    def initialize_simulation(
        self, 
        patient_profile: Optional[dict] = None,
        target_gravity: Optional[GravityLevel] = None
    ) -> dict:
        """
        Initialise une nouvelle simulation.
        
        Args:
            patient_profile: Profil custom (aléatoire si None)
            target_gravity: Gravité cible pour le profil aléatoire
            
        Returns:
            {
                "session_id": str,
                "patient_profile": dict,
                "first_message": str  # Première question de l'agent
            }
        """
        pass
    
    def run_step(self) -> dict:
        """
        Exécute un tour de dialogue.
        
        Returns:
            {
                "agent_question": str,
                "patient_response": str,
                "turn_number": int,
                "should_stop": bool,
                "patient_data": Patient  # Données extraites
            }
        """
        pass
    
    def run_full_simulation(self) -> dict:
        """
        Exécute la simulation complète jusqu'à la fin.
        
        Returns:
            {
                "conversation": list[dict],
                "triage_result": TriageResult,
                "evaluation": TriageEvaluation,
                "metrics": dict
            }
        """
        pass
    
    def get_current_state(self) -> dict:
        """
        État actuel de la simulation.
        
        Returns:
            {
                "session_id": str,
                "turn_count": int,
                "conversation": list[dict],
                "patient_data": Patient,
                "is_complete": bool
            }
        """
        pass
    
    def get_result(self) -> Optional[TriageResult]:
        """Retourne le résultat du triage (None si pas terminé)."""
        pass
    
    def evaluate_accuracy(self) -> TriageEvaluation:
        """
        Compare la prédiction à la vraie gravité.
        
        Returns:
            TriageEvaluation avec is_correct, severity_error, etc.
        """
        pass
    
    def get_conversation_history(self) -> list[dict]:
        """Historique de conversation formaté pour affichage."""
        pass
    
    def reset(self) -> None:
        """Remet à zéro pour une nouvelle simulation."""
        pass
    
    def _should_stop(self) -> bool:
        """Détermine si la simulation doit s'arrêter."""
        pass
