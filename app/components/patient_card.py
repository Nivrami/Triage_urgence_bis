"""
Composants pour afficher les infos patient et résultats de triage.
"""

import streamlit as st
from typing import Optional


# Couleurs par niveau de gravité
GRAVITY_COLORS = {
    "GRIS": "#9E9E9E",
    "VERT": "#4CAF50",
    "JAUNE": "#FFC107",
    "ROUGE": "#F44336",
}


class PatientCard:
    """
    Carte d'affichage des informations patient.
    """
    
    def __init__(self, patient_data: dict) -> None:
        """
        Initialise la carte patient.
        
        Args:
            patient_data: Données du patient
        """
        pass
    
    def render(self) -> None:
        """Affiche la carte complète."""
        pass
    
    def render_basic_info(self) -> None:
        """Affiche les infos de base (nom, âge, sexe)."""
        pass
    
    def render_symptoms(self) -> None:
        """Affiche les symptômes."""
        pass
    
    def render_constantes(self) -> None:
        """
        Affiche les constantes vitales.
        
        Avec indicateurs visuels pour les valeurs anormales.
        """
        pass
    
    def render_antecedents(self) -> None:
        """Affiche les antécédents et allergies."""
        pass
    
    def render_completeness(self) -> None:
        """Affiche le score de complétude."""
        pass


class TriageResultCard:
    """
    Carte d'affichage du résultat de triage.
    """
    
    def __init__(self, triage_result) -> None:
        """
        Initialise la carte résultat.
        
        Args:
            triage_result: TriageResult
        """
        pass
    
    def render(self) -> None:
        """Affiche la carte complète."""
        pass
    
    def render_gravity_badge(self) -> None:
        """
        Affiche le badge de gravité.
        
        Grand badge coloré avec le niveau.
        """
        pass
    
    def render_confidence(self) -> None:
        """Affiche le score de confiance."""
        pass
    
    def render_reasoning(self) -> None:
        """Affiche le raisonnement/justification."""
        pass
    
    def render_recommendations(self) -> None:
        """Affiche les actions recommandées."""
        pass
    
    def render_sources(self) -> None:
        """Affiche les sources RAG utilisées."""
        pass
    
    @staticmethod
    def get_gravity_color(gravity: str) -> str:
        """Retourne la couleur pour un niveau de gravité."""
        pass
    
    @staticmethod
    def get_gravity_description(gravity: str) -> str:
        """Retourne la description pour un niveau."""
        pass
