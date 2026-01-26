"""
Page 1: Simulation automatique.

Dialogue automatique entre agent de triage et patient simulé.
"""


import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))
from src.llm.llm_factory import LLMFactory
from src.agents.patient_generator import PatientGenerator
from src.agents.patient_simulator import PatientSimulator
from src.agents.nurse_agent import NurseAgent
from src.models.conversation import ConversationHistory
from dotenv import find_dotenv, load_dotenv
from typing import Optional

# Charger les variables d'environnement
load_dotenv(find_dotenv())

# Profils prédéfinis
PREDEFINED_PROFILES = {
    "🔴 Cas Grave - Infarctus": "Homme de 62 ans avec suspicion d'infarctus du myocarde",
    "🟡 Cas Modéré - Fracture": "Femme de 55 ans avec fracture suspectée du poignet après chute",
    "🟢 Cas Léger - Entorse": "Homme de 30 ans avec entorse de cheville",
    "🔵 Cas Critique - AVC": "Femme de 68 ans avec suspicion d'AVC, troubles de la parole et paralysie faciale",
    "🟠 Cas Urgent - Pneumonie": "Homme de 45 ans avec dyspnée importante et fièvre élevée",
}



def init_session_state() -> None:
    """Initialise le state de la session."""
    if "simulation_started" not in st.session_state:
        st.session_state.simulation_started = False
    if "simulation_paused" not in st.session_state:
        st.session_state.simulation_paused = False
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "patient" not in st.session_state:
        st.session_state.patient = None
    if "patient_simulator" not in st.session_state:
        st.session_state.patient_simulator = None
    if "nurse_agent" not in st.session_state:
        st.session_state.nurse_agent = None
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "simulation_complete" not in st.session_state:
        st.session_state.simulation_complete = False
    if "llm" not in st.session_state:
        st.session_state.llm = None


def reset_simulation() -> None:
    """Réinitialise la simulation."""
    st.session_state.simulation_started = False
    st.session_state.simulation_paused = False
    st.session_state.conversation_history = []
    st.session_state.patient = None
    st.session_state.patient_simulator = None
    st.session_state.nurse_agent = None
    st.session_state.conversation = None
    st.session_state.question_count = 0
    st.session_state.simulation_complete = False


def start_simulation(pathology_description: str) -> None:
    """Démarre une nouvelle simulation."""
    try:
        # Initialiser le LLM si nécessaire
        if st.session_state.llm is None:
            with st.spinner("🔧 Initialisation du LLM Mistral..."):
                st.session_state.llm = LLMFactory.create(
                    "mistral", "mistral-small-latest"
                )

        llm = st.session_state.llm

        # Générer le patient
        with st.spinner("🔍 Génération du patient..."):
            generator = PatientGenerator(llm)
            patient = generator.generate_from_description(pathology_description)
            st.session_state.patient = patient

        # Créer les agents
        with st.spinner("🤖 Création des agents..."):
            st.session_state.patient_simulator = PatientSimulator(llm, patient)
            st.session_state.nurse_agent = NurseAgent(llm, max_questions=6)

        # Obtenir la plainte initiale
        initial_complaint = st.session_state.patient_simulator.get_initial_complaint()
        st.session_state.conversation = ConversationHistory()
        st.session_state.conversation.add_assistant_message(initial_complaint)

        st.session_state.conversation_history = [
            {"role": "patient", "content": initial_complaint, "type": "initial"}
        ]

        st.session_state.simulation_started = True
        st.session_state.question_count = 0
        st.success("✅ Simulation démarrée avec succès!")

    except Exception as e:
        st.error(f"❌ Erreur lors du démarrage de la simulation: {str(e)}")


