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
if 'correct_count' not in st.session_state:
    st.session_state['correct_count'] = 0
if 'correct_a' not in st.session_state:
    st.session_state['correct_a'] = 0
if 'correct_c' not in st.session_state:
    st.session_state['correct_c'] = 0
if 'responses_a' not in st.session_state:
    st.session_state['responses_a'] = []
if 'responses_c' not in st.session_state:
    st.session_state['responses_c'] = []
if 'shuffled_questions' not in st.session_state:
    st.session_state['shuffled_questions'] = []
if 'answers_ready' not in st.session_state:
    st.session_state['answers_ready'] = False

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
    st.write("### Questions")
    for i, question in enumerate(st.session_state['shuffled_questions']):
        st.write(f"**Question {i + 1}: {question.get('Question finale', 'Question manquante')}**")
        st.write(f"A) {question.get('Choix_A', 'Option manquante')}")
        st.write(f"B) {question.get('Choix_B', 'Option manquante')}")
        st.write(f"C) {question.get('Choix_C', 'Option manquante')}")

        st.radio("Votre réponse :", ["A", "B", "C"], key=f"question_{i + 1}")

# Fonction pour valider les réponses avant la correction
def validate_answers():
    st.write("### Validation des réponses")
    if st.button("Valider mes réponses"):
        st.session_state['answers_ready'] = True

# Fonction pour afficher les résultats et les corrections
def show_results():
    st.write("### Résultats et corrections")
    st.write(f"- Catégorie A : {st.session_state['correct_a']} bonnes réponses sur 33")
    st.write(f"- Catégorie C : {st.session_state['correct_c']} bonnes réponses sur 87")
    st.write(f"- **Score total** : {st.session_state['correct_count']} bonnes réponses sur {len(st.session_state['shuffled_questions'])}")

    st.write("**Détails des réponses :**")
    for i, question in enumerate(st.session_state['shuffled_questions']):
        user_answer = st.session_state.get(f"question_{i + 1}", "Non répondu")
        correct_answer = question.get('Reponse', 'Réponse manquante')
        st.write(f"**Question {i + 1}: {question.get('Question finale')}**")
        st.write(f"- Votre réponse : {user_answer}")
        st.write(f"- Réponse correcte : {correct_answer}")
        if user_answer == correct_answer:
            st.success("Bonne réponse")
            st.session_state['correct_count'] += 1
            if question.get('Categorie') == 'A':
                st.session_state['correct_a'] += 1
            elif question.get('Categorie') == 'C':
                st.session_state['correct_c'] += 1
        else:
            st.error("Mauvaise réponse")

# Lancer l'examen
if not st.session_state['answers_ready']:
    if st.button("Commencer l'examen"):
        show_all_questions()
        validate_answers()
else:
    show_results()
