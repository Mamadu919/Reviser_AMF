import pandas as pd
import streamlit as st
import os
import json

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
    category_a = data[data.iloc[:, 3] == 'A']  # Colonne d'index 3 pour la catégorie
    category_c = data[data.iloc[:, 3] == 'C']
except IndexError:
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
if 'asked_questions' not in st.session_state:
    st.session_state['asked_questions'] = []
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
if 'question_number' not in st.session_state:
    st.session_state['question_number'] = 1
if 'current_question' not in st.session_state:
    st.session_state['current_question'] = None
if 'current_category' not in st.session_state:
    st.session_state['current_category'] = None
if 'category_a_count' not in st.session_state:
    st.session_state['category_a_count'] = 33
if 'category_c_count' not in st.session_state:
    st.session_state['category_c_count'] = 87

# Fonction pour sauvegarder les questions utilisées
def save_used_questions():
    with open(used_questions_file, "w") as f:
        json.dump(list(st.session_state['used_questions']), f)

# Fonction pour sélectionner une question
def select_next_question():
    if st.session_state['category_a_count'] > 0:
        available_questions = category_a[~category_a.iloc[:, 0].isin(st.session_state['used_questions'])]
        if not available_questions.empty:
            next_question = available_questions.sample(n=1, random_state=1).iloc[0]
            st.session_state['current_question'] = next_question
            st.session_state['current_category'] = 'A'
            st.session_state['category_a_count'] -= 1
            return

    if st.session_state['category_c_count'] > 0:
        available_questions = category_c[~category_c.iloc[:, 0].isin(st.session_state['used_questions'])]
        if not available_questions.empty:
            next_question = available_questions.sample(n=1, random_state=1).iloc[0]
            st.session_state['current_question'] = next_question
            st.session_state['current_category'] = 'C'
            st.session_state['category_c_count'] -= 1
            return

    finish_exam()

# Fonction pour poser une question
def ask_question():
    question = st.session_state['current_question']
    category = st.session_state['current_category']

    st.write(f"Question {st.session_state['question_number']}: {question.iloc[4]}")
    st.write(f"A) {question.iloc[5]}")
    st.write(f"B) {question.iloc[6]}")
    st.write(f"C) {question.iloc[7]}")
    answer = st.radio("Votre réponse :", ["A", "B", "C"], key=f"question_{question.iloc[0]}")

    if st.button("Valider", key=f"validate_{st.session_state['question_number']}"):
        is_correct = answer == question.iloc[8]
        if is_correct:
            st.session_state['correct_count'] += 1
            if category == 'A':
                st.session_state['correct_a'] += 1
            elif category == 'C':
                st.session_state['correct_c'] += 1

        st.session_state['asked_questions'].append(question.iloc[0])
        st.session_state['used_questions'].add(question.iloc[0])
        save_used_questions()

        response_record = {
            "question": question.iloc[4],
            "choices": {
                "A": question.iloc[5],
                "B": question.iloc[6],
                "C": question.iloc[7]
            },
            "your_answer": answer,
            "correct_answer": question.iloc[8],
            "is_correct": is_correct
        }
        if category == 'A':
            st.session_state['responses_a'].append(response_record)
        elif category == 'C':
            st.session_state['responses_c'].append(response_record)

        st.session_state['question_number'] += 1
        select_next_question()

# Fonction pour terminer l'examen
def finish_exam():
    st.write("Examen terminé !")
    st.write(f"Résultats :")
    st.write(f"- Catégorie A : {st.session_state['correct_a']} bonnes réponses sur 33")
    st.write(f"- Catégorie C : {st.session_state['correct_c']} bonnes réponses sur 87")
    st.write(f"Score total : {st.session_state['correct_count']} bonnes réponses sur 120")

    st.write("**Détails des réponses**")

    st.write("**Catégorie A**")
    for response in st.session_state['responses_a']:
        st.write(f"Question: {response['question']}")
        st.write(f"A) {response['choices']['A']}")
        st.write(f"B) {response['choices']['B']}")
        st.write(f"C) {response['choices']['C']}")
        st.write(f"Votre réponse: {response['your_answer']} - Réponse correcte: {response['correct_answer']}")
        if response['is_correct']:
            st.success("Bonne réponse")
        else:
            st.error("Mauvaise réponse")
        st.write("---")

    st.write("**Catégorie C**")
    for response in st.session_state['responses_c']:
        st.write(f"Question: {response['question']}")
        st.write(f"A) {response['choices']['A']}")
        st.write(f"B) {response['choices']['B']}")
        st.write(f"C) {response['choices']['C']}")
        st.write(f"Votre réponse: {response['your_answer']} - Réponse correcte: {response['correct_answer']}")
        if response['is_correct']:
            st.success("Bonne réponse")
        else:
            st.error("Mauvaise réponse")
        st.write("---")

    if st.button("Faire un autre examen blanc"):
        st.session_state['asked_questions'] = []
        st.session_state['correct_count'] = 0
        st.session_state['correct_a'] = 0
        st.session_state['correct_c'] = 0
        st.session_state['responses_a'] = []
        st.session_state['responses_c'] = []
        st.session_state['question_number'] = 1
        st.session_state['category_a_count'] = 33
        st.session_state['category_c_count'] = 87
        st.session_state['current_question'] = None
        st.session_state['used_questions'] = set()
        save_used_questions()

# Lancer l'examen
if st.session_state.get('current_question') is None:
    select_next_question()

if st.session_state['current_question'] is not None:
    ask_question()

if st.button("Terminer l'examen"):
    finish_exam()
