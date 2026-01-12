"""
Point d'entrée de l'application Streamlit.

Lancer avec: streamlit run app/main.py
"""

import streamlit as st


def init_session_state() -> None:
    """
    Initialise le session_state de Streamlit.
    
    Variables à initialiser:
    - workflow_simulation: SimulationWorkflow
    - workflow_interactive: InteractiveWorkflow
    - metrics_aggregator: MetricsAggregator
    - current_conversation: list
    - current_result: TriageResult | None
    """
    pass


def load_components():
    """
    Charge tous les composants (avec cache Streamlit).
    
    Utiliser @st.cache_resource pour:
    - LLM Provider
    - Embedding Provider
    - Vector Store
    - Classifier (modèle ML)
    
    Returns:
        Dict avec tous les composants initialisés
    """
    pass


def render_sidebar() -> None:
    """
    Affiche la sidebar avec:
    - Sélection de la page
    - Configuration (modèle LLM, etc.)
    - Métriques résumées
    """
    pass


def main() -> None:
    """
    Fonction principale.
    
    Structure:
    1. Configuration de la page
    2. Initialisation du state
    3. Chargement des composants
    4. Affichage sidebar
    5. Routing vers la bonne page
    """
    pass


if __name__ == "__main__":
    main()
