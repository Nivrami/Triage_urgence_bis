"""
Agent infirmier qui mène l'entretien de triage.

Pose des questions pertinentes pour évaluer le patient.
"""

from typing import Optional
from .base_agent import BaseAgent
from ..llm.base_llm import BaseLLMProvider
from ..models.conversation import ConversationHistory


class NurseAgent(BaseAgent):
    """
    Agent infirmier qui pose des questions de triage.
    
    Suit une méthodologie de triage :
    1. Plainte principale
    2. Caractérisation (où, depuis quand, comment)
    3. Symptômes associés
    4. Antécédents
    5. Évaluation gravité
    """
    
    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        max_questions: int = 8
    ):
        """
        Initialise l'agent infirmier.
        
        Args:
            llm_provider: Provider LLM
            max_questions: Nombre maximum de questions à poser
        """
        system_prompt = """Tu es un infirmier expérimenté aux urgences qui fait le triage des patients.

**TES OBJECTIFS :**
1. Identifier la plainte principale
2. Caractériser les symptômes (localisation, intensité, évolution)
3. Rechercher les signes de gravité (RED FLAGS)
4. Connaître les antécédents pertinents
5. Évaluer l'urgence de la prise en charge

**MÉTHODOLOGIE DE TRIAGE :**

**Phase 1 - Plainte principale :**
- "Bonjour, que se passe-t-il aujourd'hui ?"
- Écouter la plainte

**Phase 2 - Caractérisation :**
- "Depuis quand ?" (temporalité)
- "Où exactement ?" (localisation)
- "Comment ça a commencé ?" (mode de début)
- "Est-ce que ça s'aggrave ?" (évolution)

**Phase 3 - Symptômes associés :**
- "Avez-vous d'autres symptômes ?"
- Recherche systématique selon l'organe

**Phase 4 - Antécédents :**
- "Avez-vous des antécédents médicaux ?"
- "Prenez-vous des médicaments ?"
- "Des allergies ?"

**RED FLAGS À RECHERCHER :**
- Douleur thoracique → Infarctus ?
- Difficulté respiratoire → Détresse respiratoire ?
- Troubles neurologiques → AVC ?
- Fièvre élevée + confusion → Sepsis ?
- Hémorragie → Choc hémorragique ?

**RÈGLES :**
- Une seule question à la fois
- Questions claires et directes
- Adapter selon les réponses
- Pas de question répétée
- Rester professionnel mais empathique
"""
        
        super().__init__(
            llm_provider=llm_provider,
            system_prompt=system_prompt,
            name="NurseAgent"
        )
        
        self.max_questions = max_questions
        self.questions_asked = 0
        self.conversation = ConversationHistory()
    
    def run(self, input_data: ConversationHistory) -> dict:
        """
        Génère la prochaine question.
        
        Args:
            input_data: Historique de conversation
            
        Returns:
            dict avec "question": str, "should_stop": bool
        """
        self.conversation = input_data
        question = self.ask_next_question()
        should_stop = not self.should_continue()
        
        return {
            "question": question,
            "should_stop": should_stop
        }
    
    def ask_next_question(self) -> str:
        """
        Génère la prochaine question à poser.
        
        Returns:
            str: Question à poser au patient
        """
        if self.questions_asked == 0:
            # Première question standard
            self.questions_asked += 1
            return "Bonjour, que se passe-t-il aujourd'hui ?"
        
        # Questions suivantes générées dynamiquement
        prompt = f"""**HISTORIQUE DE LA CONVERSATION :**
{self.conversation.get_full_text()}

**CONTEXTE :**
- Tu as déjà posé {self.questions_asked} question(s)
- Tu peux poser encore {self.max_questions - self.questions_asked} question(s)

**TA MISSION :**
Génère LA PROCHAINE question la plus pertinente pour :
1. Compléter l'évaluation du patient
2. Identifier les signes de gravité
3. Obtenir les informations manquantes critiques

**RÈGLES :**
- UNE SEULE question claire et directe
- Adapte-toi à ce qui a déjà été dit
- Ne répète JAMAIS une question déjà posée
- Priorise les informations critiques (depuis quand, où, gravité)

**EXEMPLES DE BONNES QUESTIONS :**
- "Depuis quand avez-vous ces symptômes ?"
- "Où avez-vous mal exactement ?"
- "La douleur est-elle constante ou par moments ?"
- "Avez-vous d'autres symptômes : nausées, vomissements, fièvre ?"
- "Avez-vous des antécédents médicaux ?"
- "Prenez-vous des médicaments régulièrement ?"

**RÉPONDS UNIQUEMENT AVEC LA QUESTION (pas de préambule) :**
"""
        
        messages = [{"role": "user", "content": prompt}]
        
        question = self.llm.generate(
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )
        
        # Nettoyer la question
        question = question.strip()
        # Enlever les guillemets si présents
        question = question.strip('"').strip("'")
        # S'assurer qu'il y a un point d'interrogation
        if not question.endswith('?'):
            question += ' ?'
        
        self.questions_asked += 1
        
        return question
    
    def should_continue(self) -> bool:
        """
        Détermine si on doit continuer à poser des questions.
        
        Returns:
            bool: True si on doit continuer, False sinon
        """
        return self.questions_asked < self.max_questions
    
    def add_to_history(self, role: str, content: str) -> None:
        """
        Ajoute un message à l'historique.
        
        Args:
            role: "nurse" ou "patient"
            content: Contenu du message
        """
        if role == "nurse":
            self.conversation.add_user_message(content)
        elif role == "patient":
            self.conversation.add_assistant_message(content)
    
    def get_conversation_history(self) -> ConversationHistory:
        """Retourne l'historique de conversation."""
        return self.conversation
    
    def reset(self) -> None:
        """Réinitialise l'agent pour une nouvelle consultation."""
        self.questions_asked = 0
        self.conversation = ConversationHistory()
