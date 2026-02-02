"""
Page Streamlit  - Chatbot + ML Predictor + Monitoring
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.rag.chatbot import TriageChatbotAPI
from src.rag.predictor import MLTriagePredictor
from src.rag.entry_forms import render_entry_forms
from src.utils.conversation_storage import get_storage

# Config
st.set_page_config(page_title="Chatbot Triage ML", page_icon="🏥", layout="wide")

st.title("🏥 Chatbot de Triage des Urgences")
st.markdown("*Assistant ML pour aide à la décision*")


# Afficher les formulaires et récupérer les données
result = render_entry_forms()

if result is not None:
    patient_info, vitals = result
    # On stocke dans le session_state pour que la sidebar y ait accès
    st.session_state["patient_info"] = patient_info
    st.session_state["vitals"] = vitals
else:
    # Si le formulaire n'est pas validé, on s'assure que les variables existent
    patient_info, vitals = {}, {}
    st.info("Veuillez remplir et valider le formulaire patient pour démarrer.")
    st.stop()  # Optionnel : arrête l'exécution ici tant que le formulaire n'est pas soumis

st.divider()

# Session
if "chatbot" not in st.session_state:
    # Charger RAG
    retriever = None
    with st.spinner("🔄 Chargement RAG..."):
        try:
            project_root = Path(__file__).resolve().parents[2]
            vector_db_path = project_root / "data" / "vector_db"

            from src.rag.vector_store import VectorStore, RAGRetriever

            vector_store = VectorStore(
                persist_directory=str(vector_db_path), collection_name="triage_medical"
            )
            retriever = RAGRetriever(vector_store=vector_store)

            st.session_state.predictor = MLTriagePredictor(rag_retriever=retriever)
            st.success("✅ RAG chargé avec succès")
        except Exception as e:
            st.warning(f"⚠️ RAG non chargé: {e}")
            st.session_state.predictor = MLTriagePredictor()

    # Créer chatbot AVEC le retriever RAG
    st.session_state.chatbot = TriageChatbotAPI(retriever=retriever)
    st.session_state.messages = []
    st.session_state.started = False
    st.session_state.prediction = None

bot = st.session_state.chatbot
predictor = st.session_state.predictor

# Synchroniser les données du formulaire avec l'état interne du bot.

if patient_info:
    bot.data.update(patient_info)
if vitals:
    # S'assurer que la clé 'vitals' existe dans bot.data
    if "vitals" not in bot.data or not isinstance(bot.data["vitals"], dict):
        bot.data["vitals"] = {}
    bot.data["vitals"].update(vitals)

# 'data' est maintenant l'état interne du bot, qui est la source de vérité
data = bot.data

# Sidebar
with st.sidebar:
    st.header("🧑‍⚕️ Dossier patient")

    st.subheader("Identité")

    # Utiliser 'data' (l'état du bot) comme source de vérité
    st.write(f"**N° patient:** {data.get('patient_id') or '—'}")
    st.write(f"**Âge:** {data.get('age') or '—'}")

    # Convertir le code sex en texte lisible
    sex_code = data.get("sex", "—")
    sex_display = (
        "Homme"
        if sex_code == "H"
        else "Femme" if sex_code == "F" else "Autre" if sex_code == "A" else "—"
    )
    st.write(f"**Genre:** {sex_display}")
    st.divider()

    st.subheader("Symptômes")
    if data["symptoms"]:
        for s in data["symptoms"]:
            st.write(f"• {s}")
    else:
        st.write("—")
    st.divider()

    st.subheader("Constantes vitales")

    # Utiliser les constantes vitales de l'état du bot
    vitals_display = data.get("vitals", {})

    # Calculer progression (5 constantes attendues)
    required_vitals = ["Temperature", "FC", "TA_systolique", "SpO2", "FR"]
    count = sum(1 for key in required_vitals if vitals_display.get(key) is not None)

    st.write(f"**Progression: {count}/5**")

    if vitals_display:
        if "Temperature" in vitals_display:
            st.write(f"🌡️ Temp: {vitals_display['Temperature']}°C")
        if "FC" in vitals_display:
            st.write(f"❤️ FC: {vitals_display['FC']} bpm")
        if "TA_systolique" in vitals_display:
            ta_dia = vitals_display.get("TA_diastolique", "?")
            st.write(f"💉 TA: {vitals_display['TA_systolique']}/{ta_dia}")
        if "SpO2" in vitals_display:
            st.write(f"🫁 SpO2: {vitals_display['SpO2']}%")
        if "FR" in vitals_display:
            st.write(f"🌬️ FR: {vitals_display['FR']}/min")
    else:
        st.write("—")
    st.divider()

    # Actions
    if st.button("🔄 Nouvelle conversation", use_container_width=True):
        bot.reset()
        st.session_state.messages = []
        st.session_state.started = False
        st.session_state.prediction = None
        st.rerun()

    ready = bot.is_ready_for_prediction()

    if st.button(
        "🎯 Obtenir prédiction ML",
        use_container_width=True,
        disabled=not ready,
        help="5/5 constantes requises",
    ):
        with st.spinner("🔮 Analyse ML en cours..."):
            summary = bot.get_summary()
            st.write(summary)
            st.session_state.prediction = predictor.predict(summary)
        st.rerun()

    # Section Sauvegarde
    st.divider()
    st.subheader("💾 Sauvegardes")

    # Bouton sauvegarder
    can_save = st.session_state.started and len(st.session_state.messages) > 0
    if st.button(
        "💾 Sauvegarder conversation",
        use_container_width=True,
        disabled=not can_save,
        help="Sauvegarde la conversation actuelle",
    ):
        storage = get_storage()
        conv_id = storage.save_conversation(
            messages=st.session_state.messages,
            patient_data=data,
            prediction=st.session_state.prediction,
        )
        st.success(f"Sauvegarde: {conv_id}")

    # Liste des conversations sauvegardees
    with st.expander("📂 Conversations sauvegardees"):
        storage = get_storage()
        conversations = storage.list_conversations(limit=10)

        if conversations:
            for conv in conversations:
                col_info, col_load = st.columns([3, 1])
                with col_info:
                    name = conv.get("patient_name", "?")
                    sev = conv.get("severity") or "—"
                    ts = conv.get("timestamp", "")[:10]
                    st.caption(f"{ts} | {name} | {sev}")
                with col_load:
                    if st.button("📥", key=f"load_{conv['id']}", help="Charger"):
                        loaded = storage.load_conversation(conv["id"])
                        if loaded:
                            # Restaurer la conversation
                            st.session_state.messages = loaded.get("messages", [])
                            patient = loaded.get("patient_data", {})
                            bot.data["name"] = patient.get("name")
                            bot.data["age"] = patient.get("age")
                            bot.data["sex"] = patient.get("sex")
                            bot.data["symptoms"] = patient.get("symptoms", [])
                            bot.data["vitals"] = patient.get("vitals", {})
                            st.session_state.prediction = loaded.get("prediction")
                            st.session_state.started = True
                            st.rerun()
        else:
            st.caption("Aucune sauvegarde")

# Conversation
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Conversation")

    if not st.session_state.started:
        if st.button("🚀 Démarrer", use_container_width=True):
            msg = bot.start()
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.session_state.started = True
            st.rerun()

    # Messages
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Input
    if st.session_state.started and not st.session_state.prediction:
        user_input = st.chat_input("Votre message...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = bot.chat(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

# Prédiction
with col2:
    st.subheader("🎯 Résultat ML")

    if st.session_state.prediction:
        r = st.session_state.prediction

        # Badge niveau
        st.markdown(
            f"""
        <div style="
            background-color:{r['color']};
            padding:20px;
            border-radius:10px;
            text-align:center;
            font-size:22px;
            font-weight:bold;
            color:{'white' if r['severity_level'] in ['ROUGE','GRIS'] else 'black'};
            margin-bottom:20px;
        ">{r['label']}</div>
        """,
            unsafe_allow_html=True,
        )

        st.info(f"**Action:** {r['action']}")

        # Drapeaux rouges
        if r.get("red_flags"):
            st.warning("⚠️ **Signes de gravité:**")
            for f in r["red_flags"]:
                st.markdown(f"- {f}")

        # Probabilités
        st.subheader("📊 Probabilités ML")
        for lvl in ["ROUGE", "JAUNE", "VERT", "GRIS"]:
            p = r["probabilities"].get(lvl, 0)
            st.progress(p, text=f"{lvl}: {p*100:.1f}%")

        st.metric("Confiance", f"{r['confidence']*100:.1f}%")

        # Features
        if r.get("features_used"):
            with st.expander("🔍 Features ML"):
                st.json(r["features_used"])

        # RAG Sources
        if r.get("rag_sources"):
            with st.expander("📚 Sources RAG"):
                for source in r["rag_sources"]:
                    st.markdown(f"- {source}")

        # Justification
        with st.expander("📋 Justification ML + RAG", expanded=True):
            st.markdown(r["justification"])

        # Export
        st.divider()
        if st.button("💾 Exporter rapport", use_container_width=True):
            export = f"# RAPPORT TRIAGE ML\n\n"
            export += f"## {r['label']}\n"
            export += f"**Action:** {r['action']}\n"
            export += f"**Confiance:** {r['confidence']*100:.1f}%\n\n"

            if r.get("red_flags"):
                export += "## Drapeaux rouges\n"
                for f in r["red_flags"]:
                    export += f"- {f}\n"

            export += "\n## Conversation\n\n"
            for m in st.session_state.messages:
                role = "Assistant" if m["role"] == "assistant" else "Patient"
                export += f"**{role}:** {m['content']}\n\n"

            st.download_button(
                "📥 Télécharger",
                export,
                "rapport_triage_ml.md",
                "text/markdown",
                use_container_width=True,
            )
    else:
        st.info(
            "💡 Complétez la conversation (5/5 constantes) puis cliquez 'Obtenir prédiction ML'"
        )

        with st.expander("❓ Aide"):
            st.markdown(
                """
            **Constantes requises (5/5):**
            - ✅ Température
            - ✅ Fréquence cardiaque (FC)
            - ✅ Tension artérielle (TA)
            - ✅ Saturation oxygène (SpO2)
            - ✅ Fréquence respiratoire (FR)

            Le bot vous guidera étape par étape.
            """
            )

st.divider()
st.caption(
    "🤖 ML (Random Forest) + 📚 RAG (Documents médicaux) + 🔮 Mistral API | ⚠️ Outil d'aide - ne remplace pas avis médical"
)
