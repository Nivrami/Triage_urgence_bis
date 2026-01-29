"""
Page 1 : Génération de conversations automatiques.
"""

import streamlit as st
import json
import sys
from pathlib import Path

# Ajouter le chemin src au PYTHONPATH
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

from src.llm.llm_factory import LLMFactory
from src.workflows.simulation_workflow import SimulationWorkflow

# Configuration
st.set_page_config(
    page_title="Génération - Triage Urgences",
    page_icon="🎲",
    layout="wide"
)

# Titre
st.title("🎲 Génération de Conversations")

st.markdown("""
Générez des conversations automatiques entre un infirmier et un patient pour créer un dataset de triage.
""")

# Sidebar - Paramètres
with st.sidebar:
    st.header("⚙️ Paramètres")
    
    max_turns = st.slider(
        "Nombre max de questions",
        min_value=3,
        max_value=15,
        value=8,
        help="Nombre maximum de questions que l'infirmier peut poser"
    )
    
    st.markdown("---")
    
    st.markdown("""
    ### 💡 Astuce
    
    Laissez la pathologie vide pour une génération aléatoire !
    """)

# Initialisation session state
if 'conversations' not in st.session_state:
    st.session_state.conversations = []

if 'current_result' not in st.session_state:
    st.session_state.current_result = None

# Zone principale
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Configuration")
    
    # Input pathologie
    pathology_input = st.text_input(
        "Pathologie (optionnel)",
        placeholder="Ex: Homme de 65 ans avec infarctus",
        help="Laissez vide pour une génération aléatoire"
    )

