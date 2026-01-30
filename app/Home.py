"""
Page d'accueil - Application de triage des urgences.
"""

import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Triage Urgences - IA",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Titre principal
st.title("🏥 Système de Triage Intelligent aux Urgences")

st.markdown(
    """
---

## 👋 Bienvenue !

Cette application utilise l'intelligence artificielle pour simuler et analyser des conversations
de triage aux urgences.

### 🎯 Fonctionnalités

"""
)

# Colonnes pour les features
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
    ### 🎲 Génération de conversations

    - Génère des conversations automatiques entre infirmier et patient
    - Extraction automatique des informations médicales
    - Constantes vitales mesurées
    - Export des données pour machine learning

    👉 **[Aller à la page Génération](/Generation)**
    """
    )

with col2:
    st.markdown(
        """
    ### 👤 Mode interactif

    - Jouez le rôle de l'infirmier
    - Posez vos propres questions
    - Le patient IA répond en temps réel
    - Recommandations de triage


    """
    )

st.markdown(
    """
---

## 📊 Données générées

Les conversations générées contiennent :

- **Informations patient** : âge, sexe, symptômes, antécédents
- **Constantes vitales** : FC, FR, SpO2, TA, température
- **Historique complet** de la conversation
- **Format ML** : prêt pour l'entraînement de modèles

---

## 🚀 Commencer

Sélectionnez une page dans la barre latérale pour commencer ! 👈

"""
)

# Sidebar
with st.sidebar:
    st.markdown(
        """

    ---

    ### ℹ️ À propos

    Application développée pour le triage intelligent aux urgences.

    **Modèle LLM** : Mistral AI
    **Framework** : Streamlit
    """
    )

# Footer
st.markdown(
    """
---
<div style='text-align: center; color: gray;'>
    <small>🏥 Système de Triage Intelligent - 2025</small>
</div>
""",
    unsafe_allow_html=True,
)
