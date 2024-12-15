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

# Initialiser les états de session
if 'exam_started' not in st.session_state:
    st.session_state['exam_started'] = False
if 'exam_finished' not in st.session_state:
    st.session_state['exam_finished'] = False
if 'used_questions' not in st.session_state:
    st.session_state['used_questions'] = set()
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

# Charger les questions utilisées précédemment
if os.path.exists(used_questions_file):
    with open(used_questions_file, "r") as f:
        st.session_state['used_questions'] = set(json.load(f))

# Fonction pour sauvegarder les questions utilisées
def save_used_questions():
    with open(used_questions_file, "w") as f:
        json.dump(list(st.session_state['used_questions']), f)

# Fonction pour initialiser les questions
def initialize_questions():
    available_a = category_a[~category_a['Question finale'].isin(st.session_state['used_questions'])]
    available_c = category_c[~category_c['Question finale'].isin(st.session_state['used_questions'])]

    if len(available_a) < 33 or len(available_c) < 87:
        st.error("Pas assez de questions disponibles dans les catégories.")
        st.stop()

    questions_a = available_a.sample(n=33, random_state=1).to_dict(orient='records')
    questions_c = available_c.sample(n=87, random_state=1).to_dict(orient='records')

    st.session_state['shuffled_questions'] = random.sample(questions_a + questions_c, len(questions_a + questions_c))
    st.session_state['exam_started'] = True
    st.session_state['exam_finished'] = False

# Fonction pour afficher toutes les questions directement
def show_all_questions():
    for i, question in enumerate(st.session_state['shuffled_questions']):
        st.write(f"**Question {i + 1}: {question.get('Question finale', 'Question manquante')}**")
        st.write(f"A) {question.get('Choix_A', 'Option manquante')}")
        st.write(f"B) {question.get('Choix_B', 'Option manquante')}")
        st.write(f"C) {question.get('Choix_C', 'Option manquante')}")

        st.radio("Votre réponse :", ["A", "B", "C"], key=f"question_{i + 1}")

# Fonction pour valider les réponses
def validate_exam():
    st.session_state['correct_a'] = 0
    st.session_state['correct_c'] = 0
    st.session_state['responses'] = []

    for i, question in enumerate(st.session_state['shuffled_questions']):
        answer = st.session_state.get(f"question_{i + 1}", None)
        response_record = {
            "question": question.get('Question finale', 'Question manquante'),
            "choices": {
                "A": question.get('Choix_A', 'Option manquante'),
                "B": question.get('Choix_B', 'Option manquante'),
                "C": question.get('Choix_C', 'Option manquante')
            },
            "your_answer": answer,
            "correct_answer": question.get('Reponse', 'Réponse manquante'),
            "is_correct": answer == question.get('Reponse', '')
        }
        st.session_state['responses'].append(response_record)

        if question.get('Categorie') == 'A' and response_record["is_correct"]:
            st.session_state['correct_a'] += 1
        elif question.get('Categorie') == 'C' and response_record["is_correct"]:
            st.session_state['correct_c'] += 1

    st.session_state['correct_count'] = st.session_state['correct_a'] + st.session_state['correct_c']
    st.session_state['exam_finished'] = True
    save_used_questions()

# Fonction pour afficher les résultats
def show_results():
    st.write("### Résultats de l'examen")
    st.write(f"- **Catégorie A :** {st.session_state['correct_a']} bonnes réponses sur 33.")
    st.write(f"- **Catégorie C :** {st.session_state['correct_c']} bonnes réponses sur 87.")
    st.write(f"- **Score total :** {st.session_state['correct_count']} bonnes réponses sur 120.")

    pourcentage_a = (st.session_state['correct_a'] / 33) * 100
    pourcentage_c = (st.session_state['correct_c'] / 87) * 100
    st.write(f"- **Pourcentage Catégorie A :** {pourcentage_a:.2f}%")
    st.write(f"- **Pourcentage Catégorie C :** {pourcentage_c:.2f}%")

    if pourcentage_a >= 80 and pourcentage_c >= 80:
        st.success("Félicitations ! Vous avez réussi l'examen.")
    else:
        st.error("Désolé, vous n'avez pas réussi. Vous devez atteindre au moins 80% dans chaque catégorie.")

    st.write("### Détails des réponses")
    for i, response in enumerate(st.session_state['responses']):
        st.write(f"**Question {i + 1} :** {response['question']}")
        st.write(f"- A) {response['choices']['A']}")
        st.write(f"- B) {response['choices']['B']}")
        st.write(f"- C) {response['choices']['C']}")
        st.write(f"- **Votre réponse :** {response['your_answer']} - **Réponse correcte :** {response['correct_answer']}")
        if response['is_correct']:
            st.success("Bonne réponse")
        else:
            st.error("Mauvaise réponse")
        st.write("---")

# Fonction pour recommencer un examen
def restart_exam():
    st.session_state['exam_started'] = False
    st.session_state['exam_finished'] = False
    st.session_state['shuffled_questions'] = []

# Workflow de l'application
if not st.session_state['exam_started']:
    if st.button("Commencer l'examen"):
        initialize_questions()

if st.session_state['exam_started'] and not st.session_state['exam_finished']:
    show_all_questions()
    if st.button("Valider l'examen"):
        validate_exam()

if st.session_state['exam_finished']:
    show_results()
    if st.button("Faire un autre examen blanc"):
        restart_exam()
