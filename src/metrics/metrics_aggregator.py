"""
Agrégateur de métriques pour le dashboard.

Centralise toutes les métriques pour affichage.
"""

from typing import Optional
from datetime import datetime
from .cost_tracker import CostTracker
from .latency_tracker import LatencyTracker
from .carbon_tracker import CarbonTracker


class MetricsAggregator:
    """
    Agrège toutes les métriques pour le dashboard.
    
    Point central pour:
    - Collecter les métriques des différents trackers
    - Formater pour l'affichage Streamlit
    - Sauvegarder l'historique
    """
    
    def __init__(
        self,
        cost_tracker: CostTracker,
        latency_tracker: LatencyTracker,
        carbon_tracker: CarbonTracker
    ) -> None:
        """
        Initialise l'agrégateur.
        
        Args:
            cost_tracker: Tracker de coûts
            latency_tracker: Tracker de latence
            carbon_tracker: Tracker carbone
        """
        pass
    
    def get_all_metrics(self) -> dict:
        """
        Retourne toutes les métriques.
        
        Returns:
            {
                "cost": {...},
                "latency": {...},
                "carbon": {...},
                "sessions": {...}
            }
        """
        pass
    
    def get_summary(self) -> dict:
        """
        Résumé pour affichage rapide (cards).
        
        Returns:
            {
                "total_cost": float,
                "avg_latency_ms": float,
                "total_emissions_g": float,
                "session_count": int,
                "request_count": int
            }
        """
        pass
    
    def log_triage_session(
        self,
        session_id: str,
        patient_id: str,
        gravity_predicted: str,
        turn_count: int,
        duration_seconds: float,
        is_correct: Optional[bool] = None
    ) -> None:
        """
        Log une session de triage complète.
        
        Args:
            session_id: ID de la session
            patient_id: ID du patient
            gravity_predicted: Gravité prédite
            turn_count: Nombre de tours de dialogue
            duration_seconds: Durée totale
            is_correct: Prédiction correcte (si simulation)
        """
        pass
    
    def get_session_metrics(self, session_id: str) -> dict:
        """Métriques pour une session spécifique."""
        pass
    
    def get_accuracy_metrics(self) -> dict:
        """
        Métriques de précision (si simulations).
        
        Returns:
            {
                "accuracy": float,
                "by_gravity": {...},
                "confusion_matrix": [...]
            }
        """
        pass
    
    def export_to_json(self, path: str) -> None:
        """Exporte toutes les métriques en JSON."""
        pass
    
    def get_metrics_for_dashboard(self) -> dict:
        """
        Format optimisé pour Streamlit.
        
        Returns:
            {
                "cards": [...],      # Données pour les metric cards
                "charts": {...},     # Données pour les graphiques
                "tables": {...}      # Données pour les tableaux
            }
        """
        pass
    
    def get_time_series_data(self) -> dict:
        """Données temporelles pour les graphiques."""
        pass
    
    def reset_all(self) -> None:
        """Remet tous les trackers à zéro."""
        pass
