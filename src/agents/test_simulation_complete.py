"""
Test complet de la simulation automatique.

Génère un patient → Conversation infirmier/patient → Affiche le résultat
"""

from src.llm.llm_factory import LLMFactory
from src.agents.patient_generator import PatientGenerator
from src.agents.patient_simulator import PatientSimulator
from src.agents.nurse_agent import NurseAgent
from src.models.conversation import ConversationHistory


def run_complete_simulation(pathology_description: str):
    """
    Exécute une simulation complète.
    
    Args:
        pathology_description: Description de la pathologie
    """
    print("=" * 70)
    print(" SIMULATION DE TRIAGE AUX URGENCES")
    print("=" * 70)
    
    # 1. Initialiser le LLM
    print("\n Initialisation du LLM Mistral...")
    llm = LLMFactory.create("mistral", "mistral-small-latest")
    print(" LLM prêt")
    
    # 2. Générer le patient
    print(f"\n Génération du patient : {pathology_description}")
    generator = PatientGenerator(llm)
    patient = generator.generate_from_description(pathology_description)
    
    print(f"\n PATIENT GÉNÉRÉ :")
    print(f"   Nom : {patient.prenom} {patient.nom}")
    print(f"   Âge : {patient.age} ans ({patient.sexe})")
    print(f"   Symptômes : {', '.join(patient.symptomes_exprimes)}")
    if patient.constantes:
        print(f"   FC : {patient.constantes.fc} bpm")
        print(f"   SpO2 : {patient.constantes.spo2}%")
        print(f"   Température : {patient.constantes.temperature}°C")
    print(f"   Depuis : {patient.duree_symptomes}")
    
    # 3. Créer les agents
    print("\n Création des agents...")
    patient_simulator = PatientSimulator(llm, patient)
    nurse = NurseAgent(llm, max_questions=6)
    print(" Agents prêts")
    
    # 4. Plainte initiale
    print("\n" + "=" * 70)
    print(" DÉBUT DE LA CONSULTATION")
    print("=" * 70)
    
    initial_complaint = patient_simulator.get_initial_complaint()
    print(f"\n Patient arrive :")
    print(f"   {initial_complaint}")
    
    conversation = ConversationHistory()
    conversation.add_assistant_message(initial_complaint)
    
    # 5. Boucle de questions
    question_num = 1
    while nurse.should_continue():
        # Infirmier pose une question
        question = nurse.ask_next_question()
        print(f"\n Infirmier (Q{question_num}) :")
        print(f"   {question}")
        
        conversation.add_user_message(question)
        nurse.add_to_history("nurse", question)
        
        # Patient répond
        response = patient_simulator.respond(question)
        print(f"\n Patient :")
        print(f"   {response}")
        
        conversation.add_assistant_message(response)
        nurse.add_to_history("patient", response)
        
        question_num += 1
    
    # 6. Résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DE LA CONSULTATION")
    print("=" * 70)
    
    print(f"\n📝 Nombre d'échanges : {len(conversation.messages)}")
    print(f"\n👤 Profil patient :")
    print(f"   - Âge : {patient.age} ans")
    print(f"   - Symptômes rapportés : {', '.join(patient.symptomes_exprimes)}")
    print(f"   - Antécédents : {', '.join(patient.antecedents) if patient.antecedents else 'Aucun'}")
    
    if patient.constantes:
        print(f"\n🩺 Constantes réelles (connues du système) :")
        print(f"   - FC : {patient.constantes.fc} bpm")
        print(f"   - FR : {patient.constantes.fr} /min")
        print(f"   - SpO2 : {patient.constantes.spo2}%")
        print(f"   - TA : {patient.constantes.ta_systolique}/{patient.constantes.ta_diastolique} mmHg")
        print(f"   - Température : {patient.constantes.temperature}°C")
    
    print("\n" + "=" * 70)
    print("✅ SIMULATION TERMINÉE")
    print("=" * 70)
    
    return {
        "patient": patient,
        "conversation": conversation
    }


if __name__ == "__main__":
    # Test 1 : Cas grave
    print("\n🔴 TEST 1 : CAS GRAVE (ROUGE)")
    result1 = run_complete_simulation(
        "Homme de 62 ans avec suspicion d'infarctus du myocarde"
    )
    
    print("\n\n" + "=" * 70)
    