# utils/text_utils.py
import streamlit as st


def get_explanation(topic, detail_level="medium"):
    """Generate a comprehensive explanation of the topic"""
    try:
        prompt = f"""
        Create a comprehensive explanation about '{topic}'. 
        Make it {detail_level} level of detail, clear, and easy to understand.
        Include key concepts, important details, and real-world examples.
        Structure it in a way that's suitable for audio narration.
        """
        response = st.session_state.gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error getting explanation: {e}")
        return ""


def generate_study_notes(topic, explanation):
    """Generate structured study notes based on the explanation"""
    try:
        prompt = f"""
        Based on this explanation about '{topic}':

        {explanation}

        Create structured study notes with the following:
        1. Main concept definitions
        2. Key points organized by subtopics
        3. Important relationships between concepts
        4. A logical hierarchy of information

        Format it clearly with headers, bullet points, and numbering where appropriate.
        """
        response = st.session_state.gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating study notes: {e}")
        return ""


def generate_summary(topic, explanation):
    """Generate a bullet-point summary of the explanation"""
    try:
        prompt = f"""
        Based on this explanation about '{topic}':

        {explanation}

        Create a concise bullet-point summary that captures the essential information.
        Focus on the most important concepts, facts, and takeaways.
        Keep each bullet point brief but informative.
        """
        response = st.session_state.gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return ""


def generate_quiz(topic, explanation, num_questions=5):
    """Generate a multiple-choice quiz based on the topic explanation"""
    try:
        prompt = f"""
        Based on this explanation about '{topic}':

        {explanation}

        Create {num_questions} multiple-choice quiz questions to test understanding of key concepts.
        For each question, provide 4 options and indicate the correct answer.
        Format as:

        Q1: [Question]
        A. [Option A]
        B. [Option B]
        C. [Option C]
        D. [Option D]
        Correct Answer: [Letter]

        Then repeat for Q2 through Q{num_questions}.
        """
        response = st.session_state.gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating quiz: {e}")
        return ""


def generate_practice_problems(topic, explanation, difficulty="medium", num_problems=3):
    """Generate practice problems with solutions for the topic"""
    try:
        prompt = f"""
        Based on this explanation about '{topic}':

        {explanation}

        Create {num_problems} {difficulty}-level practice problems or exercises that would help someone master this topic.
        For each problem:
        1. Clearly state the problem or exercise
        2. Provide step-by-step solution or approach
        3. Include any relevant tips or hints

        Format with clear separation between problems, and clearly label the problem statement and solution parts.
        """
        response = st.session_state.gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating practice problems: {e}")
        return ""

