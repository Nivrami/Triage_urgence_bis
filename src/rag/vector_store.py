"""
Interface avec la base de données vectorielle.

JUSTIFIER le choix de la base:
- ChromaDB: Simple, persistance facile, bon pour prototype
- FAISS: Plus performant à grande échelle, Facebook
- Pinecone: Cloud, scalable, mais payant
- Weaviate: Open source, features avancées
"""

from typing import Optional
from .embeddings import EmbeddingProvider


class VectorStore:
    """Interface avec la base vectorielle."""
    
    def __init__(
        self, 
        persist_path: str,
        embedding_provider: EmbeddingProvider,
        collection_name: str = "medical_docs"
    ) -> None:
        """
        Initialise la base vectorielle.
        
        Args:
            persist_path: Chemin pour la persistance
            embedding_provider: Provider d'embeddings
            collection_name: Nom de la collection
            
        JUSTIFIER: Pourquoi ChromaDB?
        - Simple à utiliser
        - Persistance automatique
        - Pas de serveur externe
        - Suffisant pour un projet de cette taille
        """
        pass
    
    def add_documents(
        self, 
        documents: list[dict],
        ids: Optional[list[str]] = None
    ) -> None:
        """
        Ajoute des documents à la base.
        
        Args:
            documents: Liste de {"text": ..., "metadata": {...}}
            ids: IDs optionnels (générés si absents)
        """
        pass
    
    def add_texts(
        self,
        texts: list[str],
        metadatas: Optional[list[dict]] = None,
        ids: Optional[list[str]] = None
    ) -> None:
        """
        Ajoute des textes bruts.
        
        Args:
            texts: Liste de textes
            metadatas: Métadonnées associées
            ids: IDs optionnels
        """
        pass
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        filter_metadata: Optional[dict] = None
    ) -> list[dict]:
        """
        Recherche les documents similaires.
        
        Args:
            query: Requête de recherche
            top_k: Nombre de résultats
            filter_metadata: Filtre sur les métadonnées
            
        Returns:
            Liste de {"text": ..., "metadata": ..., "score": ...}
        """
        pass
    
    def search_with_scores(
        self, 
        query: str, 
        top_k: int = 5
    ) -> list[tuple[dict, float]]:
        """Recherche avec scores de similarité."""
        pass
    
    def delete_collection(self) -> None:
        """Supprime la collection."""
        pass
    
    def get_collection_stats(self) -> dict:
        """
        Retourne les statistiques de la collection.
        
        Returns:
            {"count": int, "name": str, ...}
        """
        pass
    
    def update_document(self, doc_id: str, new_text: str, new_metadata: dict) -> None:
        """Met à jour un document."""
        pass
    
    def delete_document(self, doc_id: str) -> None:
        """Supprime un document."""
        pass
    
    def persist(self) -> None:
        """Force la persistance (si pas automatique)."""
        pass
