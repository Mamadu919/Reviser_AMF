import pandas as pd
import streamlit as st

# Titre de l'application
st.title("Révision pour le Certificat AMF")

# Charger les données via un téléversement
uploaded_file = st.file_uploader("Choisissez un fichier Excel", type="xlsx")

# Si un fichier est téléversé, chargez-le
if uploaded_file is not None:
    data = pd.read_excel(uploaded_file)
    
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
    def ask_question(question, category):
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

    # Démarrer ou continuer la révision
    if st.button("Commencer la révision") or st.session_state.get('revision_started', False):
        st.session_state['revision_started'] = True

        # Sélectionner une question de catégorie A ou C selon les questions restantes
        remaining_a = select_questions(category_a, 33 - len([q for q in st.session_state['asked_questions'] if q in category_a.iloc[:, 0].values]))
        remaining_c = select_questions(category_c, 87 - len([q for q in st.session_state['asked_questions'] if q in category_c.iloc[:, 0].values]))

        if not remaining_a.empty:
            ask_question(remaining_a.iloc[0], 'A')
        elif not remaining_c.empty:
            ask_question(remaining_c.iloc[0], 'C')
        else:
            # Fin de la révision
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
                st.session_state['revision_started'] = False
else:
    st.warning("Veuillez téléverser un fichier Excel pour commencer.")
