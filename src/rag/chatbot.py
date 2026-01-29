"""
Chatbot Final - Mistral API ROBUSTE avec Monitoring
"""

import re
import time
import os
from typing import Dict
from mistralai import Mistral
from dotenv import load_dotenv
load_dotenv()  


class TriageChatbotAPI:
    """Chatbot Mistral API robuste avec tracking complet."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if self.api_key:
            self.client = Mistral(api_key=self.api_key)
            self.use_api = True
            print("✅ Mistral API activée")
        else:
            self.use_api = False
            print("⚠️ Mode règles (sans API)")
        
        self.reset()
    
    def start(self) -> str:
        return "Bonjour. Indiquez : prénom, âge, sexe\nExemple : Jean, 25 ans, homme"
    
    def chat(self, msg: str) -> str:
        """Chat principal avec tracking."""
        start = time.time()
        self.data["messages"].append({"role": "user", "content": msg})
        
        # Extraire données
        self._extract(msg)
        
        # Déterminer étape suivante
        next_step = self._get_next_step()
        
        # Générer réponse
        if self.use_api and self.data.get("age") and next_step != "identity":
            response = self._ask_with_api(next_step)
        else:
            response = self._ask_with_rules(next_step)
        
        self.data["messages"].append({"role": "assistant", "content": response})
        
        # Track latence
        self._track_latency(time.time() - start)
        
        return response
    
    def _get_next_step(self) -> str:
        """Détermine prochaine étape unique."""
        if not self.data.get("age") or not self.data.get("sex"):
            return "identity"
        
        if not self.data.get("symptoms"):
            return "symptoms"
        
        v = self.data["vitals"]
        
        if "Temperature" not in v:
            return "temperature"
        if "FC" not in v:
            return "fc"
        if "TA_systolique" not in v:
            return "ta"
        if "SpO2" not in v:
            return "spo2"
        if "FR" not in v:
            return "fr"
        
        return "done"
    
    def _ask_with_api(self, step: str) -> str:
        """Appel Mistral """
        try:
            # Prompts intelligents (pas robotiques)
            prompts = {
                "symptoms": """Tu es un assistant médical empathique. Le patient a déjà donné son identité.
Demande maintenant son symptôme principal de manière naturelle et rassurante.
Donne un exemple concret pour guider le patient.
Réponds en 1-2 phrases maximum.""",
                
                "temperature": """Le patient a décrit ses symptômes. 
Demande maintenant sa température corporelle de manière claire.
Format attendu: un nombre entre 35 et 43°C.
Donne un exemple: "Quelle est votre température ? Exemple: 38.5"
Sois bref et précis.""",
                
                "fc": """Demande la fréquence cardiaque (pouls) du patient.
Format attendu: nombre de battements par minute.
Exemple: "Quel est votre pouls ? Exemple: 80"
Reste concis.""",
                
                "ta": """Demande la tension artérielle.
Format attendu: deux nombres séparés par un slash (systolique/diastolique).
Exemple: "Quelle est votre tension ? Exemple: 120/80"
Une seule phrase.""",
                
                "spo2": """Demande la saturation en oxygène (SpO2).
Format attendu: pourcentage entre 50 et 100.
Exemple: "Quelle est votre saturation en oxygène ? Exemple: 97"
Sois direct.""",
                
                "fr": """Demande la fréquence respiratoire.
Format attendu: nombre de respirations par minute.
Exemple: "Quelle est votre fréquence respiratoire ? Exemple: 16"
Concis et clair.""",
                
                "done": """Toutes les informations sont collectées.
