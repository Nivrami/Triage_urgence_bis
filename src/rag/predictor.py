"""
Predictor ML + RAG - Random Forest + Documents médicaux
"""

import joblib
import numpy as np
import time
from pathlib import Path
from typing import Dict, List, Optional
# Import des règles d'urgence
try:
    from src.rag.EmergencyRules import check_vital_emergency_rules
except ImportError:
    print("[WARN] EmergencyRules non disponible")
    check_vital_emergency_rules = None


class MLTriagePredictor:
    """Prédit avec Random Forest + enrichissement RAG."""

    def __init__(self, model_path: str = None, rag_retriever=None):
        # Modèle ML
        if model_path is None:
            model_path = Path(__file__).parent.parent / "models" / "random_forest_simple.pkl"

        try:
            self.model = joblib.load(model_path)
            print("[OK] Modele ML charge")
        except Exception as e:
            print(f"[ERREUR] Modele: {e}")
            self.model = None

        # RAG
        self.rag = rag_retriever
        if self.rag:
            print("[OK] RAG active")
        else:
            print("[WARN] RAG desactive")

        self.severity_levels = {
            "ROUGE": {"label": "🔴 URGENCE VITALE", "action": "APPELER LE 15", "color": "#FF0000"},
            "JAUNE": {"label": "🟡 URGENCE", "action": "Urgences dans l'heure", "color": "#FFD700"},
            "VERT": {"label": "🟢 NON URGENT", "action": "Consultation 24-48h", "color": "#00FF00"},
            "GRIS": {"label": "⚪ PAS D'URGENCE", "action": "RDV médecin", "color": "#808080"},
        }

    def predict(self, chatbot_summary: Dict) -> Dict:
        """
        Prédiction ML + RAG avec données enrichies.
        
        Args:
            chatbot_summary: {
                'patient_info': {'patient_id': str, 'age': int, 'sex': str},
                'vitals': {'Temperature': float, 'FC': int, ...},
                'symptoms': List[str],
                'medical_history': List[str],
                'current_medications': List[str],
                'allergies': List[str],
                'symptom_duration': str,
                'messages': List[str]
            }
        """
        start = time.time()

        # Extraire données
        patient_info = chatbot_summary.get("patient_info", {})
        vitals = chatbot_summary.get("vitals", {})
        symptoms = chatbot_summary.get("symptoms", [])
        medical_history = chatbot_summary.get("medical_history", [])
        medications = chatbot_summary.get("current_medications", [])
        allergies = chatbot_summary.get("allergies", [])
        duration = chatbot_summary.get("symptom_duration")
       
        #  VÉRIFICATION RÈGLES D'URGENCE VITALE
       
        is_vital_emergency, red_flags = self._check_vital_emergency_rules(
            patient_info, vitals, symptoms, medical_history, duration
        )

        if is_vital_emergency:
            # Urgence vitale détectée → ROUGE immédiat
            result = {
                "severity_level": "ROUGE",
                "label": self.severity_levels["ROUGE"]["label"],
                "action": self.severity_levels["ROUGE"]["action"],
                "color": self.severity_levels["ROUGE"]["color"],
                "red_flags": red_flags,
                "justification": self._justify_vital_emergency(red_flags, patient_info, vitals, symptoms),
                "probabilities": {"ROUGE": 1.0, "JAUNE": 0.0, "VERT": 0.0, "GRIS": 0.0}, 
                "confidence": 1.0,
                "features_used": self._build_features_dict(patient_info, vitals),
                "rag_sources": [],
                "method": "Règles d'urgence vitale",
            }
            
            self._track(result, patient_info, time.time() - start)
            return result
       
        # ML PREDICTION
        features = self._prep_features(patient_info, vitals)

        if not self.model or not features:
            return self._fallback(symptoms, vitals, medical_history)

       try:
            pred = self.model.predict([features])[0]
            probas = self.model.predict_proba([features])[0]

            classes = ["GRIS", "JAUNE", "ROUGE", "VERT"]
            severity = classes[pred] if isinstance(pred, (int, np.integer)) else pred

            proba_dict = {classes[i]: float(probas[i]) for i in range(4)}
            confidence = float(max(probas))

        except Exception as e:
            print(f"[ERREUR] Prédiction ML: {e}")
            return self._fallback(symptoms, vitals, medical_history)

        # AJUSTEMENT DU CONTEXTE MEDICAL
        severity, adjusted_flags = self._adjust_severity_with_context(
            severity, red_flags, medical_history, medications, duration, proba_dict
        )

        # RAG ENRICHMENT
        rag_data = self._rag_enrich(severity, symptoms, adjusted_flags, medical_history)

        # Result
        result = {
            "severity_level": severity,
            "label": self.severity_levels[severity]["label"],
            "action": self.severity_levels[severity]["action"],
            "color": self.severity_levels[severity]["color"],
            "red_flags": ajusted_flags,
            "justification": self._justify(severity, ajusted_flags, features, symptoms, rag_data, medical_history, medications, allergies, duration),
            "probabilities": proba_dict,
            "confidence": confidence,
            "features_used": self._build_features_dict(patient_info, vitals),
            "rag_sources": rag_data.get("sources", []) if rag_data else [],
        }

        # Track
        self._track(result, patient, time.time() - start)

        return result

    def _rag_enrich(self, severity: str, symptoms: List[str], flags: List[str]) -> Dict:
        """RAG enrichissement."""
        if not self.rag:
            return None

        try:
            # Query ciblée
            q_parts = [f"protocole niveau {severity}"]

            if symptoms:
                q_parts.append(", ".join(symptoms[:2]))

            if flags:
                q_parts.append(flags[0])

            query = " ".join(q_parts)

            # Retrieve
            start = time.time()
            context = self.rag.retrieve_context(query, top_k=3)

            # Track RAG latency
            try:
                import sys
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).parent.parent))
                from src.monitoring.metrics_tracker import get_tracker

                get_tracker().track_latency("RAG", "retrieve", time.time() - start)
            except:
                pass

            # Nettoyer et extraire contenu pertinent
            clean_context = self._clean_rag_context(context, severity)

            return {"context": clean_context, "sources": [f"Protocoles {severity}"]}
        except Exception as e:
            print(f"Erreur RAG: {e}")
            return None

    def _clean_rag_context(self, context: str, severity: str) -> str:
        """Nettoie contexte RAG pour garder contenu pertinent."""
        # Enlever les tags [Source X: ...]
        import re

        context = re.sub(r"\[Source \d+:.*?\]", "", context)

        # Garder lignes avec contenu (pas juste titres emoji)
        lines = context.split("\n")
        content_lines = []

        for line in lines:
            line = line.strip()
            # Ignorer lignes vides ou juste emojis/titres
            if not line:
                continue
            if line.startswith("#"):
                continue
            # Garder lignes avec contenu substantiel
            if (
                len(line) > 20
                or line.startswith("-")
                or line.startswith("✅")
                or line.startswith("•")
            ):
                content_lines.append(line)

        # Limiter à ~400 chars de contenu utile
        result = "\n".join(content_lines[:15])

        if len(result) > 400:
            result = result[:400] + "..."

        # Si trop court, ajouter message générique
        if len(result) < 50:
            defaults = {
                "ROUGE": "Urgence vitale: appeler SMUR, surveillance continue, ne pas attendre.",
                "JAUNE": "Urgence: consultation dans l'heure, surveiller constantes, réévaluer rapidement.",
                "VERT": "Non urgent: consultation dans 24-48h, surveillance domicile possible.",
                "GRIS": "Pas d'urgence: RDV médecin traitant, conseils généraux.",
            }
            result = defaults.get(severity, "Protocole standard applicable.")

        return result

    def _prep_features(self, patient: Dict, vitals: Dict) -> List[float]:
        """[FC, FR, SpO2, TA_sys, TA_dia, Temp, Age, Sex]."""
        try:
            return [
                vitals.get("FC", 75),
                vitals.get("FR", 16),
                vitals.get("SpO2", 98),
                vitals.get("TA_systolique", 120),
                vitals.get("TA_diastolique", 80),
                vitals.get("Temperature", 37.0),
                patient.get("age", 40),
                1 if patient.get("genre") in ["Homme", "H"] else 0,
            ]
        except:
            return None

    
    def _justify(
        self, severity: str, flags: List[str], features: List[float], symptoms: List[str], rag: Dict
    ) -> str:
        """Justification."""
        j = f"**{self.severity_levels[severity]['label']}**\n\n"
        j += "**🤖 Analyse ML + 📚 Protocoles RAG**\n\n"

        if flags:
            j += "**⚠️ Signes de gravité :**\n"
            for f in flags:
                j += f"- {f}\n"
            j += "\n"

        j += "**📊 Constantes (ML) :**\n"
        j += f"- FC: {features[0]:.0f} bpm, FR: {features[1]:.0f}/min\n"
        j += f"- SpO2: {features[2]:.0f}%, TA: {features[3]:.0f}/{features[4]:.0f}\n"
        j += f"- Temp: {features[5]:.1f}°C\n"

        if symptoms:
            j += f"\n**Symptômes:** {', '.join(symptoms)}\n"

        # RAG - Afficher contenu nettoyé
        if rag and rag.get("context"):
            j += "\n---\n\n**📚 Recommandations protocoles (RAG) :**\n\n"
            j += rag["context"]
            if rag.get("sources"):
                j += f"\n\n*Réf: {', '.join(rag['sources'])}*"

        return j

    def _fallback(self, symptoms: List[str], vitals: Dict) -> Dict:
        """Fallback."""
        flags = self._red_flags(vitals, symptoms)

        if len(flags) >= 3:
            sev = "ROUGE"
        elif len(flags) >= 1:
            sev = "JAUNE"
        elif symptoms:
            sev = "VERT"
        else:
            sev = "GRIS"

        return {
            "severity_level": sev,
            "label": self.severity_levels[sev]["label"],
            "action": self.severity_levels[sev]["action"],
            "color": self.severity_levels[sev]["color"],
            "red_flags": flags,
            "justification": f"Règles\n\n{', '.join(flags) or 'Aucun signe'}",
            "probabilities": {sev: 1.0},
            "confidence": 0.5,
            "rag_sources": [],
        }

    def _track(self, result: Dict, patient: Dict, duration: float):
        """Track."""
        try:
            import sys
            from pathlib import Path

            sys.path.insert(0, str(Path(__file__).parent.parent))
            from src.monitoring.metrics_tracker import get_tracker

            t = get_tracker()

            t.track_prediction(
                severity=result["severity_level"],
                age=patient.get("age", 0),
                sex=patient.get("sex", "?")[0] if patient.get("sex") else "?",
                symptoms=[],
                red_flags=result["red_flags"],
                confidence=result["confidence"],
            )

            t.track_latency("Predictor_ML_RAG", "predict", duration)
        except:
            pass

    def predict_with_probabilities(self, chatbot_summary: Dict) -> Dict:
        return self.predict(chatbot_summary)
