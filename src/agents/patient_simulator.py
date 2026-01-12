"""
Simulateur de patient - Version dynamique sans profils prédéfinis.

Simule un patient avec un profil généré par PatientGenerator.
"""

from typing import Optional
from .base_agent import BaseAgent
from ..llm.base_llm import BaseLLMProvider
from ..models.patient import Patient
from ..models.conversation import ConversationHistory


class PatientSimulator(BaseAgent):
    """
    Simule un patient avec un profil donné.
    
    Le patient répond aux questions de manière cohérente avec :
    - Ses symptômes
    - Ses constantes vitales
    - Ses antécédents
    - Sa personnalité (déduite de la gravité)
    """
    
    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        patient: Patient
    ):
        """
        Initialise le simulateur avec un patient.
        
        Args:
            llm_provider: Provider LLM
            patient: Profil patient généré par PatientGenerator
        """
        self.patient = patient
        self.conversation = ConversationHistory()
        
        # Créer le system prompt basé sur le patient
        system_prompt = self._build_system_prompt()
        
        super().__init__(
            llm_provider=llm_provider,
            system_prompt=system_prompt,
            name=f"Patient_{patient.prenom}"
        )
    
    def run(self, input_data: str) -> dict:
        """
        Répond à une question de l'infirmier.
        
        Args:
            input_data: Question posée
            
        Returns:
            dict avec "response": str
        """
        response = self.respond(input_data)
        return {"response": response}
    
    def respond(self, question: str) -> str:
        """
        Le patient répond à une question de l'infirmier.
        
        Args:
            question: Question posée par l'infirmier
            
        Returns:
            str: Réponse du patient
        """
        # Ajouter la question à l'historique
        self.conversation.add_user_message(question)
        
        # Construire les messages pour le LLM
        messages = self._build_messages(question, self.conversation)
        
        # Générer la réponse
        response = self.llm.generate(
            messages=messages,
            temperature=0.8,  # Un peu de variabilité pour être naturel
            max_tokens=200
        )
        
        # Sauvegarder la réponse
        self.conversation.add_assistant_message(response)
        
        return response
    
    def get_initial_complaint(self) -> str:
        """
        Génère la plainte initiale du patient.
        
        Returns:
            str: Première phrase du patient en arrivant aux urgences
        """
        prompt = """Tu arrives aux urgences. 
        
Dis bonjour et exprime ta plainte principale en 1-2 phrases SIMPLES.

Exemple de bonnes réponses :
- "Bonjour docteur, j'ai très mal au cœur depuis ce matin..."
- "Bonjour, je n'arrive plus à respirer correctement..."
- "Bonjour, ma cheville est très gonflée depuis ma chute..."

Réponds maintenant :"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm.generate(
            messages=messages,
            temperature=0.8,
            max_tokens=150
        )
        
        # Sauvegarder dans l'historique
        self.conversation.add_assistant_message(response)
        
        return response
    
    def _build_system_prompt(self) -> str:
        """Construit le prompt système basé sur le profil patient."""
        
        prompt = f"""Tu es {self.patient.prenom} {self.patient.nom}, {self.patient.age} ans, qui arrive aux urgences.

**TES SYMPTÔMES :**
"""
        
        for symptom in self.patient.symptomes_exprimes:
            prompt += f"- {symptom}\n"
        
        prompt += f"\n**DEPUIS QUAND :**\n{self.patient.duree_symptomes or 'Quelques heures'}\n"
        
        # Constantes (le patient ne les connaît pas précisément)
        if self.patient.constantes:
            prompt += "\n**CE QUE TU RESSENS PHYSIQUEMENT :**\n"
            
            const = self.patient.constantes
            
            if const.fc and const.fc > 100:
                prompt += "- Ton cœur bat vite, tu le sens\n"
            elif const.fc and const.fc < 60:
                prompt += "- Tu te sens faible\n"
            
            if const.spo2 and const.spo2 < 92:
                prompt += "- Tu as du mal à respirer, tu es essoufflé\n"
            
            if const.temperature and const.temperature > 38:
                prompt += f"- Tu as chaud, tu transpires (tu as {const.temperature}°C de fièvre)\n"
            
            if const.ta_systolique and const.ta_systolique < 90:
                prompt += "- Tu te sens étourdi, faible\n"
        
        # Antécédents
        if self.patient.antecedents:
            prompt += "\n**TES ANTÉCÉDENTS MÉDICAUX :**\n"
            for ant in self.patient.antecedents:
                prompt += f"- {ant}\n"
        
        # Règles de comportement
        prompt += """
**COMMENT TU DOIS TE COMPORTER :**

1. **Parle SIMPLEMENT** : Tu es un patient normal, pas un médecin
   ❌ "J'ai une dyspnée"
   ✅ "J'ai du mal à respirer"
   
   ❌ "Douleur rétrosternale constrictive"
   ✅ "J'ai mal au milieu de la poitrine, ça serre fort"

2. **Exprime tes symptômes subjectivement** :
   - "j'ai mal", "ça me fait mal quand..."
   - "ça serre", "ça brûle", "ça lance"
   - "je sens que...", "j'ai l'impression que..."

3. **Tu es INQUIET** : C'est pour ça que tu es venu aux urgences
   - Montre ton inquiétude dans tes réponses
   - Tu peux être anxieux, stressé

4. **Tu NE CONNAIS PAS ta maladie** : Tu décris juste ce que tu ressens

5. **Sois COHÉRENT** : 
   - Réponds selon tes symptômes listés
   - Ne contredis pas tes réponses précédentes
   - Si on te demande un symptôme que tu n'as pas, dis NON

6. **Reste naturel** :
   - Phrases courtes et simples
   - Tu peux hésiter parfois
   - Tu peux ne pas savoir exactement

**EXEMPLES DE DIALOGUE :**

Infirmier : "Depuis quand avez-vous mal ?"
TOI : "Ça a commencé ce matin vers 8h, d'un coup..." ✅

Infirmier : "Où avez-vous mal exactement ?"
TOI : "Là, au milieu de la poitrine, et ça descend dans le bras gauche..." ✅

Infirmier : "Avez-vous de la fièvre ?"
TOI : "Oui, je me sens chaud et je transpire..." ✅

Infirmier : "Avez-vous des antécédents ?"
TOI : "Oui, je suis diabétique depuis 10 ans et hypertendu..." ✅
"""
        
        return prompt
    
    def get_patient_profile(self) -> Patient:
        """Retourne le profil patient."""
        return self.patient
    
    def get_conversation_history(self) -> ConversationHistory:
        """Retourne l'historique de conversation."""
        return self.conversation
    
    def reset_conversation(self) -> None:
        """Réinitialise l'historique de conversation."""
        self.conversation = ConversationHistory()
