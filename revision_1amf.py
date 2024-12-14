import pandas as pd
import streamlit as st
import os
import json
import random

# Titre de l'application
st.title("Révision pour le Certificat AMF")

# Demander un nom d'utilisateur
username = st.text_input("Entrez votre nom d'utilisateur :")
if not username:
    st.stop()

# Générer un fichier spécifique pour l'utilisateur
used_questions_file = f"used_questions_{username}.json"

# Charger les données directement depuis un fichier inclus dans le projet
file_path = "AMF.csv"  # Le fichier doit être dans le même dossier
try:
    data = pd.read_csv(file_path, encoding="ISO-8859-1", on_bad_lines="skip", delimiter=";")
    required_columns = ['Categorie', 'Question finale', 'Choix_A', 'Choix_B', 'Choix_C', 'Reponse']
    if not all(col in data.columns for col in required_columns):
        st.error("Les colonnes attendues dans le fichier sont manquantes ou mal formatées.")
        st.stop()
except FileNotFoundError:
    st.error(f"Le fichier {file_path} est introuvable. Assurez-vous qu'il est dans le même dossier que ce script.")
    st.stop()
except Exception as e:
    st.error(f"Une erreur est survenue lors du chargement du fichier : {e}")
    st.stop()

# Filtrer les questions par catégorie
category_a = data[data['Categorie'] == 'A']
category_c = data[data['Categorie'] == 'C']

# Charger les questions déjà utilisées
if os.path.exists(used_questions_file):
    with open(used_questions_file, "r") as f:
        used_questions = set(json.load(f))
else:
    used_questions = set()

# Initialiser les états de session
if 'used_questions' not in st.session_state:
    st.session_state['used_questions'] = used_questions
if 'correct_count' not in st.session_state:
    st.session_state['correct_count'] = 0
if 'correct_a' not in st.session_state:
    st.session_state['correct_a'] = 0
if 'correct_c' not in st.session_state:
    st.session_state['correct_c'] = 0
if 'responses' not in st.session_state:
    st.session_state['responses'] = []
if 'shuffled_questions' not in st.session_state:
    st.session_state['shuffled_questions'] = []

# Tirer toutes les questions au démarrage de l'examen
def initialize_questions():
    available_a = category_a[~category_a['Question finale'].isin(st.session_state['used_questions'])]
    available_c = category_c[~category_c['Question finale'].isin(st.session_state['used_questions'])]

    questions_a = available_a.sample(n=min(len(available_a), 33), random_state=1).to_dict(orient='records')
    questions_c = available_c.sample(n=min(len(available_c), 87), random_state=1).to_dict(orient='records')

    st.session_state['shuffled_questions'] = random.sample(questions_a + questions_c, len(questions_a + questions_c))

if not st.session_state['shuffled_questions']:
    initialize_questions()

# Fonction pour afficher toutes les questions directement
def show_all_questions():
    for i, question in enumerate(st.session_state['shuffled_questions']):
        st.write(f"**Question {i + 1}: {question['Question finale']}**")
        st.write(f"A) {question['Choix_A']}")
        st.write(f"B) {question['Choix_B']}")
        st.write(f"C) {question['Choix_C']}")

        answer = st.radio("Votre réponse :", ["A", "B", "C"], key=f"question_{i + 1}")

        response_record = {
            "question": question['Question finale'],
            "choices": {
                "A": question['Choix_A'],
                "B": question['Choix_B'],
                "C": question['Choix_C']
            },
            "your_answer": answer,
            "correct_answer": question['Reponse'],
            "is_correct": answer == question['Reponse'],
            "category": question['Categorie']
        }
        st.session_state['responses'].append(response_record)

# Fonction pour terminer l'examen
def finish_exam():
    st.write("### Examen terminé !")
    st.write(f"**Résultats :**")
    correct_count = sum(1 for r in st.session_state['responses'] if r['is_correct'])
    correct_a = sum(1 for r in st.session_state['responses'] if r['is_correct'] and r['category'] == 'A')
    correct_c = sum(1 for r in st.session_state['responses'] if r['is_correct'] and r['category'] == 'C')
    st.write(f"- Catégorie A : {correct_a} bonnes réponses sur 33")
    st.write(f"- Catégorie C : {correct_c} bonnes réponses sur 87")
    st.write(f"- **Score total** : {correct_count} bonnes réponses sur 120")

    if st.button("Faire un autre examen blanc"):
        st.session_state['used_questions'] = set()
        st.session_state['responses'] = []
        st.session_state['shuffled_questions'] = []
        initialize_questions()

# Lancer l'examen
if st.button("Commencer l'examen"):
    show_all_questions()

if st.button("Valider mes réponses"):
    finish_exam()
