"""
Conversation Storage - Sauvegarde et chargement des conversations
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import uuid


class ConversationStorage:
    """Gere la persistance des conversations sur disque."""

    def __init__(self, storage_dir: str = "data/conversations"):
        """
        Args:
            storage_dir: Dossier de stockage des conversations
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_conversation(
        self,
        messages: List[Dict],
        patient_data: Dict,
        prediction: Optional[Dict] = None,
        conversation_id: Optional[str] = None,
    ) -> str:
        """
        Sauvegarde une conversation complete.

        Args:
            messages: Liste des messages [{role, content}, ...]
            patient_data: Donnees du patient (age, sex, symptoms, vitals)
            prediction: Resultat de prediction ML (optionnel)
            conversation_id: ID existant pour mise a jour (optionnel)

        Returns:
            ID de la conversation sauvegardee
        """
        if not conversation_id:
            conversation_id = str(uuid.uuid4())[:8]

        timestamp = datetime.now().isoformat()

        conversation = {
            "id": conversation_id,
            "timestamp": timestamp,
            "messages": messages,
            "patient_data": patient_data,
            "prediction": prediction,
        }

        # Nom de fichier avec date et ID
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conv_{date_str}_{conversation_id}.json"
        filepath = self.storage_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)

        return conversation_id

    def load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Charge une conversation par son ID.

        Args:
            conversation_id: ID de la conversation

        Returns:
            Dictionnaire de la conversation ou None si non trouvee
        """
        # Chercher le fichier correspondant
        for filepath in self.storage_dir.glob(f"conv_*_{conversation_id}.json"):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)

        return None

    def list_conversations(self, limit: int = 20) -> List[Dict]:
        """
        Liste les conversations recentes.

        Args:
            limit: Nombre maximum de conversations a retourner

        Returns:
            Liste de resumes de conversations (id, timestamp, patient_name, severity)
        """
        conversations = []

        # Lister tous les fichiers JSON
        files = sorted(self.storage_dir.glob("conv_*.json"), reverse=True)

        for filepath in files[:limit]:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Extraire un resume
                patient = data.get("patient_data", {})
                prediction = data.get("prediction", {})

                summary = {
                    "id": data.get("id"),
                    "timestamp": data.get("timestamp"),
                    "filename": filepath.name,
                    "patient_name": patient.get("name", "Inconnu"),
                    "patient_age": patient.get("age"),
                    "symptoms": patient.get("symptoms", []),
                    "severity": prediction.get("severity_level") if prediction else None,
                    "message_count": len(data.get("messages", [])),
                }
                conversations.append(summary)
            except (json.JSONDecodeError, KeyError):
                continue

        return conversations

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Supprime une conversation.

        Args:
            conversation_id: ID de la conversation

        Returns:
            True si supprimee, False sinon
        """
        for filepath in self.storage_dir.glob(f"conv_*_{conversation_id}.json"):
            filepath.unlink()
            return True
        return False

    def export_to_markdown(self, conversation_id: str) -> Optional[str]:
        """
        Exporte une conversation en format Markdown.

        Args:
            conversation_id: ID de la conversation

        Returns:
            Contenu Markdown ou None
        """
        data = self.load_conversation(conversation_id)
        if not data:
            return None

        patient = data.get("patient_data", {})
        prediction = data.get("prediction", {})
        messages = data.get("messages", [])

        md = f"""# Rapport de Triage - {data.get('timestamp', 'Date inconnue')}

## Informations Patient

- **Nom:** {patient.get('name', 'Non renseigne')}
- **Age:** {patient.get('age', 'Non renseigne')} ans
- **Sexe:** {patient.get('sex', 'Non renseigne')}
- **Symptomes:** {', '.join(patient.get('symptoms', [])) or 'Aucun'}

## Constantes Vitales

"""
        vitals = patient.get("vitals", {})
        if vitals:
            md += f"- FC: {vitals.get('FC', '—')} bpm\n"
            md += f"- FR: {vitals.get('FR', '—')} /min\n"
            md += f"- SpO2: {vitals.get('SpO2', '—')} %\n"
            md += f"- TA: {vitals.get('TA_systolique', '—')}/{vitals.get('TA_diastolique', '—')} mmHg\n"
            md += f"- Temperature: {vitals.get('Temperature', '—')} C\n"
        else:
            md += "Non renseignees\n"

        if prediction:
            md += f"""
## Prediction ML

- **Niveau:** {prediction.get('severity_level', 'Non determine')}
- **Label:** {prediction.get('label', '')}
- **Action:** {prediction.get('action', '')}
- **Confiance:** {prediction.get('confidence', 0)*100:.1f}%

### Red Flags
{chr(10).join(['- ' + f for f in prediction.get('red_flags', [])]) or 'Aucun'}

### Justification
{prediction.get('justification', 'Non disponible')}
"""

        md += "\n## Conversation\n\n"
        for msg in messages:
            role = "Patient" if msg["role"] == "user" else "Assistant"
            md += f"**{role}:** {msg['content']}\n\n"

        return md


# Singleton pour acces global
_storage_instance = None


def get_storage(storage_dir: str = "data/conversations") -> ConversationStorage:
    """Retourne l'instance singleton du storage."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = ConversationStorage(storage_dir)
    return _storage_instance
