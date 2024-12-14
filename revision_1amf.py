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
except FileNotFoundError:
    st.error(f"Le fichier {file_path} est introuvable. Assurez-vous qu'il est dans le même dossier que ce script.")
    st.stop()
except Exception as e:
    st.error(f"Une erreur est survenue lors du chargement du fichier : {e}")
    st.stop()

# Filtrer les questions par catégorie
try:
    category_a = data[data['Categorie'] == 'A']  # Utilise la colonne 'Categorie'
    category_c = data[data['Categorie'] == 'C']
except KeyError:
    st.error("Les colonnes attendues dans le fichier sont manquantes ou mal formatées.")
    st.stop()

# Charger les questions déjà utilisées
if os.path.exists(used_questions_file):
    with open(used_questions_file, "r") as f:
        used_questions = set(json.load(f))
else:
    used_questions = set()

# Initialiser les états de session
if 'used_questions' not in st.session_state:
    st.session_state['used_questions'] = used_questions
if 'shuffled_questions' not in st.session_state:
    st.session_state['shuffled_questions'] = []
if 'correct_count' not in st.session_state:
    st.session_state['correct_count'] = 0
if 'correct_a' not in st.session_state:
    st.session_state['correct_a'] = 0
if 'correct_c' not in st.session_state:
    st.session_state['correct_c'] = 0

# Tirer toutes les questions au démarrage de l'examen
def initialize_questions():
    available_a = category_a[~category_a['Question finale'].isin(st.session_state['used_questions'])]
    available_c = category_c[~category_c['Question finale'].isin(st.session_state['used_questions'])]

    questions_a = available_a.sample(n=min(len(available_a), 33), random_state=1).to_dict(orient='records')
    questions_c = available_c.sample(n=min(len(available_c), 87), random_state=1).to_dict(orient='records')

    st.session_state['shuffled_questions'] = random.sample(questions_a + questions_c, len(questions_a + questions_c))

if not st.session_state['shuffled_questions']:
    initialize_questions()

# Fonction pour afficher toutes les questions directement avec validation
def show_all_questions():
    answers = {}  # Dictionnaire pour stocker les réponses de l'utilisateur
    for i, question in enumerate(st.session_state['shuffled_questions']):
        st.write(f"**Question {i + 1}: {question.get('Question finale', 'Question manquante')}**")
        st.write(f"A) {question.get('Choix_A', 'Option manquante')}")
        st.write(f"B) {question.get('Choix_B', 'Option manquante')}")
        st.write(f"C) {question.get('Choix_C', 'Option manquante')}")
        answers[i] = st.radio("Votre réponse :", ["A", "B", "C"], key=f"question_{i + 1}")

    # Validation de toutes les réponses
    if st.button("Valider toutes les réponses"):
        correct_count = 0
        correct_a = 0
        correct_c = 0

        for i, question in enumerate(st.session_state['shuffled_questions']):
            is_correct = answers[i] == question.get('Reponse', '')
            if is_correct:
                correct_count += 1
                if question.get('Categorie') == 'A':
                    correct_a += 1
                elif question.get('Categorie') == 'C':
                    correct_c += 1

        st.session_state['correct_count'] = correct_count
        st.session_state['correct_a'] = correct_a
        st.session_state['correct_c'] = correct_c
        finish_exam()

# Fonction pour terminer l'examen
def finish_exam():
    st.write("### Examen terminé !")
    st.write(f"**Résultats :**")
    st.write(f"- Catégorie A : {st.session_state['correct_a']} bonnes réponses sur 33")
    st.write(f"- Catégorie C : {st.session_state['correct_c']} bonnes réponses sur 87")
    st.write(f"- **Score total** : {st.session_state['correct_count']} bonnes réponses sur {len(st.session_state['shuffled_questions'])}")

    if st.button("Faire un autre examen blanc"):
        st.session_state['used_questions'] = set()
        st.session_state['shuffled_questions'] = []
        st.session_state['correct_count'] = 0
        st.session_state['correct_a'] = 0
        st.session_state['correct_c'] = 0
        initialize_questions()

# Lancer l'examen
if st.button("Commencer l'examen"):
    show_all_questions()
