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
        st.write(f"**Question {i + 1}: {question.get('Question finale', 'Question manquante')}**")
        st.write(f"A) {question.get('Choix_A', 'Option manquante')}")
        st.write(f"B) {question.get('Choix_B', 'Option manquante')}")
        st.write(f"C) {question.get('Choix_C', 'Option manquante')}")

        answer = st.radio("Votre réponse :", ["A", "B", "C"], key=f"question_{i + 1}")

        is_correct = answer == question.get('Reponse', '')
        if is_correct:
            st.session_state['correct_count'] += 1
            if question.get('Categorie') == 'A':
                st.session_state['correct_a'] += 1
            elif question.get('Categorie') == 'C':
                st.session_state['correct_c'] += 1

        response_record = {
            "question": question.get('Question finale', 'Question manquante'),
            "choices": {
                "A": question.get('Choix_A', 'Option manquante'),
                "B": question.get('Choix_B', 'Option manquante'),
                "C": question.get('Choix_C', 'Option manquante')
            },
            "your_answer": answer,
            "correct_answer": question.get('Reponse', 'Réponse manquante'),
            "is_correct": is_correct
        }
        if question.get('Categorie') == 'A':
            st.session_state['responses_a'].append(response_record)
        elif question.get('Categorie') == 'C':
            st.session_state['responses_c'].append(response_record)

# Fonction pour afficher le récapitulatif des résultats
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

    st.write("#### Catégorie A")
    for response in st.session_state['responses_a']:
        st.write(f"**Question :** {response['question']}")
        st.write(f"- A) {response['choices']['A']}")
        st.write(f"- B) {response['choices']['B']}")
        st.write(f"- C) {response['choices']['C']}")
        st.write(f"- **Votre réponse :** {response['your_answer']} - **Réponse correcte :** {response['correct_answer']}")
        if response['is_correct']:
            st.success("Bonne réponse")
        else:
            st.error("Mauvaise réponse")
        st.write("---")

    st.write("#### Catégorie C")
    for response in st.session_state['responses_c']:
        st.write(f"**Question :** {response['question']}")
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
    st.session_state['correct_count'] = 0
    st.session_state['correct_a'] = 0
    st.session_state['correct_c'] = 0
    st.session_state['responses_a'] = []
    st.session_state['responses_c'] = []
    st.session_state['shuffled_questions'] = []
    initialize_questions()

# Lancer l'examen
if st.button("Commencer l'examen"):
    show_all_questions()

if st.button("Valider l'examen"):
    show_results()
    if st.button("Faire un autre examen blanc"):
        restart_exam()
