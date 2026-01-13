"""
Page 2: Mode interactif.

L'utilisateur joue le rôle du patient ou de l'infirmier.
"""

import streamlit as st
from src.llm.llm_factory import LLMFactory
from src.agents.patient_generator import PatientGenerator
from src.agents.patient_simulator import PatientSimulator
from src.agents.nurse_agent import NurseAgent
from src.models.conversation import ConversationHistory
from dotenv import find_dotenv, load_dotenv
from typing import Optional, Dict

# Charger les variables d'environnement
load_dotenv(find_dotenv())

# Couleurs par niveau de gravité
GRAVITY_COLORS = {
    "GRIS": "#9E9E9E",
    "VERT": "#4CAF50",
    "JAUNE": "#FFC107",
    "ROUGE": "#F44336",
}

GRAVITY_DESCRIPTIONS = {
    "GRIS": "Décédé ou situation dépassée",
    "VERT": "Peu urgent - Peut attendre",
    "JAUNE": "Urgent - Prise en charge rapide nécessaire",
    "ROUGE": "Très urgent - Pronostic vital engagé",
}


def init_session_state() -> None:
    """Initialise le state de la session."""
    if "interactive_mode" not in st.session_state:
        st.session_state.interactive_mode = None  # "patient" ou "nurse"
    if "interactive_started" not in st.session_state:
        st.session_state.interactive_started = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "llm" not in st.session_state:
        st.session_state.llm = None
    if "patient_simulator" not in st.session_state:
        st.session_state.patient_simulator = None
    if "nurse_agent" not in st.session_state:
        st.session_state.nurse_agent = None
    if "patient_profile" not in st.session_state:
        st.session_state.patient_profile = None
    if "triage_result" not in st.session_state:
        st.session_state.triage_result = None
    if "session_complete" not in st.session_state:
        st.session_state.session_complete = False
    if "question_count" not in st.session_state:
        st.session_state.question_count = 0
    if "info_collected" not in st.session_state:
        st.session_state.info_collected = {
            "symptoms": False,
            "duration": False,
            "intensity": False,
            "medical_history": False,
            "vital_signs": False,
        }


def reset_session() -> None:
    """Réinitialise la session interactive."""
    st.session_state.interactive_mode = None
    st.session_state.interactive_started = False
    st.session_state.messages = []
    st.session_state.conversation = None
    st.session_state.patient_simulator = None
    st.session_state.nurse_agent = None
    st.session_state.patient_profile = None
    st.session_state.triage_result = None
    st.session_state.session_complete = False
    st.session_state.question_count = 0
    st.session_state.info_collected = {
        "symptoms": False,
        "duration": False,
        "intensity": False,
        "medical_history": False,
        "vital_signs": False,
    }


def start_interactive_session(
    mode: str, pathology_description: Optional[str] = None
) -> None:
    """Démarre une session interactive."""
    try:
        # Initialiser le LLM
        if st.session_state.llm is None:
            with st.spinner("🔧 Initialisation du LLM..."):
                st.session_state.llm = LLMFactory.create(
                    "mistral", "mistral-small-latest"
                )

        llm = st.session_state.llm
        st.session_state.interactive_mode = mode
        st.session_state.conversation = ConversationHistory()

        if mode == "patient":
            # Mode: utilisateur = patient, agent = infirmier
            with st.spinner("🤖 Création de l'agent infirmier..."):
                st.session_state.nurse_agent = NurseAgent(llm, max_questions=10)

            # L'infirmier commence la conversation
            initial_question = st.session_state.nurse_agent.ask_next_question()
            st.session_state.messages.append(
                {"role": "assistant", "content": initial_question, "avatar": "👨‍⚕️"}
            )
            st.session_state.conversation.add_assistant_message(initial_question)
            st.session_state.nurse_agent.add_to_history("nurse", initial_question)

        else:  # mode == "nurse"
            # Mode: utilisateur = infirmier, agent = patient
            if not pathology_description:
                st.error("❌ Description du cas requise pour le mode infirmier")
                return

            with st.spinner("🔍 Génération du patient virtuel..."):
                generator = PatientGenerator(llm)
                patient = generator.generate_from_description(pathology_description)
                st.session_state.patient_profile = patient
                st.session_state.patient_simulator = PatientSimulator(llm, patient)

            # Le patient commence avec sa plainte
            initial_complaint = (
                st.session_state.patient_simulator.get_initial_complaint()
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": initial_complaint, "avatar": "🤕"}
            )
            st.session_state.conversation.add_assistant_message(initial_complaint)

        st.session_state.interactive_started = True
        st.success("✅ Session démarrée avec succès!")

    except Exception as e:
        st.error(f"❌ Erreur lors du démarrage: {str(e)}")


