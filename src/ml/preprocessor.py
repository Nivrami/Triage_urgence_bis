"""
Prétraitement des données pour le ML.
"""

from typing import Optional
import json


class DataPreprocessor:
    """
    Prétraitement des données pour le classificateur.
    
    Responsabilités:
    - Encoder les symptômes (TF-IDF, embeddings, etc.)
    - Normaliser les constantes vitales
    - Gérer les valeurs manquantes
    """
    
    def __init__(self) -> None:
        """
        Initialise le preprocessor.
        
        JUSTIFIER tes choix d'encodage:
        - TF-IDF: Simple, interprétable
        - Embeddings: Plus riche mais moins explicable
        """
        pass
    
    def fit(self, data: list[dict]) -> None:
        """
        Apprend les transformations sur les données d'entraînement.
        
        Args:
            data: Liste de patients (dicts)
        """
        pass
    
    def transform(self, data: dict) -> list[float]:
        """
        Applique les transformations à un patient.
        
        Args:
            data: Données d'un patient
            
        Returns:
            Vecteur de features
        """
        pass
    
    def fit_transform(self, data: list[dict]) -> list[list[float]]:
        """Fit + transform en une méthode."""
        pass
    
    def encode_symptoms(self, symptoms: list[str]) -> list[float]:
        """
        Encode les symptômes en vecteur numérique.
        
        Options:
        - Bag of words
        - TF-IDF
        - Embeddings moyennés
        """
        pass
    
    def normalize_constantes(self, constantes: dict) -> list[float]:
        """
        Normalise les constantes vitales.
        
        - Remplace None par la moyenne ou -1
        - Normalise entre 0 et 1 (ou z-score)
        """
        pass
    
    def encode_categorical(self, value: str, categories: list[str]) -> list[float]:
        """One-hot encoding pour les variables catégorielles."""
        pass
    
    def get_feature_names(self) -> list[str]:
        """Retourne les noms des features (pour interprétation)."""
        pass
    
    def save(self, path: str) -> None:
        """Sauvegarde le preprocessor (pour réutilisation)."""
        pass
    
    def load(self, path: str) -> None:
        """Charge un preprocessor sauvegardé."""
        pass
    
    def _handle_missing_values(self, features: list[float]) -> list[float]:
        """Gère les valeurs manquantes."""
        pass
