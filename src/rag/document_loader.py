"""
Document Loader - Charge les documents markdown du RAG
"""

from pathlib import Path
from typing import List, Dict
import re


class DocumentLoader:
    """Charge et parse les documents médicaux markdown."""
    
    def __init__(self, documents_dir: str = "data/rag_document"):
        """
        Args:
            documents_dir: Chemin vers le dossier contenant les documents
        """
        self.documents_dir = Path(documents_dir)
        
    def load_all_documents(self) -> List[Dict[str, str]]:
        """
        Charge tous les documents markdown du dossier.
        
        Returns:
            Liste de dictionnaires {content, metadata}
        """
        
        documents = []
        
        # Charger tous les fichiers .md
        for md_file in sorted(self.documents_dir.glob("*.md")):
            doc = self.load_document(md_file)
            if doc:
                documents.append(doc)
        
        print(f"✅ {len(documents)} documents chargés")
        return documents
    
    def load_document(self, file_path: Path) -> Dict:
        """
        Charge un document markdown unique.
        
        Returns:
            Dict avec content et metadata
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraire le titre (première ligne # )
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem
            
            return {
                "content": content,
                "metadata": {
                    "source": str(file_path),
                    "title": title,
                    "filename": file_path.name
                }
            }
        except Exception as e:
            print(f"❌ Erreur chargement {file_path}: {e}")
            return None
    
    def chunk_document(self, document: Dict, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """
        Découpe un document en chunks avec overlap.
        
        Args:
            document: Document à découper
            chunk_size: Taille max d'un chunk (caractères)
            overlap: Chevauchement entre chunks
            
        Returns:
            Liste de chunks avec metadata
        """
        content = document["content"]
        metadata = document["metadata"]
        
        # Découper par sections (## )
        sections = self._split_by_headers(content)
        
        chunks = []
        for section_title, section_content in sections:
            # Si section trop grande, découper
            if len(section_content) > chunk_size:
                sub_chunks = self._split_text(section_content, chunk_size, overlap)
                for i, chunk_text in enumerate(sub_chunks):
                    chunks.append({
                        "content": chunk_text,
                        "metadata": {
                            **metadata,
                            "section": section_title,
                            "chunk_id": f"{metadata['filename']}_{section_title}_{i}"
                        }
                    })
            else:
                chunks.append({
                    "content": section_content,
                    "metadata": {
                        **metadata,
                        "section": section_title,
                        "chunk_id": f"{metadata['filename']}_{section_title}"
                    }
                })
        
        return chunks
    
    def _split_by_headers(self, content: str) -> List[tuple]:
        """
        Découpe le contenu par sections (headers ##).
        
        Returns:
            Liste de (titre_section, contenu_section)
        """
        sections = []
        
        # Pattern pour détecter headers niveau 2 et plus (## )
        pattern = r'^(#{2,})\s+(.+)$'
        
        current_section = "Introduction"
        current_content = []
        
        for line in content.split('\n'):
            match = re.match(pattern, line)
            if match:
                # Nouvelle section trouvée
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                current_section = match.group(2)
                current_content = [line]
            else:
                current_content.append(line)
        
        # Ajouter dernière section
        if current_content:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections
    
    def _split_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        Découpe un texte en chunks de taille fixe avec overlap.
        
        Args:
            text: Texte à découper
            chunk_size: Taille max d'un chunk
            overlap: Chevauchement
            
        Returns:
            Liste de chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Essayer de couper à un point, ligne vide ou fin de phrase
            if end < len(text):
                # Chercher dernier point dans chunk
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n\n')
                
                cut_point = max(last_period, last_newline)
                if cut_point > chunk_size // 2:  # Au moins à mi-chemin
                    chunk = chunk[:cut_point + 1]
                    end = start + cut_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def load_and_chunk_all(self, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """
        Charge tous les documents et les découpe en chunks.
        
        Returns:
            Liste de chunks prêts pour vectorisation
        """
        documents = self.load_all_documents()
        
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc, chunk_size, overlap)
            all_chunks.extend(chunks)
        
        print(f"✅ {len(all_chunks)} chunks créés")
        return all_chunks


if __name__ == "__main__":
    # Test
    loader = DocumentLoader("data/rag_document")
    
    print(" Chargement des documents...")
    documents = loader.load_all_documents()
    
    print("\n Découpage en chunks...")
    chunks = loader.load_and_chunk_all(chunk_size=800, overlap=150)
    
    print(f"\n📊 Résumé:")
    print(f"- Documents : {len(documents)}")
    print(f"- Chunks : {len(chunks)}")
    print(f"\n📄 Exemple de chunk:")
    print(f"Content: {chunks[0]['content'][:200]}...")
    print(f"Metadata: {chunks[0]['metadata']}")
