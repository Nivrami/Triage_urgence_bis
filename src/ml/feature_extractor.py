"""
Extraction de features depuis les conversations.
"""

from typing import Optional
from ..llm.base_llm import BaseLLMProvider
from ..models.patient import Patient, Constantes
from ..models.conversation import ConversationHistory


class FeatureExtractor:
    """
    Extrait les features structurées depuis une conversation.
    
    Utilise le LLM pour parser le texte libre en données structurées.
    """
    
    def __init__(
        self, 
        llm_provider: BaseLLMProvider,
        extraction_prompt: str = ""
    ) -> None:
        """
        Initialise l'extracteur.
        
        Args:
            llm_provider: Provider LLM pour l'extraction
            extraction_prompt: Prompt custom (utilise défaut sinon)
        """
        pass
    
    def extract_from_conversation(
        self, 
        conversation: ConversationHistory
    ) -> dict:
        """
        Extrait toutes les informations d'une conversation.
        
        Args:
            conversation: Historique de conversation
            
        Returns:
            {
                "symptomes": [...],
                "constantes": {...},
                "antecedents": [...],
                "allergies": [...],
                "age": ...,
                "sexe": ...,
                "duree_symptomes": ...
            }
        """
        pass
    
    def extract_symptoms(self, text: str) -> list[str]:
        """
        Extrait les symptômes mentionnés.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Liste de symptômes
        """
        pass
    
    def extract_constantes(self, text: str) -> Constantes:
        """
        Extrait les constantes vitales.
        
        Recherche les patterns:
        - "tension 12/8" -> ta_systolique=120, ta_diastolique=80
        - "39 de fièvre" -> temperature=39
        - etc.
        """
        pass
    
    def extract_antecedents(self, text: str) -> list[str]:
        """Extrait les antécédents médicaux."""
        pass
    
    def extract_allergies(self, text: str) -> list[str]:
        """Extrait les allergies mentionnées."""
        pass
    
    def extract_age_sexe(self, text: str) -> dict:
        """Extrait l'âge et le sexe."""
        pass
    
    def conversation_to_patient(
        self, 
        conversation: ConversationHistory
    ) -> Patient:
        """
        Convertit une conversation en objet Patient.
        
        Raccourci pour extract_from_conversation + création Patient.
        """
        pass
    
    def _call_llm_for_extraction(self, text: str) -> dict:
        """Appelle le LLM pour l'extraction structurée."""
        pass
    
    def _parse_json_response(self, response: str) -> dict:
        """Parse la réponse JSON du LLM."""
        pass
    
    def _validate_extracted_data(self, data: dict) -> dict:
        """Valide et nettoie les données extraites."""
        pass