def handle_user_message(user_message: str) -> None:
    """Traite un message de l'utilisateur."""
    if not user_message.strip():
        return

    mode = st.session_state.interactive_mode

    # Ajouter le message utilisateur
    st.session_state.messages.append(
        {"role": "user", "content": user_message, "avatar": "👤"}
    )
    st.session_state.conversation.add_user_message(user_message)
    st.session_state.question_count += 1

    # Analyser le message pour mettre à jour les infos collectées
    update_info_collected(user_message)

    try:
        if mode == "patient":
            # L'utilisateur est le patient, l'agent infirmier répond
            nurse = st.session_state.nurse_agent
            nurse.add_to_history("patient", user_message)

            if nurse.should_continue() and not st.session_state.session_complete:
                with st.spinner("💭 L'infirmier analyse votre réponse..."):
                    next_question = nurse.ask_next_question()

                st.session_state.messages.append(
                    {"role": "assistant", "content": next_question, "avatar": "👨‍⚕️"}
                )
                st.session_state.conversation.add_assistant_message(next_question)
                nurse.add_to_history("nurse", next_question)
            else:
                # Session terminée, proposer le triage
                st.session_state.session_complete = True
                completion_message = "Merci pour ces informations. L'évaluation est maintenant complète. Vous pouvez consulter le résultat du triage ci-dessous."
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": completion_message,
                        "avatar": "👨‍⚕️",
                    }
                )

        else:  # mode == "nurse"
            # L'utilisateur est l'infirmier, le patient virtuel répond
            patient_sim = st.session_state.patient_simulator

            with st.spinner("💬 Le patient réfléchit..."):
                response = patient_sim.respond(user_message)

            st.session_state.messages.append(
                {"role": "assistant", "content": response, "avatar": "🤕"}
            )
            st.session_state.conversation.add_assistant_message(response)

            # Vérifier si assez d'informations collectées
            if check_completion():
                st.session_state.session_complete = True

    except Exception as e:
        st.error(f"❌ Erreur lors du traitement: {str(e)}")


def update_info_collected(message: str) -> None:
    """Met à jour les informations collectées basé sur le message."""
    message_lower = message.lower()

    # Détection simple par mots-clés
    symptom_keywords = ["symptôme", "douleur", "mal", "souffr", "gên"]
    duration_keywords = ["depuis", "quand", "combien de temps", "début"]
    intensity_keywords = ["intensité", "échelle", "grave", "sévère", "fort"]
    history_keywords = ["antécédent", "maladie", "traitement", "allergie", "médical"]
    vitals_keywords = ["tension", "température", "pouls", "fréquence", "saturation"]

    if any(kw in message_lower for kw in symptom_keywords):
        st.session_state.info_collected["symptoms"] = True
    if any(kw in message_lower for kw in duration_keywords):
        st.session_state.info_collected["duration"] = True
    if any(kw in message_lower for kw in intensity_keywords):
        st.session_state.info_collected["intensity"] = True
    if any(kw in message_lower for kw in history_keywords):
        st.session_state.info_collected["medical_history"] = True
    if any(kw in message_lower for kw in vitals_keywords):
        st.session_state.info_collected["vital_signs"] = True


def check_completion() -> bool:
    """Vérifie si assez d'informations ont été collectées."""
    collected = sum(st.session_state.info_collected.values())
    return collected >= 3 or st.session_state.question_count >= 8


def calculate_completeness() -> Dict[str, any]:
    """Calcule le pourcentage de complétude."""
    collected = sum(st.session_state.info_collected.values())
    total = len(st.session_state.info_collected)
    percentage = (collected / total) * 100

    return {
        "percentage": percentage,
        "collected": collected,
        "total": total,
        "details": st.session_state.info_collected,
    }


def render_mode_selector() -> Optional[str]:
    """Sélecteur de mode interactif."""
    st.subheader("🎭 Choisissez votre rôle")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🤕 Je suis le patient", use_container_width=True, type="primary"):
            return "patient"

    with col2:
        if st.button(
            "👨‍⚕️ Je suis l'infirmier", use_container_width=True, type="primary"
        ):
            return "nurse"

    st.info(
        "💡 **Patient**: L'agent jouera le rôle de l'infirmier et vous posera des questions\n\n"
        "💡 **Infirmier**: Vous interrogerez un patient virtuel généré par l'IA"
    )

    return None


