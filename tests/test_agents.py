"""
Tests pour les agents.
"""

import pytest


class TestTriageAgent:
    """Tests pour l'agent de triage."""
    
    def test_should_stop_interview_enough_info(self):
        """Test arrêt avec assez d'infos."""
        pass
    
    def test_should_stop_interview_not_enough(self):
        """Test continuation sans assez d'infos."""
        pass
    
    def test_extract_patient_data(self):
        """Test extraction des données patient."""
        pass
    
    def test_predict_gravity(self):
        """Test de prédiction de gravité."""
        pass


class TestPatientSimulator:
    """Tests pour le simulateur de patient."""
    
    def test_set_profile(self):
        """Test de définition du profil."""
        pass
    
    def test_generate_random_profile(self):
        """Test de génération aléatoire."""
        pass
    
    def test_get_true_gravity(self):
        """Test récupération vraie gravité."""
        pass
    
    def test_run_response_coherent(self):
        """Test que les réponses sont cohérentes avec le profil."""
        pass
