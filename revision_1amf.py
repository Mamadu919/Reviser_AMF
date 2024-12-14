import pandas as pd
import streamlit as st
import os
import random

# Titre de l'application
st.title("Révision pour le Certificat AMF")

# Demander un nom d'utilisateur
username = st.text_input("Entrez votre nom d'utilisateur :")
if not username:
    st.stop()

# Charger le fichier CSV
file_path = "AMF.csv"  # Chemin vers le fichier CSV
try:
    data = pd.read_csv(file_path, encoding="ISO-8859-1", on_bad_lines="skip", delimiter=";")
    data.columns = data.columns.str.strip()
    required_columns = ['Categorie', 'Question finale', 'Choix_A', 'Choix_B', 'Choix_C', 'Reponse']
    if not all(col in data.columns for col in required_columns):
        st.error(f"Colonnes manquantes ou mal formatées. Colonnes actuelles : {list(data.columns)}")
        st.stop()
except FileNotFoundError:
    st.error("Le fichier CSV est introuvable.")
    st.stop()
except Exception as e:
    st.error(f"Une erreur est survenue lors du chargement du fichier : {e}")
    st.stop()

# Filtrer les questions par catégorie
category_a = data[data['Categorie'] == 'A']
category_c = data[data['Categorie'] == 'C']

# Initialiser les états de session
if 'exam_started' not in st.session_state:
    st.session_state['exam_started'] = False
if 'responses' not in st.session_state:
    st.session_state['responses'] = []
if 'correct_a' not in st.session_state:
    st.session_state['correct_a'] = 0
if 'correct_c' not in st.session_state:
    st.session_state['correct_c'] = 0
if 'questions' not in st.session_state:
    st.session_state['questions'] = []

# Fonction pour initialiser les questions
def initialize_questions():
    questions_a = category_a.sample(n=33, random_state=1).to_dict(orient='records')
    questions_c = category_c.sample(n=87, random_state=1).to_dict(orient='records')
    st.session_state['questions'] = random.sample(questions_a + questions_c, len(questions_a + questions_c))
    st.session_state['exam_started'] = True
    st.session_state['responses'] = []
    st.session_state['correct_a'] = 0
    st.session_state['correct_c'] = 0

# Fonction pour afficher les questions
def show_questions():
    for idx, question in enumerate(st.session_state['questions']):
        st.write(f"**Question {idx + 1}: {question['Question finale']}**")
        st.write(f"A) {question['Choix_A']}")
        st.write(f"B) {question['Choix_B']}")
        st.write(f"C) {question['Choix_C']}")

        # Enregistrer la réponse de l'utilisateur
        user_answer = st.radio(
            "Votre réponse :",
            options=["A", "B", "C"],
            key=f"question_{idx}"
        )

        # Ajouter la réponse uniquement si elle n'est pas encore enregistrée
        if idx >= len(st.session_state['responses']):
            st.session_state['responses'].append({
                "question": question['Question finale'],
                "correct_answer": question['Reponse'],
                "user_answer": user_answer,
                "is_correct": user_answer == question['Reponse'],
                "categorie": question['Categorie']
            })

# Fonction pour afficher les résultats
def show_results():
    correct_a = sum(1 for r in st.session_state['responses'] if r['is_correct'] and r['categorie'] == 'A')
    correct_c = sum(1 for r in st.session_state['responses'] if r['is_correct'] and r['categorie'] == 'C')

    st.session_state['correct_a'] = correct_a
    st.session_state['correct_c'] = correct_c

    st.write("### Résultats de l'examen")
    st.write(f"- **Catégorie A :** {correct_a} bonnes réponses sur 33.")
    st.write(f"- **Catégorie C :** {correct_c} bonnes réponses sur 87.")
    st.write(f"- **Score total :** {correct_a + correct_c} bonnes réponses sur 120.")

    pourcentage_a = (correct_a / 33) * 100
    pourcentage_c = (correct_c / 87) * 100
    st.write(f"- **Pourcentage Catégorie A :** {pourcentage_a:.2f}%")
    st.write(f"- **Pourcentage Catégorie C :** {pourcentage_c:.2f}%")

    if pourcentage_a >= 80 and pourcentage_c >= 80:
        st.success("Félicitations ! Vous avez réussi l'examen.")
    else:
        st.error("Désolé, vous n'avez pas réussi. Vous devez atteindre au moins 80% dans chaque catégorie.")

    st.write("### Détails des réponses")
    for response in st.session_state['responses']:
        st.write(f"**Question :** {response['question']}")
        st.write(f"- **Votre réponse :** {response['user_answer']} - **Réponse correcte :** {response['correct_answer']}")
        if response['is_correct']:
            st.success("Bonne réponse")
        else:
            st.error("Mauvaise réponse")
        st.write("---")

# Fonction pour recommencer un examen
def restart_exam():
    st.session_state['exam_started'] = False
    st.session_state['responses'] = []
    st.session_state['correct_a'] = 0
    st.session_state['correct_c'] = 0
    st.session_state['questions'] = []

# Workflow principal
if not st.session_state['exam_started']:
    if st.button("Commencer l'examen"):
        initialize_questions()

elif st.session_state['exam_started']:
    show_questions()
    if st.button("Valider l'examen"):
        show_results()
        if st.button("Faire un autre examen blanc"):
            restart_exam()