def render_nurse_mode_setup() -> Optional[str]:
    """Configuration pour le mode infirmier."""
    st.subheader("📋 Configuration du patient virtuel")

    pathology_description = st.text_area(
        "Décrivez le cas médical du patient virtuel",
        placeholder="Ex: Homme de 45 ans avec douleur thoracique intense et essoufflement",
        height=100,
        key="pathology_input",
    )

    if st.button("▶️ Commencer la consultation", disabled=not pathology_description):
        return pathology_description

    return None


def render_chat_history(messages: list[dict]) -> None:
    """Affiche l'historique du chat."""
    for msg in messages:
        avatar = msg.get("avatar", "💬")
        role = "assistant" if msg["role"] == "assistant" else "user"

        with st.chat_message(role, avatar=avatar):
            st.markdown(msg["content"])


def render_chat_input() -> Optional[str]:
    """Input pour la réponse de l'utilisateur."""
    if st.session_state.session_complete:
        st.info(
            "✅ La session est terminée. Consultez le résultat du triage ci-dessous."
        )
        return None

    mode = st.session_state.interactive_mode

    if mode == "patient":
        placeholder = "Décrivez vos symptômes, répondez aux questions de l'infirmier..."
    else:
        placeholder = "Posez une question au patient..."

    return st.chat_input(placeholder, key="chat_input")


def render_progress_indicator(completeness: dict) -> None:
    """Indicateur de progression du triage."""
    st.subheader("📊 Progression de l'évaluation")

    percentage = completeness["percentage"]
    st.progress(percentage / 100)
    st.caption(
        f"Complétude: {percentage:.0f}% ({completeness['collected']}/{completeness['total']} catégories)"
    )

    with st.expander("📝 Détails des informations collectées"):
        info_labels = {
            "symptoms": (
                "✅ Symptômes"
                if completeness["details"]["symptoms"]
                else "⬜ Symptômes"
            ),
            "duration": (
                "✅ Durée" if completeness["details"]["duration"] else "⬜ Durée"
            ),
            "intensity": (
                "✅ Intensité"
                if completeness["details"]["intensity"]
                else "⬜ Intensité"
            ),
            "medical_history": (
                "✅ Antécédents"
                if completeness["details"]["medical_history"]
                else "⬜ Antécédents"
            ),
            "vital_signs": (
                "✅ Constantes"
                if completeness["details"]["vital_signs"]
                else "⬜ Constantes"
            ),
        }

        for label in info_labels.values():
            st.write(label)


