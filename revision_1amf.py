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

# Charger le fichier CSV
file_path = "AMF.csv"  # Chemin vers le fichier CSV
try:
    data = pd.read_csv(file_path, encoding="ISO-8859-1", on_bad_lines="skip", delimiter=";")
    # Normaliser les noms des colonnes
    data.columns = data.columns.str.strip()
    # Vérifier que toutes les colonnes nécessaires sont présentes
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
if 'responses' not in st.session_state:
    st.session_state['responses'] = []
if 'shuffled_questions' not in st.session_state:
    st.session_state['shuffled_questions'] = []

# Tirer 33 questions de catégorie A et 87 de catégorie C
def initialize_questions():
    available_a = category_a[~category_a['Question finale'].isin(st.session_state['used_questions'])]
    available_c = category_c[~category_c['Question finale'].isin(st.session_state['used_questions'])]

    if len(available_a) < 33 or len(available_c) < 87:
        st.error("Pas assez de questions disponibles dans les catégories.")
        st.stop()

    questions_a = available_a.sample(n=33, random_state=1).to_dict(orient='records')
    questions_c = available_c.sample(n=87, random_state=1).to_dict(orient='records')

    st.session_state['shuffled_questions'] = random.sample(questions_a + questions_c, len(questions_a + questions_c))

if not st.session_state['shuffled_questions']:
    initialize_questions()

# Afficher les questions
for i, question in enumerate(st.session_state['shuffled_questions']):
    st.write(f"**Question {i + 1}: {question['Question finale']}**")
    st.write(f"A) {question['Choix_A']}")
    st.write(f"B) {question['Choix_B']}")
    st.write(f"C) {question['Choix_C']}")

    answer = st.radio("Votre réponse :", ["A", "B", "C"], key=f"question_{i}")
    is_correct = answer == question['Reponse']
    if is_correct:
        st.session_state['correct_count'] += 1

# Afficher les résultats après validation
if st.button("Valider l'examen"):
    st.write(f"### Résultat final : {st.session_state['correct_count']} réponses correctes sur 120 questions.")
