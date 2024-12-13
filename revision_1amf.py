import pandas as pd
import streamlit as st

# Titre de l'application
st.title("Révision pour le Certificat AMF")

# Charger les données directement depuis un fichier inclus dans le projet
file_path = "AMF.xlsx"  # Le fichier doit être à côté de ce script
try:
    data = pd.read_excel(file_path, engine="openpyxl")
except FileNotFoundError:
    st.error(f"Le fichier {file_path} est introuvable. Assurez-vous qu'il est dans le même dossier que ce script.")
    st.stop()
except Exception as e:
    st.error(f"Une erreur est survenue lors du chargement du fichier : {e}")
    st.stop()

# Filtrer les questions par catégorie en utilisant l'index de colonne pour 'Categorie'
category_a = data[data.iloc[:, 3] == 'A']  # Colonne d'index 3 pour la catégorie
category_c = data[data.iloc[:, 3] == 'C']

# Liste pour garder en mémoire les questions posées et le score
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

# Marquer les questions déjà utilisées comme mémorisées
if 'used_questions' not in st.session_state:
    st.session_state['used_questions'] = set()

# Fonction pour sélectionner des questions aléatoires
def select_questions(category, num_questions):
    available_questions = category[~category.iloc[:, 0].isin(st.session_state['used_questions'])]  # Colonne d'index 0 pour 'ID question'
    if len(available_questions) < num_questions:
        st.warning("Pas assez de questions disponibles.")
        return available_questions.sample(n=len(available_questions), random_state=1)
    return available_questions.sample(n=num_questions, random_state=1)

# Poser une seule question à la fois
def ask_question():
    question = st.session_state['current_question']
    category = st.session_state['current_category']

    st.write(f"Question {st.session_state['question_number']}: {question.iloc[4]}")  # Colonne d'index 4 pour 'Question'
    st.write(f"A) {question.iloc[5]}")
    st.write(f"B) {question.iloc[6]}")
    st.write(f"C) {question.iloc[7]}")
    answer = st.radio("Votre réponse :", ["A", "B", "C"], key=f"question_{question.iloc[0]}")

    if st.button("Valider", key=f"validate_{question.iloc[0]}"):
        is_correct = answer == question.iloc[8]  # Colonne d'index 8 pour 'Bonne réponse'
        if is_correct:
            st.session_state['correct_count'] += 1
            if category == 'A':
                st.session_state['correct_a'] += 1
            elif category == 'C':
                st.session_state['correct_c'] += 1
        st.session_state['asked_questions'].append(question.iloc[0])  # Colonne d'index 0 pour 'ID question'
        st.session_state['used_questions'].add(question.iloc[0])
        response_record = {
            "question": question.iloc[4],
            "your_answer": answer,
            "correct_answer": question.iloc[8],
            "is_correct": is_correct
        }
        if category == 'A':
            st.session_state['responses_a'].append(response_record)
        elif category == 'C':
            st.session_state['responses_c'].append(response_record)
        st.session_state['question_number'] += 1
        st.session_state['current_question'] = None

# Terminer l'examen
def finish_exam():
    total_questions_a = 33
    total_questions_c = 87
    total_questions = total_questions_a + total_questions_c

    answered_a = len(st.session_state['responses_a'])
    answered_c = len(st.session_state['responses_c'])

    score_a = (st.session_state['correct_a'] / total_questions_a) * 100
    score_c = (st.session_state['correct_c'] / total_questions_c) * 100
    score_total = (st.session_state['correct_count'] / total_questions) * 100

    st.write(f"Examen terminé !")
    st.write(f"Résultats par catégorie :")
    st.write(f"- Catégorie A : {st.session_state['correct_a']} bonnes réponses sur {total_questions_a} ({score_a:.2f}%)")
    st.write(f"- Catégorie C : {st.session_state['correct_c']} bonnes réponses sur {total_questions_c} ({score_c:.2f}%)")
    st.write(f"Score total : {st.session_state['correct_count']} bonnes réponses sur {total_questions} ({score_total:.2f}%)")

    if score_a >= 80 and score_c >= 80:
        st.success("Félicitations, vous avez réussi !")
    else:
        st.error("Vous n'avez pas réussi.")

    st.write(f"- Vous avez répondu à {answered_a} questions sur 33 en catégorie A.")
    st.write(f"- Vous avez répondu à {answered_c} questions sur 87 en catégorie C.")

    st.write("\n**Détails de toutes les réponses**")
    st.write("\n**Catégorie A**")
    for response in st.session_state['responses_a']:
        st.write(f"Question: {response['question']}")
        st.write(f"Votre réponse: {response['your_answer']} - Réponse correcte: {response['correct_answer']}")
        if response['is_correct']:
            st.success("Bonne réponse")
        else:
            st.error("Mauvaise réponse")
        st.write("---")

    st.write("\n**Catégorie C**")
    for response in st.session_state['responses_c']:
        st.write(f"Question: {response['question']}")
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
        st.session_state['used_questions'] = set()  # Réinitialiser pour tirer une nouvelle série
        st.session_state['revision_started'] = False
        st.session_state['current_question'] = None

# Démarrer ou continuer la révision
if st.button("Commencer la révision") or st.session_state.get('revision_started', False):
    st.session_state['revision_started'] = True

    if st.session_state['current_question'] is None:
        remaining_a = select_questions(category_a, 1)
        remaining_c = select_questions(category_c, 1)

        if not remaining_a.empty:
            st.session_state['current_question'] = remaining_a.iloc[0]
            st.session_state['current_category'] = 'A'
        elif not remaining_c.empty:
            st.session_state['current_question'] = remaining_c.iloc[0]
            st.session_state['current_category'] = 'C'
        else:
            finish_exam()

    if st.session_state['current_question'] is not None:
        ask_question()

    if st.button("Terminer l'examen"):
        finish_exam()
