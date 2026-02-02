import streamlit as st
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict


def render_entry_forms():
    """Affiche les formulaires d'identité et de constantes au début de la page."""
    st.info("📋 **Saisie des informations cliniques initiales**")
    # Initialiser les dictionnaires de sortie
    patient_info = {}
    vitals = {}

    col1, col2 = st.columns(2)

    with col1:
        with st.form("form_identite"):
            st.subheader("👤 Identité")
            num_patient = st.text_input("Numéro de patient", placeholder="Ex: PAT-2024-001")
            age = st.number_input("Âge du patient", min_value=0, max_value=120, value=30)
            genre = st.selectbox("Genre", ["Homme", "Femme", "Autre"])
            submit_id = st.form_submit_button("Enregistrer l'identité")
            if submit_id:
                st.session_state.id_data = {"num": num_patient, "age": age, "genre": genre}
                # Convertir genre en format H/F
                gender_code = "H" if genre == "Homme" else "F" if genre == "Femme" else "A"
                # Créer le dictionnaire patient_info
                st.session_state.patient_info = {
                    "patient_id": num_patient,
                    "age": age,
                    "sex": gender_code,
                }
                st.toast("Identité enregistrée")

    with col2:
        with st.form("form_constantes"):
            st.subheader("🌡️ Constantes")
            c1, c2 = st.columns(2)
            with c1:
                fc = st.number_input("FC (bpm)", min_value=0, max_value=250, value=75)
                fr = st.number_input("FR (/min)", min_value=0, max_value=60, value=16)
                temp = st.number_input(
                    "T° (°C)", min_value=30.0, max_value=45.0, value=37.0, step=0.1
                )
            with c2:
                tas = st.number_input("TA Systolique", min_value=40, max_value=250, value=120)
                tad = st.number_input("TA Diastolique", min_value=30, max_value=150, value=80)
                spo2 = st.number_input("SpO2 (%)", min_value=50, max_value=100, value=98)

            submit_const = st.form_submit_button("Enregistrer les constantes")
            if submit_const:
                st.session_state.const_data = {
                    "fc": fc,
                    "fr": fr,
                    "temp": temp,
                    "tas": tas,
                    "tad": tad,
                    "spo2": spo2,
                }

                # Créer le dictionnaire vitals (format standardisé pour ML/Chatbot)
                st.session_state.vitals = {
                    "Temperature": float(temp),
                    "FC": int(fc),
                    "TA_systolique": int(tas),
                    "TA_diastolique": int(tad),
                    "SpO2": int(spo2),
                    "FR": int(fr),
                }
                st.toast("Constantes enregistrées")
    # ══════════════════════════════════════════════════════════
    # RÉCUPÉRATION DES DONNÉES DEPUIS SESSION_STATE
    # ══════════════════════════════════════════════════════════
    # Récupérer patient_info
    if "patient_info" in st.session_state:
        patient_info = st.session_state.patient_info

    # Récupérer vitals
    if "vitals" in st.session_state:
        vitals = st.session_state.vitals

    return patient_info, vitals
