# pages/2_Interactive_Quizzes.py - Enhanced quiz functionality

import streamlit as st
import re
import random
import time
import pandas as pd
from datetime import datetime

# Import utility functions
from utils.text_utils import generate_quiz
from utils.storage import save_session

# Page configuration
st.set_page_config(
    page_title="Interactive Quizzes - Personal Audio Tutor",
    page_icon="🧩",
    layout="wide"
)

# Apply theme based on dark_mode setting if available
if 'dark_mode' in st.session_state and st.session_state.dark_mode:
    st.markdown("""
    <style>
        .main {background-color: #1E1E1E; color: #FFFFFF;}
        .stTextInput > div > div > input {background-color: #2E2E2E; color: #FFFFFF;}
        .stSelectbox > div > div > select {background-color: #2E2E2E; color: #FFFFFF;}
    </style>
    """, unsafe_allow_html=True)

# Apply font size if available
if 'font_size' in st.session_state:
    font_size_map = {
        "small": "0.9rem",
        "medium": "1rem",
        "large": "1.2rem",
        "x-large": "1.5rem"
    }
    st.markdown(f"""
    <style>
        .main p, .main li {{
            font-size: {font_size_map[st.session_state.font_size]};
        }}
    </style>
    """, unsafe_allow_html=True)


# Helper function to parse quiz questions
def parse_quiz(quiz_text):
    """Parse quiz text into a structured format"""
    questions = []

    # Pattern to find questions, options and answers
    pattern = r'Q(\d+):\s*(.*?)\s*(?:(?:A|a)\.)\s*(.*?)\s*(?:(?:B|b)\.)\s*(.*?)\s*(?:(?:C|c)\.)\s*(.*?)\s*(?:(?:D|d)\.)\s*(.*?)\s*(?:Correct Answer:|Correct:|Answer:)\s*([A-Da-d])'

    matches = re.findall(pattern, quiz_text, re.DOTALL)

    for match in matches:
        q_num, question, option_a, option_b, option_c, option_d, correct = match

        questions.append({
            'question_number': int(q_num),
            'question': question.strip(),
            'options': {
                'A': option_a.strip(),
                'B': option_b.strip(),
                'C': option_c.strip(),
                'D': option_d.strip()
            },
            'correct_answer': correct.strip().upper()
        })

    return questions


