from typing import Optional, Dict, List, Any


class EmergencyRules:
    """
    Règles d'urgence vitale basées sur les recommandations officielles.
    Sources: SAMU, SFMU, HAS
    """

    @staticmethod
    def check_respiratory_distress(const_data: dict) -> Optional[str]:
        """Détresse respiratoire."""
        spo2 = const_data.get("spo2", 100)
        fr = const_data.get("fr", 16)

        if spo2 < 90:
            return "Hypoxie sévère (SpO2 < 90%)"
        if spo2 < 92 and fr > 30:
            return "Détresse respiratoire (SpO2 < 92% + polypnée)"
        if fr < 10 or fr > 35:
            return "Fréquence respiratoire critique"

        return None

    @staticmethod
    def check_hemodynamic_shock(const_data: dict) -> Optional[str]:
        """État de choc hémodynamique."""
        fc = const_data.get("fc", 70)
        tas = const_data.get("tas", 120)

        # Normalisation TA (certains saisissent 12 au lieu de 120)
        tas_norm = tas if tas > 50 else tas * 10

        if tas_norm < 90:
            return "Hypotension artérielle (TAS < 90 mmHg)"
        if fc > 130:
            return "Tachycardie extrême (FC > 130 bpm)"
        if fc < 40:
            return "Bradycardie sévère (FC < 40 bpm)"
        if fc < 50 and tas_norm < 90:
            return "État de choc (bradycardie + hypotension)"

        return None

    @staticmethod
    def check_neurological_emergency(id_data: dict, const_data: dict) -> Optional[str]:
        """Urgences neurologiques."""
        # Hypothermie profonde
        temp = const_data.get("temp", 37.0)
        if temp < 32.0:
            return "Hypothermie profonde (< 32°C)"
        if temp > 40.0:
            return "Hyperthermie maligne (> 40°C)"

        # Fièvre chez populations vulnérables
        age = id_data.get("age", 30)
        if age <= 1 and temp > 38.0:
            return "Fièvre nourrisson (< 1 an, > 38°C)"
        if age <= 3 and temp > 38.5:
            return "Forte fièvre jeune enfant (< 3 ans, > 38.5°C)"
        if age >= 75 and temp > 39.5:
            return "Fièvre personne âgée (> 75 ans, > 39.5°C)"

        return None

    @staticmethod
    def check_hypertensive_emergency(const_data: dict) -> Optional[str]:
        """Urgence hypertensive."""
        tas = const_data.get("tas", 120)
        tad = const_data.get("tad", 80)

        tas_norm = tas if tas > 50 else tas * 10
        tad_norm = tad if tad > 30 else tad * 10

        if tas_norm >= 180 or tad_norm >= 120:
            return "Crise hypertensive (TAS ≥ 180 ou TAD ≥ 120)"

        return None


def _check_vital_emergency_rules(self, id_data: dict, const_data: dict) -> tuple[bool, List[str]]:
    """
    Vérifie toutes les règles d'urgence vitale.

    Returns:
        (is_rouge, list_of_red_flags)
    """
    red_flags = []

    # Vérifier toutes les catégories
    checks = [
        EmergencyRules.check_respiratory_distress(const_data),
        EmergencyRules.check_hemodynamic_shock(const_data),
        EmergencyRules.check_neurological_emergency(id_data, const_data),
        EmergencyRules.check_hypertensive_emergency(const_data),
    ]

    red_flags = [flag for flag in checks if flag is not None]

    return len(red_flags) > 0, red_flags