def step_simulation() -> None:
    """Exécute une étape de la simulation (une question/réponse)."""
    if not st.session_state.simulation_started:
        st.warning("⚠️ Veuillez démarrer la simulation d'abord.")
        return

    if st.session_state.simulation_complete:
        st.info("ℹ️ La simulation est terminée.")
        return

    nurse = st.session_state.nurse_agent
    patient_sim = st.session_state.patient_simulator

    if not nurse.should_continue():
        st.session_state.simulation_complete = True
        st.info("✅ Simulation terminée - Nombre maximum de questions atteint.")
        return

    try:
        # L'infirmier pose une question
        with st.spinner("💭 L'infirmier réfléchit..."):
            question = nurse.ask_next_question()

        st.session_state.conversation_history.append(
            {
                "role": "nurse",
                "content": question,
                "question_num": st.session_state.question_count + 1,
            }
        )
        st.session_state.conversation.add_user_message(question)
        nurse.add_to_history("nurse", question)

        # Le patient répond
        with st.spinner("💬 Le patient répond..."):
            response = patient_sim.respond(question)

        st.session_state.conversation_history.append(
            {
                "role": "patient",
                "content": response,
            }
        )
        st.session_state.conversation.add_assistant_message(response)
        nurse.add_to_history("patient", response)

        st.session_state.question_count += 1

        # Vérifier si la conversation doit se terminer
        if not nurse.should_continue():
            st.session_state.simulation_complete = True
            st.success("✅ Simulation terminée!")

    except Exception as e:
        st.error(f"❌ Erreur lors de l'étape: {str(e)}")


def run_all_simulation() -> None:
    """Exécute toute la simulation jusqu'à la fin."""
    if not st.session_state.simulation_started:
        st.warning("⚠️ Veuillez démarrer la simulation d'abord.")
        return

    nurse = st.session_state.nurse_agent
    max_iterations = 10  # Sécurité

    progress_bar = st.progress(0)
    status_text = st.empty()

    iteration = 0
    while nurse.should_continue() and iteration < max_iterations:
        status_text.text(
            f"Question {st.session_state.question_count + 1}/{nurse.max_questions}"
        )
        step_simulation()
        iteration += 1
        progress_bar.progress(min(iteration / nurse.max_questions, 1.0))

    progress_bar.empty()
    status_text.empty()
    st.success("✅ Simulation complète terminée!")


def render_patient_profile_selector() -> Optional[str]:
    """Interface pour sélectionner/générer un profil patient."""
    st.subheader("👤 Sélection du Profil Patient")

    profile_type = st.radio(
        "Type de profil", ["Profil prédéfini", "Profil personnalisé"], horizontal=True
    )

    pathology_description = None

    if profile_type == "Profil prédéfini":
        selected_profile = st.selectbox(
            "Choisissez un profil", list(PREDEFINED_PROFILES.keys())
        )
        pathology_description = PREDEFINED_PROFILES[selected_profile]
        st.info(f"📋 Description: {pathology_description}")

    else:
        pathology_description = st.text_area(
            "Description du cas médical",
            placeholder="Ex: Femme de 35 ans avec migraine sévère et vomissements",
            height=100,
        )

    return pathology_description


def render_conversation_display(messages: list[dict]) -> None: 
    """Affiche la conversation en cours."""
    if not messages:
        st.info("💬 La conversation apparaîtra ici une fois démarrée.")
        return

    for msg in messages:
        if msg["role"] == "patient":
            if msg.get("type") == "initial":
                with st.chat_message("assistant", avatar="🤕"):
                    st.markdown(f"**Plainte initiale:**\n\n{msg['content']}")
            else:
                with st.chat_message("assistant", avatar="🤕"):
                    st.markdown(msg["content"])
        else:  # nurse
            with st.chat_message("user", avatar="👨‍⚕️"):
                q_num = msg.get("question_num", "")
                st.markdown(f"**Question {q_num}:**\n\n{msg['content']}")


