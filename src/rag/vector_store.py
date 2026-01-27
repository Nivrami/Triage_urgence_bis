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
        import chromadb

        # Sauvegarder l'embedding provider
        self.embedding_provider = embedding_provider
        self.collection_name = collection_name
        self.persist_path = persist_path

        # Créer le client ChromaDB avec persistance
        self.client = chromadb.PersistentClient(path=persist_path)

        # Créer ou récupérer la collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Similarité cosinus
        )

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
        if not documents:
            return  # Rien à ajouter

        # 1. Extraire les textes et métadonnées
        texts = [doc["text"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        # 2. Générer des IDs si absents
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]

        # 3. Générer les embeddings pour tous les textes
        embeddings = self.embedding_provider.embed_batch(texts)

        # 4. Ajouter à ChromaDB
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

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
        # Convertir en format documents
        documents = []
        for i, text in enumerate(texts):
            doc = {"text": text}
            # Ajouter des métadonnées (ou mettre un dict vide avec une clé par défaut)
            if metadatas and i < len(metadatas) and metadatas[i]:
                doc["metadata"] = metadatas[i]
            else:
                # ChromaDB nécessite des métadonnées non vides
                doc["metadata"] = {"type": "text"}
            documents.append(doc)

        self.add_documents(documents, ids)

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
        # 1. Générer l'embedding de la requête
        query_embedding = self.embedding_provider.embed_text(query)

        # 2. Chercher dans ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata  # Filtre optionnel
        )

        # 3. Formater les résultats
        documents = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                documents.append({
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "score": results["distances"][0][i]  # Score de similarité
                })

        return documents

    def search_with_scores(
        self,
        query: str,
        top_k: int = 5
    ) -> list[tuple[dict, float]]:
        """Recherche avec scores de similarité."""
        results = self.search(query, top_k)
        return [(doc, doc["score"]) for doc in results]

    def delete_collection(self) -> None:
        """Supprime la collection."""
        self.client.delete_collection(name=self.collection_name)

    def get_collection_stats(self) -> dict:
        """
        Retourne les statistiques de la collection.

        Returns:
            {"count": int, "name": str, ...}
        """
        return {
            "count": self.collection.count(),
            "name": self.collection_name,
            "persist_path": self.persist_path
        }

    def update_document(self, doc_id: str, new_text: str, new_metadata: dict) -> None:
        """Met à jour un document."""
        # Générer le nouvel embedding
        new_embedding = self.embedding_provider.embed_text(new_text)

        # Mettre à jour dans ChromaDB
        self.collection.update(
            ids=[doc_id],
            documents=[new_text],
            embeddings=[new_embedding],
            metadatas=[new_metadata]
        )

    def delete_document(self, doc_id: str) -> None:
        """Supprime un document."""
        self.collection.delete(ids=[doc_id])

    def persist(self) -> None:
        """Force la persistance (si pas automatique)."""
        # ChromaDB PersistentClient persiste automatiquement
        # Cette méthode existe pour compatibilité avec d'autres backends
        pass
