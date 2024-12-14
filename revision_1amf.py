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
except FileNotFoundError:
    st.error("Le fichier CSV est introuvable.")
    st.stop()

# Vérifier que les colonnes nécessaires sont présentes
try:
    category_a = data[data.iloc[:, 3] == 'A']  # Colonne 3 : Catégorie
    category_c = data[data.iloc[:, 3] == 'C']  # Colonne 3 : Catégorie
except IndexError:
    st.error("Les colonnes attendues sont absentes ou mal formatées.")
    st.stop()

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
if 'correct_count' not in st.session_state:
    st.session_state['correct_count'] = 0
if 'responses' not in st.session_state:
    st.session_state['responses'] = []
if 'shuffled_questions' not in st.session_state:
    st.session_state['shuffled_questions'] = []

# Tirer 33 questions de catégorie A et 87 de catégorie C
def initialize_questions():
    available_a = category_a[~category_a.iloc[:, 0].isin(st.session_state['used_questions'])]
    available_c = category_c[~category_c.iloc[:, 0].isin(st.session_state['used_questions'])]

    if len(available_a) < 33 or len(available_c) < 87:
        st.error("Pas assez de questions disponibles dans les catégories.")
        st.stop()

    questions_a = available_a.sample(n=33, random_state=1)
    questions_c = available_c.sample(n=87, random_state=1)

    st.session_state['shuffled_questions'] = pd.concat([questions_a, questions_c]).sample(frac=1, random_state=1)

if not st.session_state['shuffled_questions']:
    initialize_questions()

# Afficher les questions
for index, question in st.session_state['shuffled_questions'].iterrows():
    st.write(f"Question {index + 1}: {question.iloc[4]}")  # Colonne 4 : Question
    st.write(f"A) {question.iloc[5]}")  # Colonne 5 : Choix A
    st.write(f"B) {question.iloc[6]}")  # Colonne 6 : Choix B
    st.write(f"C) {question.iloc[7]}")  # Colonne 7 : Choix C

    answer = st.radio("Votre réponse :", ["A", "B", "C"], key=f"question_{index}")
    if answer == question.iloc[8]:  # Colonne 8 : Bonne réponse
        st.session_state['correct_count'] += 1
