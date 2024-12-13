import pandas as pd
import streamlit as st
import os
import json

# Titre de l'application
st.title("Révision pour le Certificat AMF")

# Demander un nom d'utilisateur
username = st.text_input("Entrez votre nom d'utilisateur :", key="username")
if not username.strip():
    st.stop()

# Fichier spécifique à l'utilisateur
used_questions_file = f"used_questions_{username}.json"

# Charger les données
file_path = "AMF.csv"
try:
    data = pd.read_csv(file_path, encoding="ISO-8859-1", on_bad_lines="skip", delimiter=";")
except FileNotFoundError:
    st.error(f"Le fichier {file_path} est introuvable.")
    st.stop()
except Exception as e:
    st.error(f"Erreur de chargement des données : {e}")
    st.stop()

# Vérification des colonnes nécessaires
if len(data.columns) < 9:
    st.error("Les données ne contiennent pas les colonnes attendues.")
    st.stop()

# Filtrer les catégories
try:
    category_a = data[data.iloc[:, 3] == 'A']
    category_c = data[data.iloc[:, 3] == 'C']
except IndexError:
    st.error("Erreur lors de la séparation des catégories.")
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
if 'question_number' not in st.session_state:
    st.session_state['question_number'] = 1
if 'current_question' not in st.session_state:
    st.session_state['current_question'] = None
if 'current_category' not in st.session_state:
    st.session_state['current_category'] = None

# Sauvegarder les questions utilisées
def save_used_questions():
    with open(used_questions_file, "w") as f:
        json.dump(list(st.session_state['used_questions']), f)

# Sélectionner la prochaine question
def select_next_question():
    if len(st.session_state['used_questions']) >= len(data):
        st.success("Toutes les questions ont été répondues.")
        finish_exam()
        return

    available_a = category_a[~category_a.iloc[:, 0].isin(st.session_state['used_questions'])]
    available_c = category_c[~category_c.iloc[:, 0].isin(st.session_state['used_questions'])]

    if not available_a.empty:
        next_question = available_a.sample(n=1).iloc[0]
        st.session_state['current_question'] = next_question
        st.session_state['current_category'] = 'A'
    elif not available_c.empty:
        next_question = available_c.sample(n=1).iloc[0]
        st.session_state['current_question'] = next_question
        st.session_state['current_category'] = 'C'
    else:
        finish_exam()

# Poser la question
def ask_question():
    question = st.session_state['current_question']
    if question is None:
        return

    st.write(f"Question {st.session_state['question_number']}: {question.iloc[4]}")
    st.write(f"A) {question.iloc[5]}")
    st.write(f"B) {question.iloc[6]}")
    st.write(f"C) {question.iloc[7]}")
    answer = st.radio("Votre réponse :", ["A", "B", "C"], key=f"question_{st.session_state['question_number']}")

    if st.button("Valider", key=f"validate_{st.session_state['question_number']}"):
        correct_answer = question.iloc[8]
        is_correct = answer == correct_answer
        st.session_state['correct_count'] += int(is_correct)

        st.session_state['used_questions'].add(question.iloc[0])
        save_used_questions()

        st.session_state['question_number'] += 1
        st.session_state['current_question'] = None

        st.success("Bonne réponse !" if is_correct else "Mauvaise réponse.")
        select_next_question()

# Terminer l'examen
def finish_exam():
    st.write("Examen terminé !")
    st.write(f"Score total : {st.session_state['correct_count']} bonnes réponses.")
    st.button("Recommencer", on_click=reset_exam)

# Réinitialiser l'examen
def reset_exam():
    st.session_state.clear()
    if os.path.exists(used_questions_file):
        os.remove(used_questions_file)

# Lancer l'examen
if st.button("Commencer l'examen") or st.session_state['current_question'] is not None:
    if st.session_state['current_question'] is None:
        select_next_question()
    ask_question()
