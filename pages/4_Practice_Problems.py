import streamlit as st
import os
import sys
import json
import pandas as pd
from datetime import datetime

# Add the parent directory to sys.path to import utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.api_connector import generate_practice_problems, check_solution
from utils.storage import save_practice_session, get_practice_history
from utils.text_utils import format_problems

st.set_page_config(page_title="Practice Problems", page_icon="✏️", layout="wide")


def display_problem(problem, index):
    """Display a single practice problem with answer box"""
    st.markdown(f"### Problem {index + 1}")
    st.markdown(problem["question"])

    if "image" in problem and problem["image"]:
        st.image(problem["image"])

    if problem["type"] == "multiple_choice" and "options" in problem:
        answer = st.radio("Choose the correct answer:",
                          problem["options"],
                          key=f"problem_{index}")
    else:
        answer = st.text_area("Your answer:", key=f"problem_{index}")

    check_button = st.button("Check Answer", key=f"check_{index}")

    if check_button:
        is_correct, feedback = check_solution(problem, answer)
        if is_correct:
            st.success("Correct! " + feedback)
        else:
            st.error("Not quite right. " + feedback)

    return {"problem": problem, "user_answer": answer}


def main():
    st.title("✏️ Practice Problems")
    st.markdown("""
    Reinforce your learning with custom practice problems tailored to your studies.
    Practice makes perfect!
    """)

    tab1, tab2 = st.tabs(["Generate Problems", "Practice History"])

    with tab1:
        st.subheader("Generate Custom Practice Problems")

        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("Learning Topic:")
            difficulty = st.select_slider("Difficulty Level:",
                                          options=["Beginner", "Intermediate", "Advanced"],
                                          value="Intermediate")
        with col2:
            problem_type = st.selectbox("Problem Type:",
                                        ["Mixed", "Multiple Choice", "Short Answer", "Calculation", "Essay"])
            num_problems = st.slider("Number of Problems:", 1, 10, 5)

        advanced_options = st.expander("Advanced Options")
        with advanced_options:
            include_hints = st.checkbox("Include Hints", value=True)
            include_solutions = st.checkbox("Include Detailed Solutions", value=True)
            time_limit = st.number_input("Time Limit (minutes, 0 for no limit):",
                                         min_value=0, max_value=120, value=0)

        if st.button("Generate Practice Problems"):
            if not topic:
                st.warning("Please enter a learning topic.")
            else:
                with st.spinner(f"Generating {num_problems} practice problems for {topic}..."):
                    generated_problems = generate_practice_problems(
                        topic,
                        difficulty,
                        problem_type,
                        num_problems,
                        include_hints,
                        include_solutions
                    )

                    if generated_problems:
                        st.session_state.problems = generated_problems
                        st.session_state.show_problems = True
                        if time_limit > 0:
                            st.session_state.time_limit = time_limit * 60  # Convert to seconds
                        else:
                            st.session_state.time_limit = None
                        st.success(f"Generated {len(generated_problems)} practice problems!")
                    else:
                        st.error("Failed to generate practice problems. Please try again.")

        if 'show_problems' in st.session_state and st.session_state.show_problems:
            st.markdown("---")
            st.subheader("Practice Problems")

            if 'time_limit' in st.session_state and st.session_state.time_limit:
                time_limit_mins = st.session_state.time_limit // 60
                st.info(f"Time Limit: {time_limit_mins} minutes")
                # Time tracking would be implemented here

            responses = []
            for i, problem in enumerate(st.session_state.problems):
                response = display_problem(problem, i)
                responses.append(response)

            if st.button("Submit All Answers"):
                correct_count = 0

                # Create results summary
                results = []
                for i, resp in enumerate(responses):
                    is_correct, feedback = check_solution(resp["problem"], resp["user_answer"])
                    if is_correct:
                        correct_count += 1

                    results.append({
                        "problem_number": i + 1,
                        "correct": is_correct,
                        "feedback": feedback,
                        "user_answer": resp["user_answer"]
                    })

                # Save practice session
                session_data = {
                    "topic": topic,
                    "difficulty": difficulty,
                    "problem_type": problem_type,
                    "num_problems": num_problems,
                    "correct_count": correct_count,
                    "results": results,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                save_practice_session(session_data)

                # Display results
                st.markdown("---")
                st.subheader("Results")
                st.metric("Score", f"{correct_count}/{num_problems}",
                          f"{(correct_count / num_problems) * 100:.1f}%")

                for result in results:
                    if result["correct"]:
                        st.success(f"Problem {result['problem_number']}: Correct! {result['feedback']}")
                    else:
                        st.error(f"Problem {result['problem_number']}: Incorrect. {result['feedback']}")

    with tab2:
        st.subheader("Your Practice History")
        practice_history = get_practice_history()

        if not practice_history or len(practice_history) == 0:
            st.info("You haven't completed any practice sessions yet. Generate some problems to get started!")
        else:
            # Convert to DataFrame for easier display
            df = pd.DataFrame(practice_history)
            df["Score"] = df.apply(lambda
                                       x: f"{x['correct_count']}/{x['num_problems']} ({(x['correct_count'] / x['num_problems']) * 100:.1f}%)",
                                   axis=1)

            st.dataframe(
                df[["timestamp", "topic", "difficulty", "problem_type", "Score"]],
                use_container_width=True
            )

            if len(practice_history) >= 3:
                st.subheader("Performance Overview")
                # Add visualization of practice history here
                topics = df["topic"].value_counts().head(5)
                st.bar_chart(topics)


if __name__ == "__main__":
    main()