def render_control_buttons() -> None:
    """Boutons de contrôle de la simulation."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(
            "▶️ Démarrer",
            disabled=st.session_state.simulation_started,
            use_container_width=True,
        ):
            return "start"

    with col2:
        if st.button(
            "➡️ Étape suivante",
            disabled=not st.session_state.simulation_started
            or st.session_state.simulation_complete,
            use_container_width=True,
        ):
            return "step"

    with col3:
        if st.button(
            "⏩ Tout exécuter",
            disabled=not st.session_state.simulation_started
            or st.session_state.simulation_complete,
            use_container_width=True,
        ):
            return "run_all"

    with col4:
        if st.button("🔄 Réinitialiser", use_container_width=True):
            return "reset"

    return None
   


def render_patient_card(patient) -> None:
    """Affiche les informations du patient généré."""
    if patient is None:
        return

    with st.expander("👤 Informations du Patient", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Identité:**")
            st.write(f"• Nom: {patient.prenom} {patient.nom}")
            st.write(f"• Âge: {patient.age} ans")
            st.write(f"• Sexe: {patient.sexe}")
            st.write(f"• Depuis: {patient.duree_symptomes}")

        with col2:
            st.markdown("**Symptômes:**")
            for symptom in patient.symptomes_exprimes:
                st.write(f"• {symptom}")

        if patient.constantes:
            st.markdown("**Constantes Vitales:**")
            const_col1, const_col2, const_col3, const_col4, const_col5 = st.columns(5)

            with const_col1:
                st.metric("FC", f"{patient.constantes.fc} bpm")
            with const_col2:
                st.metric("FR", f"{patient.constantes.fr} /min")
            with const_col3:
                st.metric("SpO2", f"{patient.constantes.spo2}%")
            with const_col4:
                st.metric(
                    "TA",
                    f"{patient.constantes.ta_systolique}/{patient.constantes.ta_diastolique}",
                )
            with const_col5:
                st.metric("T°", f"{patient.constantes.temperature}°C")

        if patient.antecedents:
            st.markdown("**Antécédents:**")
            st.write(", ".join(patient.antecedents))


def render_simulation_metrics() -> None:
    """Affiche les métriques de la simulation."""
    if not st.session_state.simulation_started:
        return

    st.subheader("📊 Métriques de la Simulation")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Questions posées", st.session_state.question_count)

    with col2:
        total_messages = len(st.session_state.conversation_history)
        st.metric("Messages échangés", total_messages)

    with col3:
        max_q = (
            st.session_state.nurse_agent.max_questions
            if st.session_state.nurse_agent
            else 6
        )
        completion = (st.session_state.question_count / max_q) * 100
        st.metric("Progression", f"{completion:.0f}%")


def render_simulation_page() -> None:
    """Affiche la page simulation complète."""
    st.title("🏥 Simulation Automatique de Triage")
    st.markdown(
        """
    Cette page permet de simuler un dialogue automatique entre un agent de triage et un patient virtuel.
    L'agent pose des questions pour évaluer la gravité et proposer un niveau de triage approprié.
    """
    )

    init_session_state()

    # Sélection du profil patient
    pathology_description = render_patient_profile_selector()

    st.divider()

    # Boutons de contrôle
    action = render_control_buttons()

    # Traiter les actions
    if action == "start" and pathology_description:
        start_simulation(pathology_description)
        st.rerun()
    elif action == "step":
        step_simulation()
        st.rerun()
    elif action == "run_all":
        run_all_simulation()
    elif action == "reset":
        reset_simulation()
        st.rerun()
    elif action == "start" and not pathology_description:
        st.warning("⚠️ Veuillez saisir une description de cas médical.")

    st.divider()

    # Affichage du patient généré
    if st.session_state.patient:
        render_patient_card(st.session_state.patient)

    # Zone de conversation
    st.subheader("💬 Conversation")
    render_conversation_display(st.session_state.conversation_history)

    # Métriques
    if st.session_state.simulation_started:
        st.divider()
        render_simulation_metrics()

    # Message de fin
    if st.session_state.simulation_complete:
        st.success(
            "✅ La simulation est terminée. Vous pouvez maintenant procéder au triage final."
        )
        st.info(
            "💡 Astuce: Cliquez sur 'Réinitialiser' pour lancer une nouvelle simulation."
        )


if __name__ == "__main__":
    render_simulation_page()
