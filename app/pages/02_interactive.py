"""
Page 2: Mode interactif.

L'utilisateur joue le rôle du patient.
"""

import streamlit as st


def render_interactive_page() -> None:
    """
    Affiche la page interactive complète.
    
    Layout:
    - Header avec instructions
    - Zone de chat (historique)
    - Input utilisateur
    - Indicateur de progression
    - Résultat (quand terminé)
    """
    pass


def render_chat_interface() -> None:
    """
    Interface de chat Streamlit.
    
    Utilise st.chat_message pour un rendu moderne.
    """
    pass


def render_chat_input() -> str:
    """
    Input pour la réponse de l'utilisateur.
    
    Returns:
        Message saisi par l'utilisateur
    """
    pass


def render_chat_history(messages: list[dict]) -> None:
    """
    Affiche l'historique du chat.
    
    Format attendu:
    [{"role": "assistant", "content": "..."}, {"role": "user", "content": "..."}]
    """
    pass


def render_progress_indicator(completeness: dict) -> None:
    """
    Indicateur de progression du triage.
    
    Affiche:
    - Barre de progression
    - Infos collectées
    - Infos manquantes
    """
    pass


def render_triage_result(result) -> None:
    """
    Affiche le résultat final du triage.
    
    Style visuel avec:
    - Grande carte colorée
    - Niveau de gravité
    - Recommandations
    - Disclaimer médical
    """
    pass


def render_session_controls() -> None:
    """
    Boutons de contrôle de session.
    
    - Nouvelle session
    - Forcer le triage
    - Voir les métriques
    """
    pass


def render_disclaimer() -> None:
    """
    Affiche le disclaimer médical.
    
    IMPORTANT: Ce système est une démonstration,
    ne remplace pas un avis médical professionnel.
    """
    pass
