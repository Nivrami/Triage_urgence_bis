"""
Suivi de l'impact écologique.

Utilise CodeCarbon pour estimer les émissions CO2.

JUSTIFIER: Pourquoi tracker l'impact carbone?
- Critère d'évaluation du projet (sobriété)
- Sensibilisation à l'impact environnemental de l'IA
- Peut guider les choix de modèles (plus petit = moins d'émissions)
"""

from typing import Optional
from datetime import datetime


class CarbonTracker:
    """
    Suivi de l'impact écologique avec CodeCarbon.
    
    CodeCarbon mesure:
    - Consommation électrique (CPU, GPU, RAM)
    - Émissions CO2 selon le mix énergétique du pays
    """
    
    def __init__(
        self, 
        project_name: str = "triage_urgences",
        country_iso_code: str = "FRA"
    ) -> None:
        """
        Initialise le tracker carbone.
        
        Args:
            project_name: Nom du projet pour le logging
            country_iso_code: Code ISO du pays (FRA = France)
            
        Note: La France a un mix énergétique bas carbone (nucléaire),
        donc les émissions seront plus faibles qu'aux USA par exemple.
        """
        pass
    
    def start(self) -> None:
        """Démarre le tracking."""
        pass
    
    def stop(self) -> float:
        """
        Arrête le tracking et retourne les émissions.
        
        Returns:
            Émissions en kgCO2eq
        """
        pass
    
    def get_emissions(self) -> dict:
        """
        Émissions actuelles.
        
        Returns:
            {
                "emissions_kg": float,
                "emissions_g": float,
                "energy_consumed_kwh": float,
                "duration_seconds": float
            }
        """
        pass
    
    def estimate_emissions_per_request(self) -> float:
        """
        Estimation des émissions par requête.
        
        Returns:
            Émissions moyennes par requête en gCO2eq
        """
        pass
    
    def estimate_emissions_per_session(self) -> float:
        """Estimation par session de triage complète."""
        pass
    
    def get_energy_consumed(self) -> float:
        """Énergie consommée en kWh."""
        pass
    
    def get_duration(self) -> float:
        """Durée du tracking en secondes."""
        pass
    
    def compare_to_equivalents(self) -> dict:
        """
        Compare les émissions à des équivalents concrets.
        
        Returns:
            {
                "km_car": float,      # km en voiture
                "streaming_hours": float,  # heures de streaming
                "emails_sent": int,   # emails envoyés
            }
        """
        pass
    
    def export_to_dict(self) -> dict:
        """Exporte les données."""
        pass
    
    def reset(self) -> None:
        """Remet à zéro."""
        pass
    
    def log_to_file(self, path: str) -> None:
        """Sauvegarde dans un fichier."""
        pass
    
    def is_tracking(self) -> bool:
        """Vérifie si le tracking est actif."""
        pass
