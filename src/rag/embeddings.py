"""
Gestion des embeddings pour le RAG.

JUSTIFIER le choix du modèle d'embedding:
- all-MiniLM-L6-v2: Gratuit, rapide, 384 dims, bon pour le français
- text-embedding-3-small (OpenAI): Payant mais meilleur
- ClinicalBERT: Spécialisé médical (mentionné dans les ressources)
- camembert-base: Entraîné sur du français
"""

from typing import Optional


class EmbeddingProvider:
    """Gestion des embeddings textuels."""
    
    # Modèles supportés avec leurs dimensions
    SUPPORTED_MODELS = {
        "all-MiniLM-L6-v2": {"dim": 384, "type": "sentence-transformers"},
        "paraphrase-multilingual-MiniLM-L12-v2": {"dim": 384, "type": "sentence-transformers"},
        "text-embedding-3-small": {"dim": 1536, "type": "openai"},
        "text-embedding-3-large": {"dim": 3072, "type": "openai"},
    }
    
    def __init__(
        self, 
        model_name: str = "all-MiniLM-L6-v2",
        api_key: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialise le provider d'embeddings.
        
        Args:
            model_name: Nom du modèle à utiliser
            api_key: Clé API (pour OpenAI)
            
        JUSTIFIER ton choix de modèle ici.
        """
        pass
    
    def embed_text(self, text: str) -> list[float]:
        """
        Génère l'embedding d'un texte.
        
        Args:
            text: Texte à encoder
            
        Returns:
            Vecteur d'embedding
        """
        pass
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Génère les embeddings pour plusieurs textes.
        
        Plus efficace que d'appeler embed_text en boucle.
        
        Args:
            texts: Liste de textes
            
        Returns:
            Liste de vecteurs
        """
        pass
    
    def get_dimension(self) -> int:
        """Retourne la dimension des vecteurs."""
        pass
    
    def get_model_info(self) -> dict:
        """Informations sur le modèle."""
        pass
    
    def _load_sentence_transformer(self, model_name: str) -> None:
        """Charge un modèle sentence-transformers."""
        pass
    
    def _load_openai_embeddings(self, api_key: str) -> None:
        """Configure les embeddings OpenAI."""
        pass
