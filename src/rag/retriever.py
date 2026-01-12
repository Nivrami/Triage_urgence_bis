"""
Logique de retrieval pour le RAG.
"""

from typing import Optional
from .vector_store import VectorStore


class Retriever:
    """
    Retriever pour le RAG.
    
    Responsabilités:
    - Rechercher les documents pertinents
    - Filtrer par score
    - Formater le contexte pour le prompt
    """
    
    def __init__(
        self, 
        vector_store: VectorStore,
        default_top_k: int = 5,
        score_threshold: float = 0.5
    ) -> None:
        """
        Initialise le retriever.
        
        Args:
            vector_store: Base vectorielle
            default_top_k: Nombre de résultats par défaut
            score_threshold: Score minimum de similarité
        """
        pass
    
    def retrieve(
        self, 
        query: str, 
        top_k: Optional[int] = None
    ) -> list[dict]:
        """
        Récupère les documents pertinents.
        
        Args:
            query: Requête de recherche
            top_k: Nombre de résultats (défaut si None)
            
        Returns:
            Liste de documents pertinents
        """
        pass
    
    def retrieve_with_scores(
        self, 
        query: str, 
        top_k: Optional[int] = None
    ) -> list[tuple[dict, float]]:
        """Récupère avec les scores de similarité."""
        pass
    
    def format_context(
        self, 
        documents: list[dict],
        max_tokens: int = 1000
    ) -> str:
        """
        Formate les documents pour injection dans le prompt.
        
        Args:
            documents: Documents à formater
            max_tokens: Limite de tokens (approximative)
            
        Returns:
            Contexte formaté en string
        """
        pass
    
    def filter_by_threshold(
        self, 
        results: list[tuple[dict, float]], 
        threshold: Optional[float] = None
    ) -> list[dict]:
        """
        Filtre les résultats par score minimum.
        
        Args:
            results: Résultats avec scores
            threshold: Seuil (utilise le défaut si None)
            
        Returns:
            Documents au-dessus du seuil
        """
        pass
    
    def retrieve_and_format(
        self, 
        query: str, 
        top_k: Optional[int] = None
    ) -> str:
        """
        Raccourci: retrieve + format en une méthode.
        
        Returns:
            Contexte formaté prêt pour le prompt
        """
        pass
    
    def multi_query_retrieve(
        self, 
        queries: list[str], 
        top_k_per_query: int = 3
    ) -> list[dict]:
        """
        Recherche avec plusieurs requêtes et fusionne les résultats.
        
        Utile quand le patient a plusieurs symptômes.
        """
        pass
