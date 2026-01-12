"""
Chargement et prétraitement des documents médicaux.
"""

from typing import Optional


class DocumentLoader:
    """
    Charge et prétraite les documents pour le RAG.
    
    Sources supportées:
    - HuggingFace datasets
    - Fichiers locaux (txt, json, csv)
    - Wikipedia (optionnel)
    """
    
    def __init__(
        self, 
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> None:
        """
        Initialise le loader.
        
        Args:
            chunk_size: Taille des chunks en caractères
            chunk_overlap: Chevauchement entre chunks
            
        JUSTIFIER: Pourquoi ces valeurs?
        - chunk_size=500: Assez pour le contexte, pas trop pour l'embedding
        - chunk_overlap=50: Évite de couper des phrases importantes
        """
        pass
    
    def load_from_huggingface(
        self, 
        dataset_name: str,
        split: str = "train",
        text_column: str = "text"
    ) -> list[dict]:
        """
        Charge depuis HuggingFace.
        
        Args:
            dataset_name: Nom du dataset (ex: "mlabonne/medical-cases-fr")
            split: Split à charger
            text_column: Colonne contenant le texte
            
        Returns:
            Liste de {"text": ..., "metadata": {...}}
        """
        pass
    
    def load_from_file(self, file_path: str) -> list[dict]:
        """
        Charge depuis un fichier local.
        
        Supporte: .txt, .json, .csv
        """
        pass
    
    def load_from_directory(self, dir_path: str) -> list[dict]:
        """Charge tous les fichiers d'un répertoire."""
        pass
    
    def chunk_document(self, document: dict) -> list[dict]:
        """
        Découpe un document en chunks.
        
        Args:
            document: {"text": ..., "metadata": {...}}
            
        Returns:
            Liste de chunks avec métadonnées préservées
        """
        pass
    
    def chunk_documents(self, documents: list[dict]) -> list[dict]:
        """Découpe plusieurs documents."""
        pass
    
    def preprocess_text(self, text: str) -> str:
        """
        Nettoie le texte.
        
        - Supprime les espaces multiples
        - Normalise les caractères
        - Supprime les caractères spéciaux inutiles
        """
        pass
    
    def load_gravity_categories(self) -> list[dict]:
        """
        Charge les catégories de gravité depuis les ressources du projet.
        
        Utilise les données de Ressources_Projet.pdf
        """
        pass
    
    def load_medical_cases_fr(self) -> list[dict]:
        """
        Charge le dataset medical-cases-fr de HuggingFace.
        
        Dataset recommandé dans les ressources.
        """
        pass
