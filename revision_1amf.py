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

# Charger le fichier CSV
file_path = "AMF.csv"  # Chemin vers le fichier CSV
try:
    data = pd.read_csv(file_path, encoding="ISO-8859-1", on_bad_lines="skip", delimiter=";")
    # Vérifier que toutes les colonnes nécessaires sont présentes
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
used_questions_file = f"used_questions_{username}.json"
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
if 'responses' not in st.session_state:
    st.session_state['responses'] = []
if 'correct_count' not in st.session_state:
    st.session_state['correct_count'] = 0

# Tirer 33 questions de catégorie A et 87 de catégorie C
def initialize_questions():
    available_a = category_a[~category_a['Question finale'].isin(st.session_state['used_questions'])]
    available_c = category_c[~category_c['Question finale'].isin(st.session_state['used_questions'])]

    if len(available_a) < 33 or len(available_c) < 87:
        st.error("Pas assez de questions disponibles dans les catégories.")
        st.stop()

    questions_a = available_a.sample(n=33, random_state=1)
    questions_c = available_c.sample(n=87, random_state=1)

    st.session_state['shuffled_questions'] = pd.concat([questions_a, questions_c]).sample(frac=1, random_state=1)

if not st.session_state['shuffled_questions']:
    initialize_questions()

# Afficher les questions
st.write("### Répondez aux questions suivantes :")
for idx, question in st.session_state['shuffled_questions'].iterrows():
    st.write(f"**Question {idx + 1}: {question['Question finale']}**")
    st.write(f"A) {question['Choix_A']}")
    st.write(f"B) {question['Choix_B']}")
    st.write(f"C) {question['Choix_C']}")
    st.radio("Votre réponse :", ["A", "B", "C"], key=f"question_{idx}")

# Bouton pour valider les réponses
if st.button("Valider"):
    st.session_state['correct_count'] = 0
    st.session_state['responses'] = []

    # Vérifier chaque réponse et calculer les résultats
    for idx, question in st.session_state['shuffled_questions'].iterrows():
        user_answer = st.session_state.get(f"question_{idx}", None)
        correct_answer = question['Reponse']

        is_correct = user_answer == correct_answer
        if is_correct:
            st.session_state['correct_count'] += 1

        st.session_state['responses'].append({
            "question": question['Question finale'],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })

    # Afficher les résultats
    st.write("### Résultats")
    st.write(f"Score total : {st.session_state['correct_count']} / {len(st.session_state['shuffled_questions'])}")
    for response in st.session_state['responses']:
        st.write(f"**Question :** {response['question']}")
        st.write(f"Votre réponse : {response['user_answer']} | Réponse correcte : {response['correct_answer']}")
        if response['is_correct']:
            st.success("Bonne réponse")
        else:
            st.error("Mauvaise réponse")
