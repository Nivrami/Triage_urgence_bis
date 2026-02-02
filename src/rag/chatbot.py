"""
Chatbot Final - Mistral API ROBUSTE avec Monitoring
Version mise à jour avec patient_info et vitals
"""

import re
import time
import os
from typing import Dict, Optional
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()


class TriageChatbotAPI:
    """Chatbot Mistral API robuste avec tracking complet."""

    def __init__(self, api_key: str = None, retriever=None, patient_data: Dict = None):
        """
        Args:
            api_key: Clé API Mistral
            retriever: RAG retriever pour contexte médical
            patient_data: Données pré-remplies du formulaire {
                'patient_id': str,
                'age': int,
                'sex': 'H' ou 'F' ou 'A',
                'vitals': {
                    'Temperature': float,
                    'FC': int,
                    'TA_systolique': int,
                    'TA_diastolique': int,
                    'SpO2': int,
                    'FR': int
                }
            }
        """
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.retriever = retriever
        self.patient_data = patient_data 
        
        if self.api_key:
            self.client = Mistral(api_key=self.api_key)
            self.use_api = True
            print("[OK] Mistral API activee")
        else:
            self.use_api = False
            print("[WARN] Mode regles (sans API)")
        
        def reset(self):
        """Reset avec données formulaire pré-remplies."""
            patient_data = self.patient_data 
    
            self.data = {
            # Données du FORMULAIRE (pré-remplies)
            "patient_id": patient_data.get("patient_id") if patient_data else None,
            "age": patient_data.get("age") if patient_data else None,
            "sex": patient_data.get("sex") if patient_data else None,
            "vitals": patient_data.get("vitals", {}) if patient_data else {}
            }

        # Initialiser avec données formulaire
        self.reset()

    def start(self) -> str:
        """Message d'accueil personnalisé avec données du formulaire."""
        age = self.data.get('age', '?')
        sex_code = self.data.get('sex', '?')
        
        # Conversion H/F/A → texte
        gender_display = (
            "Homme" if sex_code == "H" 
            else "Femme" if sex_code == "F" 
            else "Patient"
        )
        
        patient_id = self.data.get('patient_id', '?')
        
        
        msg = f"Bonjour. Je vais vous poser quelques questions sur vos symptômes.\n\n"
        msg += f"**Dossier patient N°{patient_id}** - {gender_display}, {age} ans\n"
        msg += f"Constantes enregistrées ✓\n\n"
        msg += f"**Quel est votre symptôme principal aujourd'hui ?**"
        
        return msg

    def chat(self, msg: str) -> str:
        """Chat principal avec tracking."""
        start = time.time()
        self.data["messages"].append({"role": "user", "content": msg})

        # Extraire UNIQUEMENT symptômes et historique
        self._extract_symptoms_and_history(msg)

        # Déterminer étape suivante
        next_step = self._get_next_step()

         # Générer réponse
        if self.use_api and next_step != "symptoms":
            response = self._ask_with_api(next_step)
        else:
            response = self._ask_with_rules(next_step)

        self.data["messages"].append({"role": "assistant", "content": response})

        # Track latence
        self._track_latency(time.time() - start)

        return response

    def _get_next_step(self) -> str:
        """Détermine prochaine étape unique."""
        if not self.data.get("symptoms"):
            return "symptoms"
        
        if not self.data.get("medical_history_asked"):
            return "medical_history"
        
        if not self.data.get("current_medications_asked"):
            return "medications"
        
        if not self.data.get("allergies_asked"):
            return "allergies"
        
        if not self.data.get("symptom_duration_asked"):
            return "duration"

        return "done"
        
    def _ask_with_api(self, step: str) -> str:
        """Appel Mistral avec enrichissement RAG."""
        try:
            # Récupérer contexte RAG si symptômes présents
            rag_context = ""
            if self.retriever and self.data.get("symptoms"):
                try:
                    query = " ".join(self.data["symptoms"])
                    # Supporte les deux interfaces (RAGRetriever et Retriever)
                    if hasattr(self.retriever, "retrieve_context"):
                        rag_context = self.retriever.retrieve_context(query=query, top_k=3)
                    elif hasattr(self.retriever, "retrieve_and_format"):
                        rag_context = self.retriever.retrieve_and_format(
                            query=query, top_k=3, max_tokens=500
                        )
                    else:
                        rag_context = ""
                except Exception as e:
                    print(f"RAG Error: {e}")
                    rag_context = ""

            # Prompts système
            prompts = {
                "symptoms": """Tu es un assistant médical empathique en service d'urgence.
Le patient va décrire ses symptômes principaux.
Écoute attentivement et reformule pour confirmer que tu as bien compris.
Pose une question ouverte pour approfondir si nécessaire.
Reste bref (2-3 phrases max).""",

                "medical_history": """Le patient a décrit ses symptômes.
Demande maintenant s'il a des antécédents médicaux importants :
- Maladies chroniques (diabète, hypertension, asthme, etc.)
- Opérations chirurgicales passées
- Hospitalisations récentes
Formule une question claire et empathique (1-2 phrases).""",

                "medications": """Demande au patient s'il prend actuellement des médicaments.
Si oui, lesquels et depuis quand.
Sois concis et professionnel (1-2 phrases).""",

                "allergies": """Demande au patient s'il a des allergies connues :
- Médicamenteuses
- Alimentaires
- Autres (latex, piqûres, etc.)
Une question directe et claire.""",

                "duration": """Demande depuis combien de temps les symptômes ont commencé :
- durée depuis le début des symptômes ou date de début
- Évolution (stable, aggravation, amélioration)
- Facteurs déclenchants éventuels
Reste bref (2-3 questions max).""",

                "done": """Toutes les informations cliniques sont collectées.
Remercie le patient et informe-le que son dossier est maintenant complet.
L'équipe médicale va analyser les données pour établir le niveau de priorité.
Sois rassurant et professionnel (2-3 phrases).""",
            }

            system_prompt = prompts.get(step, "Guide le patient avec empathie.")

            # Ajouter le contexte RAG au prompt si disponible
            if rag_context:
                system_prompt += f"""

Contexte médical de référence (utilise ces informations pour guider tes questions):
{rag_context}"""

            # Contexte des données déjà collectées
            context = self._build_context()

            # Appel API Mistral
            start = time.time()
            resp = self.client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Contexte patient: {context}\n\nQuelle est ta question ?",
                    },
                ],
                temperature=0.4,
                max_tokens=150,
            )

            # Track API call
            self._track_api(
                resp.usage.prompt_tokens, resp.usage.completion_tokens, time.time() - start
            )

            response = resp.choices[0].message.content.strip()

            # Nettoyer la réponse si trop longue
            if len(response) > 250:
                response = response[:250] + "..."

            return response

        except Exception as e:
            print(f"API Error: {e}")
            return self._ask_with_rules(step)

    def _build_context(self) -> str:
        """Construit contexte pour Mistral."""
        parts = []

       # Identité (du formulaire)
        if self.data.get("patient_id"):
            parts.append(f"ID: {self.data['patient_id']}")
        if self.data.get("age"):
            parts.append(f"Âge: {self.data['age']} ans")
        if self.data.get("sex"):
            sex_display = (
                "Homme" if self.data["sex"] == "H" 
                else "Femme" if self.data["sex"] == "F" 
                else "Patient"
            )
            parts.append(f"Genre: {sex_display}")
            
        if self.data.get("symptoms"):
            parts.append(f"Symptômes: {', '.join(self.data['symptoms'])}")

        v = self.data["vitals"]
        vitals_collected = []
        if "Temperature" in v:
            vitals_collected.append(f"T°={v['Temperature']}°C")
        if "FC" in v:
            vitals_collected.append(f"FC={v['FC']}bpm")
        if "TA_systolique" in v:
            vitals_collected.append(f"TA={v['TA_systolique']}/{v.get('TA_diastolique', '?')}")
        if "SpO2" in v:
            vitals_collected.append(f"SpO2={v['SpO2']}%")
        if "FR" in v:
            vitals_collected.append(f"FR={v['FR']}/min")

        if vitals_collected:
            parts.append(f"Constantes: {', '.join(vitals_collected)}")
            
        # Symptômes collectés par chatbot
        if self.data.get("symptoms"):
            parts.append(f"Symptômes: {', '.join(self.data['symptoms'])}")

        # Historique médical
        if self.data.get("medical_history"):
            parts.append(f"ATCD: {', '.join(self.data['medical_history'])}")
        
        # Médicaments
        if self.data.get("current_medications"):
            parts.append(f"Traitement: {', '.join(self.data['current_medications'])}")
        
        # Allergies
        if self.data.get("allergies"):
            parts.append(f"Allergies: {', '.join(self.data['allergies'])}")
        
        # Durée symptômes
        if self.data.get("symptom_duration"):
            parts.append(f"Durée: {self.data['symptom_duration']}")

        return " | ".join(parts) if parts else "Nouveau patient"

    def _ask_with_rules(self, step: str) -> str:
        """Fallback règles."""
        responses = {
            "symptoms": "Décrivez vos symptômes principaux.\nExemple : douleur thoracique intense, essoufflement",
            "medical_history": "Avez-vous des antécédents médicaux importants ?\n(diabète, hypertension, chirurgies...)",
            "medications": "Prenez-vous actuellement des médicaments ?\nSi oui, lesquels ?",
            "allergies": "Avez-vous des allergies connues ?\n(médicaments, aliments, latex...)",
            "duration": "Depuis combien de temps avez-vous ces symptômes ?\nExemple : depuis ce matin, depuis 2 jours",
            "done": " Dossier complet. L'équipe médicale va analyser votre cas. Cliquez 'Obtenir prédiction ML'.",
        }
        return responses.get(step, "Erreur")

    def _extract_symptoms_and_history(self, msg: str):
        """Extraction UNIQUEMENT symptômes et historique (pas d'identité ni constantes)."""
        ml = msg.lower()

        # Symptômes - dictionnaire étendu par catégorie médicale
        symp = {
            # ══════════════════════════════════════════════════════════
            # NEUROLOGIQUE
            # ══════════════════════════════════════════════════════════
            r"t[eéèê]te|c[ée]phal|migraine": "Céphalée",
            r"vertige|tournis|[ée]tourdissement": "Vertiges",
            r"syncope|[ée]vanoui|perte\s*de\s*connaissance": "Syncope",
            r"convulsion|crise|[ée]pilep": "Convulsions",
            r"confusion|d[ée]sorient": "Confusion",
            r"paralys|faiblesse.*(bras|jambe|visage)": "Déficit neurologique",
            r"trouble.*parole|difficult.*parler": "Trouble de la parole",
            r"trouble.*vision|voi[rt]\s*flou|double": "Trouble visuel",
            # ══════════════════════════════════════════════════════════
            # CARDIOVASCULAIRE
            # ══════════════════════════════════════════════════════════
            r"poitrine|thorax|oppression": "Douleur thoracique",
            r"palpitation|cœur\s*bat|tachycardie": "Palpitations",
            r"jambe.*gonfl|œd[èe]me|enfl[ée]": "Œdème",
            # ══════════════════════════════════════════════════════════
            # RESPIRATOIRE
            # ══════════════════════════════════════════════════════════
            r"essouffl[éeè]|dyspn[ée]e|respir.*difficile": "Dyspnée",
            r"toux": "Toux",
            r"crachats?|expectoration": "Expectorations",
            r"[ée]touff|suffoqu": "Détresse respiratoire",
            # ══════════════════════════════════════════════════════════
            # DIGESTIF
            # ══════════════════════════════════════════════════════════
            r"ventre|abdomen|estomac": "Douleur abdominale",
            r"naus[ée]e|envie\s*de\s*vomir|mal\s*au\s*cœur": "Nausées",
            r"vomi|r[ée]gurgit": "Vomissements",
            r"diarrh[ée]e|selles?\s*liquides?": "Diarrhée",
            r"constip|bloqu[ée]|transit": "Constipation",
            r"sang.*selles|rectorragie": "Rectorragie",
            r"br[uû]lure.*estomac|reflux|acidit": "Reflux gastrique",
            r"difficult[ée].*avaler|dysphagie": "Dysphagie",
            # ══════════════════════════════════════════════════════════
            # URINAIRE
            # ══════════════════════════════════════════════════════════
            r"br[uû]l.*urin|cystite": "Brûlures mictionnelles",
            r"sang.*urine|h[ée]maturie": "Hématurie",
            r"envie.*fr[ée]quente|pollakiurie": "Pollakiurie",
            r"difficult[ée].*uriner|r[ée]tention": "Dysurie",
            # ══════════════════════════════════════════════════════════
            # MUSCULO-SQUELETTIQUE
            # ══════════════════════════════════════════════════════════
            r"dos|lombaire|lumbago|sciatique": "Lombalgie",
            r"genou": "Gonalgie",
            r"hanche": "Coxalgie",
            r"cheville|entorse": "Douleur cheville",
            r"[ée]paule": "Omalgie",
            r"nuque|cervical|torticolis": "Cervicalgie",
            r"articulation|arthr": "Arthralgie",
            r"fracture|cass[ée]": "Traumatisme osseux",
            r"bras": "Douleur membre supérieur",
            r"jambe|mollet": "Douleur membre inférieur",
            # ══════════════════════════════════════════════════════════
            # ORL / OPHTALMOLOGIE
            # ══════════════════════════════════════════════════════════
            r"gorge|angine|pharyn": "Odynophagie",
            r"oreille|otite|acouph[èe]ne": "Otalgie",
            r"nez.*bouch|rhume|sinusite": "Rhinite/Sinusite",
            r"saign.*nez|[ée]pistaxis": "Épistaxis",
            r"œil.*rouge|conjonctiv": "Conjonctivite",
            r"œil.*douleur": "Douleur oculaire",
            # ══════════════════════════════════════════════════════════
            # DERMATOLOGIE
            # ══════════════════════════════════════════════════════════
            r"[ée]ruption|bouton|rash|plaques?": "Éruption cutanée",
            r"d[ée]mangeaison|prurit|gratt": "Prurit",
            r"br[uû]lure(?!.*estomac)": "Brûlure",
            r"plaie|coupure|blessure": "Plaie",
            r"abc[èe]s|furoncle": "Abcès",
            # ══════════════════════════════════════════════════════════
            # GÉNÉRAL / PSYCHIATRIQUE
            # ══════════════════════════════════════════════════════════
            r"fi[eéèê]vre|temp[éeè]rature|frisson": "Fièvre",
            r"fatigue|[ée]puis[ée]|asth[ée]nie": "Asthénie",
            r"perte.*poids|amaigri": "Amaigrissement",
            r"sueur|transpir": "Sueurs",
            r"insomnie|dort.*mal|sommeil": "Trouble du sommeil",
            r"anxi[ée]t[ée]|stress|angoiss|panique": "Anxiété",
            r"allergi|r[ée]action|urticaire": "Réaction allergique",
            r"d[ée]prim|triste|moral": "Syndrome dépressif",
        }

        for p, s in symp.items():
            if s and re.search(p, ml):  # Ignorer les patterns avec valeur vide
                if s not in self.data["symptoms"]:
                    self.data["symptoms"].append(s)
         # ══════════════════════════════════════════════════════════
        # ANTÉCÉDENTS MÉDICAUX
        # ══════════════════════════════════════════════════════════
        medical_history_patterns = {
            r"diab[èe]te|glyc[ée]mie": "Diabète",
            r"hypertension|hta|tension\s*[ée]lev": "Hypertension",
            r"asthme": "Asthme",
            r"cancer|tumeur|chimioth[ée]rapie": "Antécédent de cancer",
            r"infarctus|crise\s*cardiaque": "Infarctus du myocarde",
            r"avc|accident.*vasculaire.*c[ée]r[ée]bral": "AVC",
            r"insuffisance.*cardiaque": "Insuffisance cardiaque",
            r"insuffisance.*r[ée]nale": "Insuffisance rénale",
            r"cirrhose|foie": "Hépatopathie",
            r"[ée]pilepsie": "Épilepsie",
            r"thyro[ïi]de": "Trouble thyroïdien",
            r"cholest[ée]rol": "Dyslipidémie",
            r"op[ée]r[ée]|chirurgie|intervention": "Chirurgie antérieure",
        }

        for pattern, history in medical_history_patterns.items():
            if re.search(pattern, ml):
                if history not in self.data["medical_history"]:
                    self.data["medical_history"].append(history)
                self.data["medical_history_asked"] = True
        
        # Détection négative (pas d'antécédent)
        if re.search(r"\b(non|aucun|pas|rien|jamais)\b.*\b(ant[ée]c[ée]dent|maladie|chirurgie)", ml):
            if not self.data["medical_history"]:
                self.data["medical_history"].append("Aucun antécédent déclaré")
            self.data["medical_history_asked"] = True
        # ══════════════════════════════════════════════════════════
        # MÉDICAMENTS
        # ══════════════════════════════════════════════════════════
        medication_patterns = {
            r"doliprane|parac[ée]tamol": "Paracétamol",
            r"ibuprofène|advil|nurofen": "Ibuprofène",
            r"aspirine": "Aspirine",
            r"m[ée]tformine": "Metformine",
            r"insuline": "Insuline",
            r"ramipril|[ée]nalapril|.*pril\b": "IEC",
            r"amlodipine|.*dipine\b": "Inhibiteur calcique",
            r"atorvastatine|simvastatine|.*statine\b": "Statine",
            r"l[ée]vothyrox|thyroxine": "Lévothyroxine",
            r"ventoline|salbutamol": "Bronchodilatateur",
            r"cortisone|prednisone": "Corticoïde",
            r"anticoagulant|warfarine|xarelto": "Anticoagulant",
            r"antid[ée]presseur": "Antidépresseur",
        }

        for pattern, med in medication_patterns.items():
            if re.search(pattern, ml):
                if med not in self.data["current_medications"]:
                    self.data["current_medications"].append(med)
                self.data["current_medications_asked"] = True

        # Détection négative
        if re.search(r"\b(non|aucun|pas|rien)\b.*(m[ée]dicament|traitement|comprim)", ml):
            if not self.data["current_medications"]:
                self.data["current_medications"].append("Aucun traitement")
            self.data["current_medications_asked"] = True

        # ══════════════════════════════════════════════════════════
        # ALLERGIES
        # ══════════════════════════════════════════════════════════
        allergy_patterns = {
            r"p[ée]nicilline": "Pénicilline",
            r"aspirine": "Aspirine",
            r"iode": "Iode",
            r"latex": "Latex",
            r"arachide|cacahu[èe]te": "Arachide",
            r"gluten": "Gluten",
            r"lactose|lait": "Lactose",
            r"pollen": "Pollen",
            r"acarien": "Acariens",
        }

        for pattern, allergy in allergy_patterns.items():
            if re.search(pattern, ml):
                if allergy not in self.data["allergies"]:
                    self.data["allergies"].append(allergy)
                self.data["allergies_asked"] = True

        # Détection négative
        if re.search(r"\b(non|aucune|pas)\b.*allergi", ml):
            if not self.data["allergies"]:
                self.data["allergies"].append("Aucune allergie connue")
            self.data["allergies_asked"] = True

        # Température - exiger contexte (°, degré, température, temp)
        if "Temperature" not in self.data["vitals"]:
            m = re.search(r"(\d{2}[.,]?\d?)\s*(?:°|degr|temp)", ml)
            if m:
                t = float(m.group(1).replace(",", "."))
                if 35 <= t <= 43:
                    self.data["vitals"]["Temperature"] = t

        # ══════════════════════════════════════════════════════════
        # DURÉE DES SYMPTÔMES
        # ══════════════════════════════════════════════════════════
        duration_patterns = [
            (r"depuis\s*(\d+)\s*heure", lambda m: f"{m.group(1)}h"),
            (r"depuis\s*(\d+)\s*jour", lambda m: f"{m.group(1)}j"),
            (r"depuis\s*(\d+)\s*semaine", lambda m: f"{m.group(1)} semaine(s)"),
            (r"depuis\s*ce\s*matin", lambda m: "Ce matin"),
            (r"depuis\s*hier", lambda m: "Hier"),
            (r"depuis\s*(\d+)\s*mois", lambda m: f"{m.group(1)} mois"),
            (r"brutal|soudain|d'un\s*coup", lambda m: "Début brutal"),
            (r"progressif|petit\s*à\s*petit", lambda m: "Début progressif"),
        ]

        for pattern, extractor in duration_patterns:
            match = re.search(pattern, ml)
            if match and not self.data.get("symptom_duration"):
                self.data["symptom_duration"] = extractor(match)
                self.data["symptom_duration_asked"] = True
                break


    def _track_latency(self, duration: float):
        """Track latence chatbot."""
        try:
            import sys
            from pathlib import Path

            sys.path.insert(0, str(Path(__file__).parent.parent))
            from src.monitoring.metrics_tracker import get_tracker

            get_tracker().track_latency("Chatbot", "chat", duration)
        except:
            pass

    def _track_api(self, tokens_in: int, tokens_out: int, latency: float):
        """Track appel API Mistral."""
        try:
            import sys
            from pathlib import Path

            sys.path.insert(0, str(Path(__file__).parent.parent))
            from src.monitoring.metrics_tracker import get_tracker

            get_tracker().track_api_call(
                service="mistral",
                model="mistral-small-latest",
                tokens_input=tokens_in,
                tokens_output=tokens_out,
                latency=latency,
                success=True,
            )
        except:
            pass

    def is_ready_for_prediction(self) -> bool:
        """Vérifie si collecte complète (symptômes + historique minimal)."""
        return (
            self.data.get("age")  # Du formulaire
            and self.data.get("sex")  # Du formulaire
            and len(self.data["vitals"]) >= 5  # Du formulaire
            and self.data.get("symptoms")  # Du chatbot
            and self.data.get("medical_history_asked")  # Du chatbot
        )

    def get_summary(self) -> Dict:
        """Résumé complet pour prédiction ML."""
        return {
            "patient_info": {
                "patient_id": self.data.get("num_patient"),
                "age": self.data.get("age"),
                "sex": self.data.get("sex"),
            },
            "symptoms": self.data.get("symptoms", []),
            "vitals": self.data["vitals"],
            "medical_history": self.data.get("medical_history", []),
            "current_medications": self.data.get("current_medications", []),
            "allergies": self.data.get("allergies", []),
            "symptom_duration": self.data.get("symptom_duration"),
            "messages": [
                m.get("content", m) if isinstance(m, dict) else m 
                for m in self.data["messages"]
            ],
        }

    def reset(self):
        """Reset avec données formulaire pré-remplies."""
        self.data = {
            # Données du FORMULAIRE (pré-remplies)
            "patient_id": patient_data.get("patient_id") if patient_data else None,
            "age": patient_data.get("age") if patient_data else None,
            "sex": patient_data.get("sex") if patient_data else None,
            "vitals": patient_data.get("vitals", {}) if patient_data else {},
            
            # Données collectées par le CHATBOT
            "symptoms": [],
            "medical_history": [],
            "current_medications": [],
            "allergies": [],
            "symptom_duration": None,
            
            # Flags de progression
            "medical_history_asked": False,
            "current_medications_asked": False,
            "allergies_asked": False,
            "symptom_duration_asked": False,
            
            # Conversation
            "messages": [],
        }
