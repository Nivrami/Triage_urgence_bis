"""
Composant dashboard pour les métriques.
"""

import streamlit as st
from typing import Optional


class MetricsDashboard:
    """
    Dashboard de métriques pour Streamlit.
    
    Affiche:
    - Cartes de métriques principales
    - Graphiques de coût et latence
    - Indicateur d'impact carbone
    """
    
    def __init__(self, metrics_data: dict) -> None:
        """
        Initialise le dashboard.
        
        Args:
            metrics_data: Données des métriques
        """
        pass
    
    def render(self) -> None:
        """Affiche le dashboard complet."""
        pass
    
    def render_summary_cards(self) -> None:
        """
        Affiche les cartes de résumé.
        
        4 colonnes:
        - Coût total
        - Latence moyenne
        - Émissions CO2
        - Sessions
        """
        pass
    
    def render_cost_chart(self) -> None:
        """
        Graphique des coûts.
        
        - Coût par modèle (bar chart)
        - Évolution dans le temps (line chart)
        """
        pass
    
    def render_latency_chart(self) -> None:
        """
        Graphique de latence.
        
        - Distribution (histogram)
        - P50, P95, P99 (bar chart)
        """
        pass
    
    def render_carbon_indicator(self) -> None:
        """
        Indicateur d'impact carbone.
        
        - Jauge visuelle
        - Équivalents concrets (km voiture, etc.)
        """
        pass
    
    def render_accuracy_metrics(self) -> None:
        """
        Métriques de précision (si simulations).
        
        - Accuracy globale
        - Matrice de confusion
        - Précision par classe
        """
        pass
    
    def render_session_table(self) -> None:
        """Tableau des sessions passées."""
        pass
    
    @staticmethod
    def create_metric_card(
        label: str,
        value: str,
        delta: Optional[str] = None,
        delta_color: str = "normal"
    ) -> None:
        """Crée une carte de métrique."""
        pass


def render_metrics_dashboard(metrics: dict) -> None:
    """Fonction helper pour afficher le dashboard."""
    pass


def render_cost_chart(cost_data: dict) -> None:
    """Affiche le graphique des coûts."""
    pass


def render_latency_chart(latency_data: dict) -> None:
    """Affiche le graphique de latence."""
    pass


def render_carbon_indicator(carbon_data: dict) -> None:
    """Affiche l'indicateur carbone."""
    pass


def render_summary_cards(summary: dict) -> None:
    """Affiche les cartes de résumé."""
    pass