def render_triage_result(result) -> None:
    """Affiche le résultat final du triage."""
    if result is None:
        return

    gravity = result.get("gravity", "VERT")
    confidence = result.get("confidence", 0.75)
    reasoning = result.get("reasoning", "Analyse en cours...")
    recommendations = result.get("recommendations", [])

    color = GRAVITY_COLORS.get(gravity, "#4CAF50")

    st.markdown(
        f"""
    <div style="
        background: linear-gradient(135deg, {color}22 0%, {color}11 100%);
        border-left: 5px solid {color};
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    ">
        <h2 style="color: {color}; margin: 0 0 10px 0;">
            🏥 Résultat du Triage: {gravity}
        </h2>
        <p style="font-size: 14px; color: #666; margin: 0;">
            {GRAVITY_DESCRIPTIONS.get(gravity, "")}
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**💭 Raisonnement:**")
        st.write(reasoning)

        if recommendations:
            st.markdown("**🎯 Recommandations:**")
            for rec in recommendations:
                st.write(f"• {rec}")

    with col2:
        st.metric("Confiance", f"{confidence*100:.0f}%")

        if confidence < 0.6:
            st.warning("⚠️ Confiance faible")
        elif confidence > 0.85:
            st.success("✅ Haute confiance")


def render_session_controls() -> None:
    """Boutons de contrôle de session."""
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Nouvelle session", use_container_width=True):
            reset_session()
            st.rerun()

    with col2:
        if st.button(
            "🏁 Forcer le triage",
            disabled=not st.session_state.interactive_started
            or len(st.session_state.messages) < 2,
            use_container_width=True,
        ):
            # Simuler un résultat de triage
            st.session_state.triage_result = {
                "gravity": "JAUNE",
                "confidence": 0.78,
                "reasoning": "Symptômes nécessitant une prise en charge rapide mais sans urgence vitale immédiate.",
                "recommendations": [
                    "Consultation médicale dans les 2-4 heures",
                    "Surveillance des constantes vitales",
                    "Hydratation et position de confort",
                ],
            }
            st.session_state.session_complete = True
            st.rerun()

    with col3:
        if st.button("📈 Voir métriques", use_container_width=True):
            st.session_state.show_metrics = not st.session_state.get(
                "show_metrics", False
            )


def render_disclaimer() -> None:
    """Affiche le disclaimer médical."""
    st.warning(
        """
    ⚠️ **AVERTISSEMENT MÉDICAL IMPORTANT**
    
    Ce système est une **démonstration à but éducatif uniquement**.
    
    Il **NE REMPLACE EN AUCUN CAS** :
    - Un avis médical professionnel
    - Une consultation médicale
    - Un diagnostic médical réel
    - Une prise en charge hospitalière
    
    En cas d'urgence médicale réelle, contactez immédiatement le **15 (SAMU)** ou le **112**.
    """
    )


def render_patient_profile() -> None:
    """Affiche le profil du patient virtuel (mode infirmier uniquement)."""
    if (
        st.session_state.interactive_mode != "nurse"
        or not st.session_state.patient_profile
    ):
        return

    patient = st.session_state.patient_profile

    with st.expander(
        "👤 Profil du patient virtuel (informations système)", expanded=False
    ):
        st.caption("ℹ️ Ces informations ne sont visibles que pour la démonstration")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Nom:** {patient.prenom} {patient.nom}")
            st.write(f"**Âge:** {patient.age} ans")
            st.write(f"**Sexe:** {patient.sexe}")

        with col2:
            st.write(f"**Depuis:** {patient.duree_symptomes}")
            if patient.antecedents:
                st.write(f"**Antécédents:** {', '.join(patient.antecedents)}")

        if patient.constantes:
            st.markdown("**Constantes réelles:**")
            const_cols = st.columns(5)
            const_cols[0].metric("FC", f"{patient.constantes.fc}")
            const_cols[1].metric("FR", f"{patient.constantes.fr}")
            const_cols[2].metric("SpO2", f"{patient.constantes.spo2}%")
            const_cols[3].metric(
                "TA",
                f"{patient.constantes.ta_systolique}/{patient.constantes.ta_diastolique}",
            )
            const_cols[4].metric("T°", f"{patient.constantes.temperature}°C")


def render_interactive_page() -> None:
    """Affiche la page interactive complète."""
    st.title("💬 Mode Interactif")
    st.markdown(
        """
    Interagissez directement avec l'IA en jouant soit le rôle du **patient**, soit celui de **l'infirmier**.
    """
    )

    init_session_state()
    render_disclaimer()

    st.divider()

    # Sélection du mode si pas encore démarré
    if not st.session_state.interactive_started:
        selected_mode = render_mode_selector()

        if selected_mode == "patient":
            start_interactive_session("patient")
            st.rerun()

        elif selected_mode == "nurse":
            pathology = render_nurse_mode_setup()
            if pathology:
                start_interactive_session("nurse", pathology)
                st.rerun()

    else:
        # Session en cours
        st.success(
            f"🎭 Mode: **{'Patient' if st.session_state.interactive_mode == 'patient' else 'Infirmier'}**"
        )

        # Afficher le profil patient si mode infirmier
        render_patient_profile()

        # Contrôles de session
        render_session_controls()

        st.divider()

        # Zone de chat
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("💬 Conversation")
            render_chat_history(st.session_state.messages)

            # Input utilisateur
            user_input = render_chat_input()
            if user_input:
                handle_user_message(user_input)
                st.rerun()

        with col2:
            # Indicateur de progression
            completeness = calculate_completeness()
            render_progress_indicator(completeness)

            # Statistiques
            st.metric("Messages échangés", len(st.session_state.messages))
            st.metric("Questions posées", st.session_state.question_count)

        # Résultat du triage si terminé
        if st.session_state.session_complete:
            st.divider()
            st.subheader("🏥 Résultat du Triage")

            if st.session_state.triage_result:
                render_triage_result(st.session_state.triage_result)
            else:
                st.info(
                    "💡 Cliquez sur 'Forcer le triage' pour obtenir une évaluation basée sur la conversation."
                )


if __name__ == "__main__":
    render_interactive_page()
