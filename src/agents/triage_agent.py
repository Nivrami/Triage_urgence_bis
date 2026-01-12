"""
Agent principal de triage.

C'est le cœur du système: il mène l'entretien et prédit la gravité.
"""

from typing import Optional
from .base_agent import BaseAgent
from ..llm.base_llm import BaseLLMProvider
from ..rag.retriever import Retriever
from ..ml.classifier import GravityClassifier
from ..ml.feature_extractor import FeatureExtractor
from ..models.patient import Patient, GravityLevel
from ..models.conversation import ConversationHistory
from ..models.triage import TriageResult


class TriageAgent(BaseAgent):
    """
    Agent principal qui mène l'entretien de triage.
    
    Responsabilités:
    1. Poser des questions pertinentes au patient
    2. Extraire les informations de la conversation
    3. Utiliser le RAG pour le contexte médical
    4. Prédire la gravité (ML + LLM)
    """
    
    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        retriever: Retriever,
        classifier: GravityClassifier,
        feature_extractor: FeatureExtractor,
        system_prompt: str = ""
    ) -> None:
        """
        Initialise l'agent de triage.
        
        Args:
            llm_provider: Provider LLM
            retriever: Retriever RAG pour le contexte médical
            classifier: Classificateur ML de gravité
            feature_extractor: Extracteur de features
            system_prompt: Prompt système (optionnel, utilise le défaut sinon)
        """
        pass
    
    def run(self, conversation: ConversationHistory) -> dict:
        """
        Exécute un tour de conversation.
        
        Args:
            conversation: Historique actuel
            
        Returns:
            {
                "response": str,           # Question ou conclusion
                "patient": Patient,        # Données patient extraites
                "should_stop": bool,       # True si assez d'infos
                "triage_result": Optional[TriageResult]  # Si terminé
            }
        """
        pass
    
    def ask_next_question(self, conversation: ConversationHistory) -> str:
        """
        Génère la prochaine question à poser.
        
        Logique:
        1. Analyser ce qui manque (via Patient.get_missing_critical_info)
        2. Récupérer contexte RAG si symptômes présents
        3. Générer une question pertinente
        """
        pass
    
    def should_stop_interview(self, patient: Patient) -> bool:
        """
        Détermine si on a assez d'informations pour classifier.
        
        Critères:
        - Au moins 1 symptôme
        - Score de complétude > seuil
        - OU max de tours atteint
        """
        pass
    
    def extract_patient_data(self, conversation: ConversationHistory) -> Patient:
        """
        Extrait les données patient de la conversation.
        
        Utilise le FeatureExtractor avec le prompt d'extraction.
        """
        pass
    
    def get_rag_context(self, symptoms: list[str]) -> str:
        """
        Récupère le contexte médical pertinent via RAG.
        
        Args:
            symptoms: Liste des symptômes à rechercher
            
        Returns:
            Contexte formaté pour injection dans le prompt
        """
        pass
    
    def predict_gravity(
        self, 
        patient: Patient, 
        rag_context: str
    ) -> TriageResult:
        """
        Prédit la gravité avec ML + LLM.
        
        Approche hybride:
        1. Prédiction ML (si features suffisantes)
        2. Prédiction LLM (avec contexte RAG)
        3. Combinaison/arbitrage des deux
        
        JUSTIFIER: Pourquoi hybride?
        - ML: Rapide, cohérent, basé sur les constantes
        - LLM: Meilleur raisonnement, gère les cas atypiques
        """
        pass
    
    def _combine_predictions(
        self,
        ml_prediction: Optional[GravityLevel],
        ml_confidence: float,
        llm_prediction: GravityLevel,
        llm_reasoning: str
    ) -> tuple[GravityLevel, float]:
        """
        Combine les prédictions ML et LLM.
        
        Stratégie possible:
        - Si ML haute confiance (>0.8): utiliser ML
        - Si ML basse confiance: utiliser LLM
        - Si désaccord: prendre le plus grave (sécurité)
        """
        pass
    
    def _generate_reasoning(
        self,
        patient: Patient,
        gravity: GravityLevel,
        rag_context: str
    ) -> str:
        """Génère l'explication du choix de gravité."""
        pass
