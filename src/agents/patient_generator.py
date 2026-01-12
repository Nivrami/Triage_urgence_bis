"""
Générateur de profils patients réalistes via LLM.

Génère un patient cohérent (symptômes, constantes, antécédents)
à partir d'une simple description de pathologie.
"""

from typing import Optional
import json
from .base_agent import BaseAgent
from ..llm.base_llm import BaseLLMProvider
from ..models.patient import Patient, Constantes, GravityLevel


class PatientGenerator(BaseAgent):
    """
    Génère un patient réaliste à partir d'une description.
    
    Input: "Homme de 65 ans avec suspicion d'infarctus"
    Output: Patient(prenom, nom, age, symptomes, constantes cohérentes...)
    """
    
    def __init__(self, llm_provider: BaseLLMProvider):
        """Initialise le générateur."""
        system_prompt = """Tu es un expert médical qui crée des profils de patients réalistes pour des simulations médicales.

Tu dois générer des patients COHÉRENTS et MÉDICALEMENT CORRECTS."""
        
        super().__init__(
            llm_provider=llm_provider,
            system_prompt=system_prompt,
            name="PatientGenerator"
        )
    
    def run(self, input_data: str) -> dict:
        """
        Génère un patient depuis une description.
        
        Args:
            input_data: Description de la pathologie
            
        Returns:
            dict avec "patient": Patient
        """
        patient = self.generate_from_description(input_data)
        return {"patient": patient}
    
    def generate_from_description(self, description: str) -> Patient:
        """
        Génère un patient complet à partir d'une description.
        
        Args:
            description: "Homme de 65 ans avec infarctus du myocarde"
            
        Returns:
            Patient: Objet Patient complet avec symptômes et constantes cohérents
        """
        prompt = f"""Génère un profil patient RÉALISTE et COHÉRENT pour cette pathologie :

**Description:** {description}

**RÈGLES CRITIQUES :**
1. Les symptômes doivent être en LANGAGE PATIENT (simple, pas médical)
   ❌ "douleur rétrosternale" → ✅ "mal au milieu de la poitrine"
   ❌ "dyspnée" → ✅ "difficulté à respirer"
   
2. Les constantes doivent être COHÉRENTES avec la pathologie
   - Si infarctus : FC élevée (>100), TA peut être basse, SpO2 < 95%
   - Si pneumonie : FC élevée, température > 38°C, SpO2 < 92%
   - Si fracture : FC légèrement élevée (stress), constantes sinon normales
   
3. Les antécédents doivent être PERTINENTS
   - Infarctus : diabète, hypertension, tabagisme
   - AVC : hypertension, fibrillation auriculaire
   - Fracture : ostéoporose si âgé
   
4. Durée des symptômes RÉALISTE
   - Infarctus : "depuis 2 heures"
   - Pneumonie : "depuis 3 jours"
   - Fracture : "depuis la chute il y a 1 heure"

**RÉPONDS UNIQUEMENT AU FORMAT JSON (pas de texte avant/après) :**

{{
  "prenom": "prénom français réaliste",
  "nom": "nom français",
  "age": nombre_coherent_avec_pathologie,
  "sexe": "M" ou "F",
  "symptomes_exprimes": [
    "symptôme en langage simple",
    "autre symptôme simple",
    "..."
  ],
  "constantes": {{
    "fc": nombre_coherent,
    "fr": nombre_coherent,
    "spo2": nombre_coherent,
    "ta_systolique": nombre,
    "ta_diastolique": nombre,
    "temperature": nombre_en_celsius
  }},
  "antecedents": [
    "antécédent pertinent 1",
    "antécédent pertinent 2"
  ],
  "duree_symptomes": "depuis combien de temps"
}}

**EXEMPLES DE BONS SYMPTÔMES (langage patient) :**
- "j'ai mal au cœur"
- "je n'arrive plus à respirer"
- "ma cheville est gonflée"
- "j'ai très mal au ventre"
- "je vois double"
- "j'ai de la fièvre et je tremble"

**EXEMPLES DE CONSTANTES COHÉRENTES :**

Infarctus :
- FC: 110-130 bpm (tachycardie)
- TA: 80-100 / 50-70 (hypotension)
- SpO2: 90-94% (légère hypoxie)
- Température: 37-37.5°C (normale)

Pneumonie sévère :
- FC: 100-120 bpm
- FR: 24-30 /min (tachypnée)
- SpO2: 85-92% (hypoxie)
- Température: 38.5-40°C (fièvre)

Fracture simple :
- FC: 80-95 bpm (légèrement élevée, stress)
- TA: 130/85 (normale ou légèrement élevée)
- SpO2: 97-99% (normale)
- Température: 36.8-37.2°C (normale)
"""
        
        # Appeler le LLM
        response = self.llm.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        
        # Parser le JSON
        try:
            data = self._extract_json_from_response(response)
            
            # Créer l'objet Constantes
            constantes_data = data.get("constantes", {})
            constantes = Constantes(
                fc=constantes_data.get("fc"),
                fr=constantes_data.get("fr"),
                spo2=constantes_data.get("spo2"),
                ta_systolique=constantes_data.get("ta_systolique"),
                ta_diastolique=constantes_data.get("ta_diastolique"),
                temperature=constantes_data.get("temperature")
            )
            
            # Créer l'objet Patient
            patient = Patient(
                prenom=data.get("prenom"),
                nom=data.get("nom"),
                age=data.get("age"),
                sexe=data.get("sexe"),
                symptomes_exprimes=data.get("symptomes_exprimes", []),
                constantes=constantes,
                antecedents=data.get("antecedents", []),
                duree_symptomes=data.get("duree_symptomes")
            )
            
            print(f"✅ Patient généré : {patient.prenom} {patient.nom}, {patient.age} ans")
            print(f"   Symptômes : {', '.join(patient.symptomes_exprimes[:3])}...")
            
            return patient
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"❌ Erreur génération patient : {e}")
            print(f"Réponse LLM : {response}")
            raise ValueError(f"Impossible de générer un patient valide : {e}")
