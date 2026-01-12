"""
Modèles de données pour les patients.

JUSTIFIER: Pourquoi Pydantic?
- Validation automatique des données
- Sérialisation/désérialisation JSON facile
- Type hints intégrés
- Immutabilité optionnelle
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
import uuid


class GravityLevel(Enum):
    """
    Niveaux de gravité du triage.
    
    JUSTIFIER: Pourquoi ces 4 niveaux?
    - Standard utilisé dans les urgences françaises
    - Correspond aux ressources fournies dans le projet
    """
    GRIS = "GRIS"    # Ne nécessite pas les urgences
    VERT = "VERT"    # Non vital, non urgent
    JAUNE = "JAUNE"  # Non vital mais urgent
    ROUGE = "ROUGE"  # Potentiellement vital et urgent
    
    @classmethod
    def from_string(cls, value: str) -> "GravityLevel":
        """Convertit une string en GravityLevel."""
        pass
    
    def to_color_code(self) -> str:
        """Retourne le code couleur hexadécimal."""
        pass
    
    def get_description(self) -> str:
        """Retourne la description du niveau."""
        pass


class Constantes(BaseModel):
    """
    Constantes vitales du patient.
    
    Valeurs normales adulte (pour référence):
    - FC: 60-100 bpm
    - FR: 12-20/min
    - SpO2: >95%
    - TA: 120/80 mmHg
    - Température: 36.5-37.5°C
    """
    fc: Optional[int] = Field(default=None, description="Fréquence cardiaque (bpm)")
    fr: Optional[int] = Field(default=None, description="Fréquence respiratoire (/min)")
    spo2: Optional[int] = Field(default=None, description="Saturation O2 (%)")
    ta_systolique: Optional[int] = Field(default=None, description="Tension systolique (mmHg)")
    ta_diastolique: Optional[int] = Field(default=None, description="Tension diastolique (mmHg)")
    temperature: Optional[float] = Field(default=None, description="Température (°C)")
    
    def is_complete(self) -> bool:
        """Vérifie si toutes les constantes sont renseignées."""
        pass
    
    def get_missing_fields(self) -> list[str]:
        """Retourne la liste des constantes manquantes."""
        pass
    
    def to_feature_vector(self) -> list[float]:
        """
        Convertit en vecteur numérique pour le ML.
        Remplace les None par des valeurs par défaut ou -1.
        """
        pass
    
    def has_critical_values(self) -> bool:
        """Vérifie si des valeurs sont critiques (hors normes)."""
        pass
    
    def get_anomalies(self) -> list[str]:
        """Retourne la liste des constantes anormales."""
        pass


class Patient(BaseModel):
    """Modèle complet d'un patient aux urgences."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prenom: Optional[str] = None
    nom: Optional[str] = None
    age: Optional[int] = None
    sexe: Optional[str] = Field(default=None, pattern="^(M|F)$")
    
    # Informations cliniques
    symptomes_exprimes: list[str] = Field(default_factory=list)
    constantes: Optional[Constantes] = None
    antecedents: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    traitements_en_cours: list[str] = Field(default_factory=list)
    duree_symptomes: Optional[str] = None
    
    # Résultat du triage
    gravite_predite: Optional[GravityLevel] = None
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1)
    
    def is_ready_for_classification(self) -> bool:
        """
        Vérifie si on a assez d'informations pour classifier.
        Minimum requis: au moins 1 symptôme.
        """
        pass
    
    def get_completeness_score(self) -> float:
        """
        Retourne un score de complétude des informations (0-1).
        Utile pour décider si continuer l'entretien.
        """
        pass
    
    def get_missing_critical_info(self) -> list[str]:
        """Retourne les informations critiques manquantes."""
        pass
    
    def to_dict(self) -> dict:
        """Sérialisation en dictionnaire."""
        pass
    
    def to_summary_string(self) -> str:
        """Résumé textuel pour injection dans un prompt."""
        pass
    
    def merge_with(self, other_data: dict) -> "Patient":
        """Fusionne avec de nouvelles données extraites."""
        pass