with col2:
    st.subheader("🚀 Actions")
    
    # Boutons
    if st.button("🎲 Générer 1 conversation", type="primary"):
        with st.spinner("Génération en cours..."):
            try:
                # Initialiser LLM
                llm = LLMFactory.create("mistral", "mistral-large-latest")
                workflow = SimulationWorkflow(llm, max_turns=max_turns)
                
                # Générer
                pathology = pathology_input if pathology_input.strip() else None
                
                # Capturer stdout pour afficher logs
                import io
                from contextlib import redirect_stdout
                import time
                
                log_stream = io.StringIO()
                start_time = time.time()
                
                with redirect_stdout(log_stream):
                    result = workflow.run_simulation(pathology=pathology)
                
                duration = time.time() - start_time
                
                # Track génération
                try:
                    sys.path.insert(0, str(root_path / "src"))
                    from src.monitoring.metrics_tracker import get_tracker
                    
                    tracker = get_tracker()
                    
                    # Track latence génération
                    tracker.track_latency(
                        component="Generation",
                        operation="conversation",
                        duration=duration
                    )
                    
                    # Track appel API LLM (estimation)
                    # Approximation: ~500 tokens input, ~300 tokens output par conversation
                    tracker.track_api_call(
                        service="mistral",
                        model="mistral-large-latest",
                        tokens_input=500,
                        tokens_output=300,
                        latency=duration,
                        success=True
                    )
                except Exception as track_error:
                    print(f"Monitoring error: {track_error}")
                
                # Sauvegarder
                st.session_state.current_result = result
                st.session_state.conversations.append(workflow.export_for_ml())
                
                st.success(f"✅ Conversation générée en {duration:.2f}s!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")
    
    if st.button("📊 Générer 10 conversations"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            llm = LLMFactory.create("mistral", "mistral-large-latest")
            workflow = SimulationWorkflow(llm, max_turns=max_turns)
            
            import time
            total_duration = 0
            
            for i in range(10):
                status_text.text(f"Génération {i+1}/10...")
                progress_bar.progress((i + 1) / 10)
                
                import io
                from contextlib import redirect_stdout
                log_stream = io.StringIO()
                
                start_time = time.time()
                
                with redirect_stdout(log_stream):
                    result = workflow.run_simulation()
                
                duration = time.time() - start_time
                total_duration += duration
                
                st.session_state.conversations.append(workflow.export_for_ml())
                workflow.reset()
                
                # Track chaque génération
                try:
                    sys.path.insert(0, str(root_path / "src"))
                    from src.monitoring.metrics_tracker import get_tracker  
                    
                    tracker = get_tracker()
                    tracker.track_latency("Generation", "conversation", duration)
                    tracker.track_api_call(
                        service="mistral",
                        model="mistral-large-latest",
                        tokens_input=500,
                        tokens_output=300,
                        latency=duration,
                        success=True
                    )
                except:
                    pass
            
            st.success(f"✅ 10 conversations générées en {total_duration:.1f}s!")
            progress_bar.empty()
            status_text.empty()
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Erreur : {str(e)}")

# Affichage résultat
st.markdown("---")

if st.session_state.current_result:
    result = st.session_state.current_result
    
    st.subheader("📋 Dernière conversation générée")
    
    # Pathologie
    st.info(f"**Pathologie :** {result['pathology']}")
    
    # Extraire les données pour utilisation
    extr = result['extracted_patient']
    orig = result['original_patient']
    
    # ⭐ NOUVELLE SECTION : Génération des constantes
    st.markdown("---")
    st.markdown("### 🩺 Mesure des Constantes Vitales")
    
    with st.expander("ℹ️ Comment sont générées les constantes ?", expanded=False):
        st.markdown("""
        **Processus automatique :**
        
        1. 🧠 L'IA analyse la pathologie simulée
        2. 📊 Génère des constantes **cohérentes** avec cette pathologie
        3. ✅ L'infirmier "mesure" ces valeurs avec ses appareils
        
        **Exemple :** Si la pathologie est "infarctus", les constantes refléteront :
        - FC élevée (stress cardiaque)
        - SpO2 basse (problème oxygénation)
        - TA anormale, etc.
        """)
    
    st.markdown("**L'infirmier procède maintenant aux mesures avec ses appareils :**")
    
    # Afficher les constantes avec des badges colorés
    if orig.constantes:
        c = orig.constantes
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # FC
            fc_status = "🟢" if 60 <= c.fc <= 100 else "🟡" if 50 <= c.fc <= 120 else "🔴"
            fc_note = "Normale" if 60 <= c.fc <= 100 else "Légèrement élevée" if c.fc > 100 else "Basse"
            st.metric("💓 Fréquence Cardiaque (FC)", f"{c.fc} bpm", help=f"{fc_status} {fc_note}")
            
            # FR
            fr_status = "🟢" if 12 <= c.fr <= 20 else "🟡" if 10 <= c.fr <= 25 else "🔴"
            fr_note = "Normale" if 12 <= c.fr <= 20 else "Élevée" if c.fr > 20 else "Basse"
            st.metric("🫁 Fréquence Respiratoire (FR)", f"{c.fr} /min", help=f"{fr_status} {fr_note}")
        
        with col2:
            # SpO2
            spo2_status = "🟢" if c.spo2 >= 95 else "🟡" if c.spo2 >= 90 else "🔴"
            spo2_note = "Normale" if c.spo2 >= 95 else "Basse - Hypoxie" if c.spo2 < 90 else "Légèrement basse"
            st.metric("🩸 Saturation Oxygène (SpO2)", f"{c.spo2}%", help=f"{spo2_status} {spo2_note}")
            
            # Température
            temp_status = "🟢" if 36.5 <= c.temperature <= 37.5 else "🟡" if c.temperature <= 38.5 else "🔴"
            temp_note = "Normale" if 36.5 <= c.temperature <= 37.5 else "Fièvre" if c.temperature > 37.5 else "Hypothermie"
            st.metric("🌡️ Température", f"{c.temperature}°C", help=f"{temp_status} {temp_note}")
        
        with col3:
            # TA
            ta_status = "🟢" if 100 <= c.ta_systolique <= 140 and 60 <= c.ta_diastolique <= 90 else "🟡" if c.ta_systolique <= 160 else "🔴"
            ta_note = "Normale" if 100 <= c.ta_systolique <= 140 else "Élevée (HTA)" if c.ta_systolique > 140 else "Basse"
            st.metric("🩺 Tension Artérielle (TA)", f"{c.ta_systolique}/{c.ta_diastolique} mmHg", help=f"{ta_status} {ta_note}")
            
            # Info patient
            st.metric("👤 Patient", f"{extr.age or orig.age} ans, {extr.sexe or orig.sexe}")
        
        # Message explicatif
        st.info(f"""
        💡 **Ces constantes sont générées automatiquement par l'IA** pour être cohérentes avec la pathologie :  
        *"{result['pathology']}"*
        
        Elles seront utilisées par le modèle de Machine Learning pour prédire le niveau de gravité.
        """)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["💬 Conversation", "📊 Données Patient", "💾 Export ML"])
    
    with tab1:
        st.markdown("### 💬 Conversation complète")
        
        # Afficher conversation (SANS les explications)
        for msg in result['conversation'].messages:
            content = msg.content
            
            # Nettoyer les explications (tout ce qui suit "Explication", "Explications")
            if '"' in content:
                # Prendre seulement ce qui est avant les explications
                parts = content.split('"')
                if len(parts) > 1:
                    content = parts[0] + '"'
            
            # Enlever les explications qui commencent par "Explication"
            if "Explication" in content:
                content = content.split("Explication")[0].strip()
            
            if msg.role.value == "user":
                st.markdown(f"**👨‍⚕️ Infirmier :** {content}")
            else:
                st.markdown(f"**🤒 Patient :** {content}")
            st.markdown("")
    
    with tab2:
        st.markdown("### 📊 Informations extraites de la conversation")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            extr = result['extracted_patient']
            
            st.markdown("**👤 Identité**")
            st.write(f"- Âge : {extr.age} ans")
            st.write(f"- Sexe : {extr.sexe}")
            
            st.markdown("**🩺 Symptômes déclarés**")
            if extr.symptomes_exprimes:
                for s in extr.symptomes_exprimes:
                    st.write(f"- {s}")
            else:
                st.write("Aucun symptôme extrait")
            
            if extr.duree_symptomes:
                st.markdown(f"**⏱️ Durée :** {extr.duree_symptomes}")
        
        with col_b:
            st.markdown("**🏥 Antécédents médicaux**")
            if extr.antecedents:
                for a in extr.antecedents:
                    st.write(f"- {a}")
            else:
                st.write("Aucun antécédent déclaré")
            
            # Complétude
            completeness = result['completeness']
            st.markdown(f"**✅ Complétude de l'information**")
            st.progress(completeness['score'])
            st.write(f"{completeness['score']*100:.0f}% des informations collectées")
            
            if completeness['missing']:
                st.warning(f"Manquant : {', '.join(completeness['missing'])}")
        
        st.info("💡 Les **constantes vitales** (FC, SpO2, TA, etc.) sont affichées dans la section ci-dessus et proviennent de la génération automatique cohérente avec la pathologie.")
    
    with tab3:
        st.markdown("### 💾 Données pour Machine Learning")
        
        # Récupérer les données ML
        llm = LLMFactory.create("mistral", "mistral-large-latest")
        workflow = SimulationWorkflow(llm)
        workflow.original_patient = result['original_patient']
        workflow.extracted_patient = result['extracted_patient']
        workflow.pathology = result['pathology']
        workflow.conversation = result['conversation']
        
        ml_data = workflow.export_for_ml()
        
        st.json(ml_data)
        
        # Bouton télécharger
        json_str = json.dumps(ml_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Télécharger (JSON)",
            data=json_str,
            file_name="conversation_triage.json",
            mime="application/json"
        )
    
    # ⭐ NOUVELLE SECTION : Prédiction ML
    st.markdown("---")
    st.subheader("🤖 Prédiction de Gravité")
    
    if st.button("🔮 Prédire le niveau de gravité", type="primary"):
        # Charger le modèle
        import pickle
        import numpy as np
        import time
        
        model_path = root_path / "src" / "models" / "random_forest_simple.pkl"
        
        if not model_path.exists():
            st.error(f"❌ Modèle non trouvé ")
            
        else:
            with st.spinner("Chargement du modèle et prédiction..."):
                start_time = time.time()
                
                # Charger modèle
                with open(model_path, 'rb') as f:
                    clf = pickle.load(f)
                
                # Récupérer données ML
                llm = LLMFactory.create("mistral", "mistral-large-latest")
                workflow = SimulationWorkflow(llm)
                workflow.original_patient = result['original_patient']
                workflow.extracted_patient = result['extracted_patient']
                workflow.pathology = result['pathology']
                workflow.conversation = result['conversation']
                
                ml_data = workflow.export_for_ml()
                
                # Extraire constantes
                fc = ml_data.get('fc', 80)
                fr = ml_data.get('fr', 16)
                spo2 = ml_data.get('spo2', 98)
                ta_sys = ml_data.get('ta_systolique', 120)
                ta_dia = ml_data.get('ta_diastolique', 80)
                temp = ml_data.get('temperature', 37.0)
                age = ml_data.get('age', 50)
                sexe = ml_data.get('sexe', 'M')
                
                # Normaliser
                fc_norm = (fc - 70) / 30
                fr_norm = (fr - 16) / 5
                spo2_norm = (spo2 - 95) / 5
                ta_sys_norm = (ta_sys - 120) / 20
                ta_dia_norm = (ta_dia - 80) / 10
                temp_norm = (temp - 37) / 2
                age_norm = (age - 50) / 25
                sexe_encoded = 1 if sexe == 'M' else 0
                
                # Features
                features = np.array([[fc_norm, fr_norm, spo2_norm, ta_sys_norm, ta_dia_norm, temp_norm, age_norm, sexe_encoded]])
                
                # Prédiction
                prediction = clf.predict(features)[0]
                probas = clf.predict_proba(features)[0]
                proba_dict = dict(zip(clf.classes_, probas))
                
                duration = time.time() - start_time
                
                # Track prédiction ML
                try:
                    sys.path.insert(0, str(root_path / "src"))
                    from src.monitoring.metrics_tracker import get_tracker
                    
                    tracker = get_tracker()
                    
                    # Track prédiction
                    tracker.track_prediction(
                        severity=prediction,
                        age=age,
                        sex=sexe[0],
                        symptoms=[],
                        red_flags=[],
                        confidence=max(probas)
                    )
                    
                    # Track latence
                    tracker.track_latency(
                        component="Predictor_ML",
                        operation="predict",
                        duration=duration
                    )
                except:
                    pass
                
                # Affichage résultat
                colors = {
                    "ROUGE": "🔴",
                    "JAUNE": "🟡",
                    "VERT": "🟢",
                    "GRIS": "⚪"
                }
                
                descriptions = {
                    "ROUGE": "**Urgence vitale immédiate** - Pronostic vital engagé",
                    "JAUNE": "**Urgent mais non vital** - Prise en charge rapide nécessaire",
                    "VERT": "**Non urgent** - Peut attendre",
                    "GRIS": "**Ne nécessite pas les urgences**"
                }
                
                # Résultat principal
                st.success(f"### {colors[prediction]} Gravité prédite : **{prediction}**")
                st.info(descriptions[prediction])
                
                # Probabilités
                st.markdown("#### 📊 Probabilités par classe")
                
                col1, col2, col3, col4 = st.columns(4)
                
                for col, label in zip([col1, col2, col3, col4], ["ROUGE", "JAUNE", "VERT", "GRIS"]):
                    with col:
                        prob = proba_dict.get(label, 0)
                        st.metric(
                            label=f"{colors[label]} {label}",
                            value=f"{prob*100:.1f}%"
                        )
                        st.progress(prob)
                
                # Détails
                with st.expander("📋 Détails de la prédiction"):
                    st.markdown("**Constantes utilisées pour la prédiction :**")
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.write(f"- FC : {fc} bpm")
                        st.write(f"- FR : {fr} /min")
                        st.write(f"- SpO2 : {spo2}%")
                    
                    with col_b:
                        st.write(f"- TA : {ta_sys}/{ta_dia} mmHg")
                        st.write(f"- Temp : {temp}°C")
                    
                    with col_c:
                        st.write(f"- Âge : {age} ans")
                        st.write(f"- Sexe : {sexe}")
                    
                    st.markdown("**Features normalisées :**")
                    st.code(f"[{fc_norm:.3f}, {fr_norm:.3f}, {spo2_norm:.3f}, {ta_sys_norm:.3f}, {ta_dia_norm:.3f}, {temp_norm:.3f}, {age_norm:.3f}, {sexe_encoded}]")

# Dataset complet
st.markdown("---")
st.subheader("📊 Dataset complet")

if st.session_state.conversations:
    st.info(f"**{len(st.session_state.conversations)} conversations** générées")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Télécharger JSON
        dataset_json = json.dumps(st.session_state.conversations, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Télécharger dataset (JSON)",
            data=dataset_json,
            file_name="dataset_triage.json",
            mime="application/json"
        )
    
    with col2:
        # Télécharger CSV
        import pandas as pd
        df = pd.DataFrame(st.session_state.conversations)
        csv = df.to_csv(index=False, encoding='utf-8')
        st.download_button(
            label="📥 Télécharger dataset (CSV)",
            data=csv,
            file_name="dataset_triage.csv",
            mime="text/csv"
        )
    
    with col3:
        # Reset
        if st.button("🗑️ Effacer le dataset"):
            st.session_state.conversations = []
            st.session_state.current_result = None
            st.rerun()
    
    # Aperçu du dataset
    with st.expander("👁️ Aperçu du dataset"):
        import pandas as pd
        df = pd.DataFrame(st.session_state.conversations)
        st.dataframe(df, use_container_width=True)

else:
    st.info("Aucune conversation générée. Cliquez sur 'Générer' pour commencer !")