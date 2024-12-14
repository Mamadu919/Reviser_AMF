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
if 'responses' not in st.session_state:
    st.session_state['responses'] = []

# Fonction pour sauvegarder les questions utilisées
def save_used_questions():
    with open(used_questions_file, "w") as f:
        json.dump(list(st.session_state['used_questions']), f)

# Fonction pour sélectionner 120 questions
def select_questions():
    available_questions = pd.concat([
        category_a[~category_a.iloc[:, 0].isin(st.session_state['used_questions'])],
        category_c[~category_c.iloc[:, 0].isin(st.session_state['used_questions'])]
    ])
    
    if len(available_questions) < 120:
        st.error("Pas assez de questions disponibles.")
        st.stop()
    
    selected_questions = available_questions.sample(n=120, random_state=1)
    st.session_state['asked_questions'] = selected_questions
    st.session_state['used_questions'].update(selected_questions.iloc[:, 0].tolist())
    save_used_questions()

# Appel de la fonction pour sélectionner les questions
select_questions()

# Afficher les questions
for index, question in st.session_state['asked_questions'].iterrows():
    st.write(f"Question {index + 1}: {question.iloc[4]}")  # Affiche la question