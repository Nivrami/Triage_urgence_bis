"""
Agent simulateur de patient.

Utilisé pour la page simulation: simule un patient avec un profil prédéfini.
"""

from typing import Optional
import random
from .base_agent import BaseAgent
from ..llm.base_llm import BaseLLMProvider
from ..models.patient import GravityLevel, Constantes


# Profils de patients prédéfinis pour la simulation
PATIENT_PROFILES = {
    GravityLevel.GRIS: [
        {
            "description": "Renouvellement ordonnance",
            "symptomes": ["besoin de renouveler mon ordonnance"],
            "age": 45,
            "sexe": "F",
            "constantes": {"fc": 72, "ta_systolique": 120, "ta_diastolique": 80},
            "personnalite": "calme, organisé"
        },
        {
            "description": "Certificat médical sport",
            "symptomes": ["besoin d'un certificat pour le sport"],
            "age": 25,
            "sexe": "M",
            "constantes": {"fc": 65, "ta_systolique": 118, "ta_diastolique": 75},
            "personnalite": "pressé, en bonne santé"
        },
    ],
    GravityLevel.VERT: [
        {
            "description": "Entorse cheville",
            "symptomes": ["mal à la cheville", "gonflée", "tombé en marchant"],
            "age": 32,
            "sexe": "M",
            "constantes": {"fc": 78, "ta_systolique": 125, "ta_diastolique": 82},
            "personnalite": "inquiet mais stable"
        },
        {
            "description": "Gastro-entérite",
            "symptomes": ["nausées", "diarrhée", "mal au ventre depuis hier"],
            "age": 28,
            "sexe": "F",
            "constantes": {"fc": 85, "temperature": 37.8},
            "personnalite": "fatiguée, un peu anxieuse"
        },
    ],
    GravityLevel.JAUNE: [
        {
            "description": "Fracture bras",
            "symptomes": ["très mal au bras", "ne peut pas bouger", "chute vélo"],
            "age": 40,
            "sexe": "M",
            "constantes": {"fc": 95, "ta_systolique": 140, "ta_diastolique": 90},
            "personnalite": "douloureux, stressé"
        },
        {
            "description": "Fièvre élevée persistante",
            "symptomes": ["fièvre depuis 3 jours", "très fatigué", "frissons"],
            "age": 55,
            "sexe": "F",
            "constantes": {"fc": 100, "temperature": 39.5, "ta_systolique": 100},
            "personnalite": "affaiblie, confuse par moments"
        },
    ],
    GravityLevel.ROUGE: [
        {
            "description": "Douleur thoracique",
            "symptomes": ["douleur dans la poitrine", "oppression", "mal au bras gauche"],
            "age": 62,
            "sexe": "M",
            "constantes": {"fc": 110, "ta_systolique": 160, "ta_diastolique": 95, "spo2": 94},
            "personnalite": "très anxieux, sueurs"
        },
        {
            "description": "Difficulté respiratoire sévère",
            "symptomes": ["ne peut plus respirer", "lèvres bleues", "asthmatique"],
            "age": 35,
            "sexe": "F",
            "constantes": {"fc": 120, "fr": 28, "spo2": 88},
            "personnalite": "paniquée, essoufflée"
        },
    ],
}


class PatientSimulator(BaseAgent):
    """
    Agent qui simule un patient pour les tests et la démonstration.
    
    Le patient a un profil prédéfini avec:
    - Symptômes réels
    - Constantes vitales
    - Personnalité (affecte les réponses)
    - Gravité réelle (pour évaluation)
    """
    
    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        patient_profile: Optional[dict] = None,
        system_prompt: str = ""
    ) -> None:
        """
        Initialise le simulateur de patient.
        
        Args:
            llm_provider: Provider LLM
            patient_profile: Profil du patient (optionnel)
            system_prompt: Prompt système custom
        """
        pass
    
    def run(self, question: str) -> str:
        """
        Répond à une question comme le patient.
        
        Args:
            question: Question posée par l'infirmier
            
        Returns:
            Réponse du patient simulé
        """
        pass
    
    def set_profile(self, profile: dict) -> None:
        """
        Définit le profil du patient simulé.
        
        Args:
            profile: Dictionnaire avec les infos du patient
        """
        pass
    
    def generate_random_profile(
        self, 
        gravity_level: Optional[GravityLevel] = None
    ) -> dict:
        """
        Génère un profil aléatoire.
        
        Args:
            gravity_level: Niveau de gravité souhaité (aléatoire si None)
            
        Returns:
            Profil patient complet
        """
        pass
    
    def get_true_gravity(self) -> GravityLevel:
        """
        Retourne la vraie gravité du patient simulé.
        Utilisé pour évaluer la précision du triage.
        """
        pass
    
    def get_true_constantes(self) -> Constantes:
        """Retourne les vraies constantes (pour évaluation)."""
        pass
    
    def get_profile_summary(self) -> str:
        """Résumé du profil pour affichage."""
        pass
    
    def _build_patient_prompt(self) -> str:
        """Construit le prompt avec le profil injecté."""
        pass
    
    def should_reveal_symptom(self, symptom: str, question: str) -> bool:
        """
        Détermine si le patient doit révéler un symptôme.
        
        Simule le fait que les patients ne disent pas tout d'emblée.
        """
        pass
