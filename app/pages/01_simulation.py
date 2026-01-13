"""
Page 1: Simulation automatique.

Dialogue automatique entre agent de triage et patient simulé.
"""

import streamlit as st     

def render_simulation_page() -> None:
    """
    Affiche la page simulation complète.
    
    Layout:
    - Header avec titre et description
    - Sélecteur de profil patient
    - Zone de conversation
    - Boutons de contrôle (Start, Step, Run All)
    - Résultat du triage
    - Métriques d'évaluation
    """
    pass


def render_patient_profile_selector() -> dict:
    """
    Interface pour sélectionner/générer un profil patient.
    
    Options:
    - Profils prédéfinis par gravité
    - Génération aléatoire
    - Profil custom
    
    Returns:
        Profil patient sélectionné
    """
    pass


def render_conversation_display(messages: list[dict]) -> None:
    """
    Affiche la conversation en cours.
    
    Style:
    - Messages agent à gauche (bleu)
    - Messages patient à droite (gris)
    - Timestamps discrets
    """
    pass    


def render_control_buttons() -> str:
    """
    Boutons de contrôle de la simulation.
    
    Returns:
        Action sélectionnée ("start", "step", "run_all", "reset")
    """
    pass  


def render_result_card(result) -> None:
    """
    Affiche le résultat du triage.
    
    Inclut:
    - Badge couleur selon gravité
    - Score de confiance
    - Reasoning
    - Actions recommandées
    """
    pass


def render_evaluation_metrics(evaluation: dict) -> None:
    """
    Affiche les métriques d'évaluation.
    
    - Prédiction vs Réalité
    - Indicateur correct/incorrect
    - Erreur de sévérité
    """
    pass


def render_simulation_metrics() -> None:
    """
    Affiche les métriques de la simulation.
    
    - Nombre de tours
    - Temps total
    - Coût
    - Émissions CO2
    """
    pass