Informe le patient que son dossier est complet et qu'il peut obtenir une prédiction.
Sois rassurant et professionnel.
Une phrase courte."""
            }
            
            system_prompt = prompts.get(step, "Guide le patient avec empathie.")
            
            # Contexte des données déjà collectées
            context = self._build_context()
            
            # Appel API avec Mistral Large
            start = time.time()
            resp = self.client.chat.complete(
                model="mistral-large-latest",  
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Contexte patient: {context}\n\nQuelle est ta question ?"}
                ],
                temperature=0.4,  
                max_tokens=100
            )
            
            # Track API call
            self._track_api(
                resp.usage.prompt_tokens,
                resp.usage.completion_tokens,
                time.time() - start
            )
            
            response = resp.choices[0].message.content.strip()
            
            # Nettoyer la réponse si trop longue
            if len(response) > 200:
                response = response[:200] + "..."
            
            return response
            
        except Exception as e:
            print(f"API Error: {e}")
            return self._ask_with_rules(step)
    
    def _build_context(self) -> str:
        """Construit contexte pour Mistral."""
        parts = []
        
        if self.data.get("name"):
            parts.append(f"Prénom: {self.data['name']}")
        if self.data.get("age"):
            parts.append(f"Âge: {self.data['age']} ans")
        if self.data.get("sex"):
            sex = "Homme" if self.data["sex"] == "H" else "Femme"
            parts.append(f"Sexe: {sex}")
        if self.data.get("symptoms"):
            parts.append(f"Symptômes: {', '.join(self.data['symptoms'])}")
        
        v = self.data["vitals"]
        vitals_collected = []
        if "Temperature" in v:
            vitals_collected.append(f"Temp: {v['Temperature']}°C")
        if "FC" in v:
            vitals_collected.append(f"FC: {v['FC']} bpm")
        if "TA_systolique" in v:
            vitals_collected.append(f"TA: {v['TA_systolique']}/{v.get('TA_diastolique', '?')}")
        if "SpO2" in v:
            vitals_collected.append(f"SpO2: {v['SpO2']}%")
        if "FR" in v:
            vitals_collected.append(f"FR: {v['FR']}/min")
        
        if vitals_collected:
            parts.append(f"Constantes: {', '.join(vitals_collected)}")
        
        return " | ".join(parts) if parts else "Nouveau patient"
    
    def _ask_with_rules(self, step: str) -> str:
        """Fallback règles."""
        responses = {
            "identity": "Précisez votre âge et sexe.\nExemple : 25 ans homme",
            "symptoms": "Quel est votre symptôme ?\nExemple : mal de tête / fièvre",
            "temperature": "Quelle est votre température ?\nExemple : 38.5",
            "fc": "Quel est votre pouls ?\nExemple : 80",
            "ta": "Quelle est votre tension ?\nExemple : 120/80",
            "spo2": "Quelle est votre saturation ?\nExemple : 97",
            "fr": "Quelle est votre fréquence respiratoire ?\nExemple : 16",
            "done": "✅ Dossier complet. Cliquez 'Obtenir prédiction ML'."
        }
        return responses.get(step, "Erreur")
    
    def _extract(self, msg: str):
        """Extraction robuste."""
        ml = msg.lower()
        
        # Âge
        if not self.data.get("age"):
            m = re.search(r'(\d{1,3})\s*ans?', ml)
            if m:
                age = int(m.group(1))
                if 0 < age < 120:
                    self.data["age"] = age
        
        # Sexe
        if not self.data.get("sex"):
            if "homme" in ml:
                self.data["sex"] = "H"
            elif "femme" in ml:
                self.data["sex"] = "F"
        
        # Prénom
        if not self.data.get("name"):
            words = msg.split(',')
            if words:
                first = words[0].strip()
                if len(first) >= 2 and first[0].isupper():
                    self.data["name"] = first
        
        # Symptômes
        symp = {
            r"t[eé]te": "Céphalée",
            r"ventre": "Douleur abdominale",
            r"poitrine": "Douleur thoracique",
            r"fi[eé]vre": "Fièvre"
        }
        for p, s in symp.items():
            if re.search(p, ml):
                if s not in self.data.get("symptoms", []):
                    if "symptoms" not in self.data:
                        self.data["symptoms"] = []
                    self.data["symptoms"].append(s)
        
        # Température
        if "Temperature" not in self.data["vitals"]:
            m = re.search(r'(\d{2}\.?\d?)', ml)
            if m:
                t = float(m.group(1))
                if 35 <= t <= 43:
                    self.data["vitals"]["Temperature"] = t
                    return
        
        # FC
        if "FC" not in self.data["vitals"]:
            m = re.search(r'(\d{2,3})', ml)
            if m:
                fc = int(m.group(1))
                if 30 <= fc <= 220:
                    self.data["vitals"]["FC"] = fc
                    return
        
        # TA
        if "TA_systolique" not in self.data["vitals"]:
            m = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})', ml)
            if m:
                self.data["vitals"]["TA_systolique"] = int(m.group(1))
                self.data["vitals"]["TA_diastolique"] = int(m.group(2))
                return
        
        # SpO2
        if "SpO2" not in self.data["vitals"]:
            m = re.search(r'(\d{2,3})', ml)
            if m:
                spo2 = int(m.group(1))
                if 50 <= spo2 <= 100:
                    self.data["vitals"]["SpO2"] = spo2
                    return
        
        # FR
        if "FR" not in self.data["vitals"]:
            m = re.search(r'(\d{1,2})', ml)
            if m:
                fr = int(m.group(1))
                if 5 <= fr <= 60:
                    self.data["vitals"]["FR"] = fr
                    return
    
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
                model="mistral-large-latest",
                tokens_input=tokens_in,
                tokens_output=tokens_out,
                latency=latency,
                success=True
            )
        except:
            pass
    
    def is_ready_for_prediction(self) -> bool:
        """Vérifie si 5/5 constantes."""
        v = self.data["vitals"]
        return (
            self.data.get("age") and
            self.data.get("sex") and
            self.data.get("symptoms") and
            all(k in v for k in ["Temperature", "FC", "TA_systolique", "SpO2", "FR"])
        )
    
    def get_summary(self) -> Dict:
        """Résumé pour prédiction ML."""
        return {
            "patient_info": {
                "name": self.data.get("name"),
                "age": self.data.get("age"),
                "sex": "Femme" if self.data.get("sex") == "F" else "Homme"
            },
            "symptoms": self.data.get("symptoms", []),
            "vitals": self.data["vitals"],
            "messages": [m.get("content", m) if isinstance(m, dict) else m for m in self.data["messages"]]
        }
    
    def reset(self):
        """Reset complet."""
        self.data = {
            "name": None,
            "age": None,
            "sex": None,
            "symptoms": [],
            "vitals": {},
            "messages": []
        }