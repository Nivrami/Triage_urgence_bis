"""
Classificateur de gravité.

JUSTIFIER le choix de l'algorithme:
- RandomForest: Interprétable (feature importance), robuste, peu d'hyperparamètres
- XGBoost: Plus performant mais moins explicable
- LogisticRegression: Baseline simple, très interprétable
- SVM: Bon pour petits datasets

Pour ce projet, RandomForest est recommandé car:
1. Feature importance = justification des décisions
2. Robuste aux données déséquilibrées
3. Pas besoin de normalisation stricte
"""

from typing import Optional
from ..models.patient import GravityLevel


class GravityClassifier:
    """
    Classificateur de gravité pour le triage.
    
    Prédit le niveau de gravité (GRIS, VERT, JAUNE, ROUGE)
    à partir des features du patient.
    """
    
    # Mapping gravité -> int pour le ML
    GRAVITY_MAPPING = {
        GravityLevel.GRIS: 0,
        GravityLevel.VERT: 1,
        GravityLevel.JAUNE: 2,
        GravityLevel.ROUGE: 3,
    }
    
    def __init__(
        self, 
        model_type: str = "random_forest",
        **model_params
    ) -> None:
        """
        Initialise le classificateur.
        
        Args:
            model_type: Type de modèle ("random_forest", "xgboost", "logistic")
            **model_params: Paramètres du modèle
            
        JUSTIFIER ton choix de modèle et ses paramètres.
        """
        pass
    
    def train(
        self, 
        X: list[list[float]], 
        y: list[int],
        validation_split: float = 0.2
    ) -> dict:
        """
        Entraîne le modèle.
        
        Args:
            X: Features
            y: Labels (0-3)
            validation_split: Proportion pour validation
            
        Returns:
            Métriques d'entraînement
        """
        pass
    
    def predict(self, features: list[float]) -> GravityLevel:
        """
        Prédit la gravité.
        
        Args:
            features: Vecteur de features
            
        Returns:
            Niveau de gravité prédit
        """
        pass
    
    def predict_proba(self, features: list[float]) -> dict[GravityLevel, float]:
        """
        Prédit avec probabilités.
        
        Args:
            features: Vecteur de features
            
        Returns:
            {GravityLevel: probabilité} pour chaque niveau
        """
        pass
    
    def predict_batch(self, X: list[list[float]]) -> list[GravityLevel]:
        """Prédit pour plusieurs patients."""
        pass
    
    def get_feature_importance(self) -> dict[str, float]:
        """
        Retourne l'importance des features.
        
        CRUCIAL pour justifier les décisions!
        
        Returns:
            {feature_name: importance_score}
        """
        pass
    
    def evaluate(
        self, 
        X_test: list[list[float]], 
        y_test: list[int]
    ) -> dict:
        """
        Évalue le modèle.
        
        Returns:
            {
                "accuracy": float,
                "precision": dict,  # par classe
                "recall": dict,
                "f1": dict,
                "confusion_matrix": list[list[int]],
                "classification_report": str
            }
        """
        pass
    
    def cross_validate(
        self, 
        X: list[list[float]], 
        y: list[int], 
        cv: int = 5
    ) -> dict:
        """Validation croisée."""
        pass
    
    def save(self, path: str) -> None:
        """Sauvegarde le modèle."""
        pass
    
    def load(self, path: str) -> None:
        """Charge un modèle sauvegardé."""
        pass
    
    def _create_model(self, model_type: str, **params):
        """Crée l'instance du modèle sklearn."""
        pass
    
    def _int_to_gravity(self, value: int) -> GravityLevel:
        """Convertit un int en GravityLevel."""
        pass
    
    def _gravity_to_int(self, gravity: GravityLevel) -> int:
        """Convertit un GravityLevel en int."""
        pass
