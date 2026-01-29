"""
Vector Store - Gestion de la base vectorielle ChromaDB
"""
 
from chromadb.config import Settings
from typing import List, Dict, Optional
from pathlib import Path
import json
import chromadb  
from sentence_transformers import SentenceTransformer  


class VectorStore:
    """Gère l'indexation et la recherche dans ChromaDB."""
    
    def __init__(
        self, 
        persist_directory: str = "data/vector_db",
        collection_name: str = "triage_medical",
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ):
        """
        Args:
            persist_directory: Dossier de persistance ChromaDB
            collection_name: Nom de la collection
            embedding_model: Modèle d'embeddings (français supporté)
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialiser ChromaDB avec persistance
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Charger le modèle d'embeddings
        print(f" Chargement modèle embeddings:{embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        print(" Modèle chargé")
        
        # Créer ou récupérer collection
        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        """Récupère ou crée la collection ChromaDB."""
        try:
            # Essayer de récupérer collection existante
            collection = self.client.get_collection(name=self.collection_name)
            print(f"✅ Collection '{self.collection_name}' chargée ({collection.count()} documents)")
        except: 
            # Créer nouvelle collection
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Base de connaissances médicales pour triage"}
            )
            print(f"✅ Collection '{self.collection_name}' créée")
        
        return collection
    
    def add_documents(self, chunks: List[Dict]) -> None:
        """
        Ajoute des documents (chunks) à la collection.
        
        Args:
            chunks: Liste de dicts {content, metadata}
        """
        if not chunks:
            print("⚠️ Aucun chunk à ajouter")
            return
        
        print(f"\n📤 Indexation de {len(chunks)} chunks...")
        
        # Préparer les données
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk["content"])
            
            # ChromaDB nécessite metadata en dict simple (pas de nested)
            metadata = {
                "source": chunk["metadata"].get("source", "unknown"),
                "title": chunk["metadata"].get("title", "unknown"),
                "section": chunk["metadata"].get("section", "unknown"),
                "chunk_id": chunk["metadata"].get("chunk_id", f"chunk_{i}")
            }
            metadatas.append(metadata)
            ids.append(f"doc_{i}")
        
        # Générer embeddings
        print(" Génération des embeddings...")
        embeddings = self.embedding_model.encode(
            documents,
            show_progress_bar=True,
            convert_to_numpy=True
        ).tolist()
        
        # Ajouter à ChromaDB
        print(" Ajout à ChromaDB...")
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ {len(chunks)} chunks indexés")
        print(f"📊 Total collection : {self.collection.count()} documents")
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Recherche sémantique dans la base.
        
        Args:
            query: Question ou texte de recherche
            n_results: Nombre de résultats à retourner
            filter_metadata: Filtres optionnels (ex: {"title": "..."})
            
        Returns:
            Liste de résultats avec scores
        """
        # Générer embedding de la query
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True
        ).tolist()[0]
        
        # Rechercher
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_metadata
        )
        
        # Formater résultats
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i],
                "id": results['ids'][0][i]
            })
        
        return formatted_results
    
    def clear_collection(self) -> None:
        """Vide complètement la collection."""
        print(f"🗑️ Suppression collection '{self.collection_name}'...")
        self.client.delete_collection(name=self.collection_name)
        self.collection = self._get_or_create_collection()
        print("✅ Collection réinitialisée")
    
    def get_stats(self) -> Dict:
        """Retourne des statistiques sur la collection."""
        count = self.collection.count()
        
        return {
            "total_documents": count,
            "collection_name": self.collection_name,
            "persist_directory": str(self.persist_directory)
        }


class RAGRetriever:
    """Retriever pour récupérer contexte pertinent."""
    
    def __init__(self, vector_store: VectorStore):
        """
        Args:
            vector_store: Instance de VectorStore
        """
        self.vector_store = vector_store
    
    def retrieve_context(
        self, 
        query: str, 
        top_k: int = 3,
        filter_by_document: Optional[str] = None
    ) -> str:
        """
        Récupère le contexte pertinent pour une query.
        
        Args:
            query: Question de l'utilisateur
            top_k: Nombre de chunks à récupérer
            filter_by_document: Filtrer par document spécifique
            
        Returns:
            Contexte formaté prêt pour le LLM
        """
        # Filtres optionnels
        where_filter = None
        if filter_by_document:
            where_filter = {"title": filter_by_document}
        
        # Rechercher
        results = self.vector_store.search(
            query=query,
            n_results=top_k,
            filter_metadata=where_filter
        )
        
        if not results:
            return "Aucun contexte trouvé."
        
        # Formater contexte
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result['metadata'].get('title', 'Document')
            section = result['metadata'].get('section', '')
            content = result['content']
            
            context_parts.append(
                f"[Source {i}: {source} - {section}]\n{content}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def retrieve_with_scores(
        self, 
        query: str, 
        top_k: int = 5
    ) -> List[Dict]:
        """
        Récupère contexte avec scores de pertinence.
        
        Returns:
            Liste de {content, metadata, score}
        """
        results = self.vector_store.search(query, n_results=top_k)
        
        # Convertir distance en score (plus proche = meilleur)
        for result in results:
            # Distance L2 : plus petit = meilleur
            # Convertir en score 0-1 (1 = parfait)
            result['relevance_score'] = 1 / (1 + result['distance'])
        
        return results


def build_vector_store(
    documents_dir: str = "data/rag_document",
    persist_dir: str = "data/vector_db",
    force_rebuild: bool = False
) -> VectorStore:   
    """
    Construit la vector store complète.
    
    Args:
        documents_dir: Dossier des documents markdown
        persist_dir: Dossier de persistance ChromaDB
        force_rebuild: Si True, reconstruit même si existe
        
    Returns:
        VectorStore initialisée    
    """
    from .document_loader import DocumentLoader
    print(documents_dir)  
    
    vector_store = VectorStore(persist_directory=persist_dir)
    
    # Si déjà des documents et pas force_rebuild, ne rien faire
    if vector_store.collection.count() > 0 and not force_rebuild:
        print("✅ Vector store déjà initialisée")
        stats = vector_store.get_stats()
        print(f"📊 {stats['total_documents']} documents indexés")
        return vector_store
    
    # Sinon, charger et indexer
    if force_rebuild:
        vector_store.clear_collection()
    
    print("\n📚 Chargement des documents...")
    loader = DocumentLoader(documents_dir)
    chunks = loader.load_and_chunk_all(chunk_size=800, overlap=150)
    
    print("\n🗄️ Indexation dans ChromaDB...")
    vector_store.add_documents(chunks)
    
    print("\n✅ Vector store prête !")
    return vector_store


if __name__ == "__main__":
    # Test complet
    print("="*70)
    print("TEST VECTOR STORE")
    print("="*70)
    
    # Construire vector store
    vector_store = build_vector_store(
        documents_dir="data/rag_document",
        force_rebuild=False  # True pour reconstruire
    )
    
    # Test recherche
    print("\n" + "="*70)
    print("TEST RECHERCHE")
    print("="*70)
    
    retriever = RAGRetriever(vector_store)
    
    queries = [
        "Quelles questions poser pour une douleur thoracique ?",
        "Quels sont les critères pour le niveau ROUGE ?",
        "Que faire en cas d'infarctus ?"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 70)
        
        context = retriever.retrieve_context(query, top_k=2)
        print(context[:500] + "...\n")