# Main function
def main():
    st.title("🧩 Interactive Quizzes")
    st.write("Test your knowledge with AI-generated quizzes on any topic")

    # Check if API is configured
    if 'api_configured' not in st.session_state or not st.session_state.api_configured:
        st.warning("Please configure your API key on the main page before using this feature.")
        st.stop()

    # Initialize quiz state variables
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_results' not in st.session_state:
        st.session_state.quiz_results = []
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'quiz_finished' not in st.session_state:
        st.session_state.quiz_finished = False

    # Two modes: create a new quiz or use content from the main app
    st.subheader("Quiz Generation")

    quiz_tab1, quiz_tab2 = st.tabs(["Create New Quiz", "Quiz from Current Topic"])

    with quiz_tab1:
        col1, col2 = st.columns([3, 1])

        with col1:
            new_topic = st.text_input("Enter a topic for your quiz:")

        with col2:
            num_questions = st.number_input("Number of Questions:", min_value=3, max_value=10, value=5)
            difficulty = st.selectbox("Difficulty:", ["easy", "medium", "hard"], index=1)

        if st.button("Generate Quiz") and new_topic:
            with st.spinner(f"Creating quiz about {new_topic}..."):
                # In a real implementation, you'd get an explanation first
                # For simplicity, we'll generate quiz directly
                explanation = f"Creating a quiz about {new_topic} at {difficulty} difficulty level."

                quiz_text = generate_quiz(new_topic, explanation, num_questions)
                st.session_state.quiz_questions = parse_quiz(quiz_text)
                st.session_state.current_question = 0
                st.session_state.user_answers = {}
                st.session_state.quiz_started = True
                st.session_state.quiz_finished = False
                st.session_state.current_quiz_topic = new_topic

                # Reset timer
                st.session_state.quiz_start_time = time.time()

                st.experimental_rerun()

    with quiz_tab2:
        # Check if there's a current topic
        if 'current_topic' in st.session_state and st.session_state.current_topic and 'explanation' in st.session_state:
            st.write(f"Current topic: **{st.session_state.current_topic}**")

            num_questions = st.number_input("Number of Questions:", min_value=3, max_value=10, value=5,
                                            key="current_topic_questions")

            if st.button("Create Quiz from Current Topic"):
                with st.spinner("Creating quiz from your current topic..."):
                    quiz_text = generate_quiz(st.session_state.current_topic, st.session_state.explanation,
                                              num_questions)
                    st.session_state.quiz_questions = parse_quiz(quiz_text)
                    st.session_state.current_question = 0
                    st.session_state.user_answers = {}
                    st.session_state.quiz_started = True
                    st.session_state.quiz_finished = False
                    st.session_state.current_quiz_topic = st.session_state.current_topic

                    # Reset timer
                    st.session_state.quiz_start_time = time.time()

                    st.experimental_rerun()
        else:
            st.info("No current topic loaded. Please generate content on the main page first or create a new quiz.")

    # Display quiz if started
    if st.session_state.quiz_started and not st.session_state.quiz_finished:
        st.markdown("---")
        st.subheader(f"Quiz: {st.session_state.current_quiz_topic}")

        # Show progress
        progress = st.progress((st.session_state.current_question) / len(st.session_state.quiz_questions))
        st.write(f"Question {st.session_state.current_question + 1} of {len(st.session_state.quiz_questions)}")

        # Display current question
        current_q = st.session_state.quiz_questions[st.session_state.current_question]

        st.markdown(f"### {current_q['question']}")

        # Display options
        option_cols = st.columns(2)

        # Determine if the user has already answered this question
        prev_answer = st.session_state.user_answers.get(st.session_state.current_question, None)

        with option_cols[0]:
            option_a_selected = st.button(
                f"A. {current_q['options']['A']}",
                key="option_a",
                disabled=(prev_answer is not None),
                use_container_width=True,
                type="primary" if prev_answer == "A" else "secondary"
            )

            option_c_selected = st.button(
                f"C. {current_q['options']['C']}",
                key="option_c",
                disabled=(prev_answer is not None),
                use_container_width=True,
                type="primary" if prev_answer == "C" else "secondary"
            )

        with option_cols[1]:
            option_b_selected = st.button(
                f"B. {current_q['options']['B']}",
                key="option_b",
                disabled=(prev_answer is not None),
                use_container_width=True,
                type="primary" if prev_answer == "B" else "secondary"
            )

            option_d_selected = st.button(
                f"D. {current_q['options']['D']}",
                key="option_d",
                disabled=(prev_answer is not None),
                use_container_width=True,
                type="primary" if prev_answer == "D" else "secondary"
            )

        # Handle answer selection
        if option_a_selected:
            st.session_state.user_answers[st.session_state.current_question] = "A"
        elif option_b_selected:
            st.session_state.user_answers[st.session_state.current_question] = "B"
        elif option_c_selected:
            st.session_state.user_answers[st.session_state.current_question] = "C"
        elif option_d_selected:
            st.session_state.user_answers[st.session_state.current_question] = "D"

        # Show feedback if the user has answered
        if st.session_state.current_question in st.session_state.user_answers:
            user_answer = st.session_state.user_answers[st.session_state.current_question]
            correct_answer = current_q['correct_answer']

            if user_answer == correct_answer:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. The correct answer is {correct_answer}.")

            # Navigation buttons
            nav_col1, nav_col2 = st.columns(2)

            with nav_col1:
                # Previous button
                if st.session_state.current_question > 0:
                    if st.button("⬅️ Previous Question"):
                        st.session_state.current_question -= 1
                        st.experimental_rerun()

            with nav_col2:
                # Next button or Finish
                if st.session_state.current_question < len(st.session_state.quiz_questions) - 1:
                    if st.button("Next Question ➡️"):
                        st.session_state.current_question += 1
                        st.experimental_rerun()
                else:
                    if st.button("Finish Quiz"):
                        # Calculate results
                        correct_count = 0
                        for q_idx, answer in st.session_state.user_answers.items():
                            if answer == st.session_state.quiz_questions[q_idx]['correct_answer']:
                                correct_count += 1

                        score = (correct_count / len(st.session_state.quiz_questions)) * 100

                        # Calculate time taken
                        time_taken = time.time() - st.session_state.quiz_start_time

                        # Store results
                        st.session_state.quiz_results = {
                            'topic': st.session_state.current_quiz_topic,
                            'score': score,
                            'correct': correct_count,
                            'total': len(st.session_state.quiz_questions),
                            'time_taken': time_taken,
                            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'questions': st.session_state.quiz_questions,
                            'user_answers': st.session_state.user_answers
                        }

                        st.session_state.quiz_finished = True

                        # Save results to history
                        if 'quiz_history' not in st.session_state:
                            st.session_state.quiz_history = []

                        st.session_state.quiz_history.append({
                            'topic': st.session_state.current_quiz_topic,
                            'score': score,
                            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        })

                        st.experimental_rerun()

    # Display results if finished
    elif st.session_state.quiz_finished:
        st.markdown("---")
        st.subheader("Quiz Results")

        results = st.session_state.quiz_results

        # Display score
        score_color = "green" if results['score'] >= 70 else "orange" if results['score'] >= 50 else "red"

        st.markdown(f"""
        <div style='padding: 20px; border-radius: 10px; background-color: #f8f9fa; text-align: center;'>
            <h1 style='color: {score_color};'>{results['score']:.1f}%</h1>
            <p>You answered {results['correct']} out of {results['total']} questions correctly</p>
            <p>Time taken: {results['time_taken']:.1f} seconds</p>
        </div>
        """, unsafe_allow_html=True)

        # Review answers
        st.markdown("### Review Your Answers")

        for i, question in enumerate(results['questions']):
            user_answer = results['user_answers'].get(i, "Not answered")
            correct_answer = question['correct_answer']

            with st.expander(f"Question {i + 1}: {question['question']}"):
                st.markdown("**Options:**")
                for opt, text in question['options'].items():
                    prefix = ""
                    if opt == user_answer and opt == correct_answer:
                        prefix = "✅ "
                    elif opt == user_answer and opt != correct_answer:
                        prefix = "❌ "
                    elif opt == correct_answer:
                        prefix = "✓ "

                    st.markdown(f"{prefix}**{opt}.** {text}")

                st.markdown(f"**Your answer:** {user_answer}")
                st.markdown(f"**Correct answer:** {correct_answer}")

        # Option to retry or create new quiz
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Retry Quiz"):
                # Reset quiz but keep the questions
                st.session_state.current_question = 0
                st.session_state.user_answers = {}
                st.session_state.quiz_started = True
                st.session_state.quiz_finished = False
                st.session_state.quiz_start_time = time.time()
                st.experimental_rerun()

        with col2:
            if st.button("New Quiz"):
                # Reset everything
                st.session_state.quiz_questions = []
                st.session_state.current_question = 0
                st.session_state.user_answers = {}
                st.session_state.quiz_started = False
                st.session_state.quiz_finished = False
                st.experimental_rerun()

    # Display quiz history
    if not st.session_state.quiz_started and 'quiz_history' in st.session_state and st.session_state.quiz_history:
        st.markdown("---")
        st.subheader("Your Quiz History")

        # Convert to DataFrame for display
        history_df = pd.DataFrame(st.session_state.quiz_history)

        # Format score as percentage
        history_df['score'] = history_df['score'].apply(lambda x: f"{x:.1f}%")

        # Rename columns
        history_df.columns = ['Topic', 'Score', 'Date']

        # Display
        st.dataframe(history_df)

        # Add option to clear history
        if st.button("Clear Quiz History"):
            st.session_state.quiz_history = []
            st.experimental_rerun()


# Run the app
if __name__ == "__main__":
    main()