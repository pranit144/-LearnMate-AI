# main.py - Homepage of your app

import streamlit as st
import os
import base64
from pathlib import Path
import tempfile
import re
import time
import json
from datetime import datetime

# Import utility functions
from utils.api_connector import setup_gemini, is_valid_api_key_format
from utils.audio_utils import generate_audio, get_download_link, split_text_into_chunks
from utils.image_utils import generate_image_descriptions, generate_placeholder_images
from utils.text_utils import get_explanation, generate_study_notes, generate_summary
from utils.storage import save_session, load_session, get_session_list

# Set page configuration
st.set_page_config(
    page_title="Personal Audio Tutor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'explanation' not in st.session_state:
    st.session_state.explanation = ""
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'notes' not in st.session_state:
    st.session_state.notes = ""
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None
if 'images' not in st.session_state:
    st.session_state.images = []
if 'gemini_model' not in st.session_state:
    st.session_state.gemini_model = None
if 'api_configured' not in st.session_state:
    st.session_state.api_configured = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{int(time.time())}"
if 'study_history' not in st.session_state:
    st.session_state.study_history = []
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'font_size' not in st.session_state:
    st.session_state.font_size = "medium"

# Apply theme based on dark_mode setting
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        .main {background-color: #1E1E1E; color: #FFFFFF;}
        .stTextInput > div > div > input {background-color: #2E2E2E; color: #FFFFFF;}
        .stSelectbox > div > div > select {background-color: #2E2E2E; color: #FFFFFF;}
    </style>
    """, unsafe_allow_html=True)

# Apply font size
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


# Main app UI
def main():
    st.title("🎓 Personal Audio Tutor")
    st.write("Your AI-powered study companion: Learn any topic through text, audio, and visuals")

    # App description and navigation help
    with st.expander("About This App"):
        st.markdown("""
        **Welcome to Personal Audio Tutor!**

        This app uses Google's Gemini AI to create personalized learning materials on any topic you want to study.

        **Features:**
        - Generate comprehensive explanations with audio narration
        - Create visual aids to help understand concepts
        - Get structured study notes and summaries
        - Take interactive quizzes to test your knowledge
        - Track your learning progress

        **Navigation:**
        - Use the sidebar pages to access different features
        - The main page is for generating new learning content
        - Your progress is automatically saved

        Start by entering a topic below and clicking "Generate Learning Materials"!
        """)

    # Sidebar for settings and navigation
    with st.sidebar:
        st.header("Settings")
        api_key = ""
        if api_key and is_valid_api_key_format(api_key):
            if st.button("Connect API") or not st.session_state.api_configured:
                api_configured = setup_gemini(api_key)
                st.session_state.api_configured = api_configured
                if api_configured:
                    st.success("API connected successfully!")

        if not st.session_state.api_configured:
            st.warning("Please enter a valid Gemini API key to continue")

        # Quick settings in sidebar
        st.subheader("Quick Settings")
        st.session_state.dark_mode = st.toggle("Dark Mode", st.session_state.dark_mode)
        st.session_state.font_size = st.select_slider(
            "Font Size",
            options=["small", "medium", "large", "x-large"],
            value=st.session_state.font_size
        )

        # Recent topics section
        if st.session_state.study_history:
            st.subheader("Recent Topics")
            for i, topic_data in enumerate(st.session_state.study_history[-5:]):
                if st.button(f"📚 {topic_data['topic']}", key=f"recent_{i}"):
                    load_session(topic_data['session_id'])
                    st.experimental_rerun()

    # Main input area
    st.header("What would you like to learn about today?")

    col1, col2 = st.columns([3, 1])

    with col1:
        topic = st.text_input("Enter a topic, chapter, or book title:")

    with col2:
        topic_type = st.selectbox("Learning Type", ["Topic", "Chapter", "Book"], index=0)
        detail_level = st.selectbox("Detail Level", ["basic", "medium", "advanced"], index=1)

    # Process button
    if st.button("Generate Learning Materials") and topic and st.session_state.api_configured:
        st.session_state.current_topic = topic

        # Create a session ID for this learning session
        session_id = f"{st.session_state.user_id}_{int(time.time())}"

        with st.spinner("Generating your personalized learning materials..."):
            # Generate explanation
            st.session_state.explanation = get_explanation(topic, detail_level)

            if st.session_state.explanation:
                # Generate study notes and summary
                st.session_state.notes = generate_study_notes(topic, st.session_state.explanation)
                st.session_state.summary = generate_summary(topic, st.session_state.explanation)

                # Generate image descriptions and create placeholder images
                image_descriptions = generate_image_descriptions(topic, st.session_state.explanation, 3)
                st.session_state.images = generate_placeholder_images(image_descriptions)
                st.session_state.image_descriptions = image_descriptions

                # Generate audio for the explanation
                text = st.session_state.explanation
                text_chunks = split_text_into_chunks(text)

                if len(text_chunks) == 1:
                    st.session_state.audio_file = generate_audio(text, "en-US", 1.0)
                    st.session_state.has_multiple_chunks = False
                else:
                    # For longer text, only generate audio for the first chunk
                    first_chunk = text_chunks[0]
                    st.session_state.audio_file = generate_audio(first_chunk, "en-US", 1.0)
                    st.session_state.text_chunks = text_chunks
                    st.session_state.has_multiple_chunks = True

                # Save to study history
                topic_data = {
                    "topic": topic,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "session_id": session_id,
                    "type": topic_type,
                    "detail_level": detail_level
                }

                # Add to study history (prevent duplicates)
                if not any(d['topic'] == topic for d in st.session_state.study_history):
                    st.session_state.study_history.append(topic_data)

                # Save session
                save_session(session_id, {
                    "topic": topic,
                    "topic_type": topic_type,
                    "explanation": st.session_state.explanation,
                    "notes": st.session_state.notes,
                    "summary": st.session_state.summary,
                    "image_descriptions": image_descriptions,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "detail_level": detail_level
                })

    # Display results if available
    if st.session_state.explanation:
        # Use tabs to organize the different types of content
        tab1, tab2, tab3, tab4 = st.tabs(["Explanation", "Audio Narration", "Visual Aids", "Study Materials"])

        with tab1:
            st.subheader(f"{topic_type}: {st.session_state.current_topic}")

            # Add a search function for the explanation
            search_term = st.text_input("Search in explanation:", key="search_explanation")
            if search_term:
                highlighted_text = st.session_state.explanation.replace(
                    search_term, f"**{search_term}**"
                )
                st.markdown(highlighted_text)
            else:
                st.markdown(st.session_state.explanation)

            # Text-to-speech button for selected text
            selected_text = st.text_area("Select text to hear (copy and paste here):",
                                         height=100, key="selected_text")
            if selected_text and st.button("Listen to Selected Text"):
                with st.spinner("Generating audio..."):
                    selected_audio = generate_audio(selected_text, "en-US", 1.0)
                    st.audio(selected_audio)

        with tab2:
            st.subheader("Audio Narration")
            if st.session_state.audio_file:
                st.audio(st.session_state.audio_file)
                st.markdown(get_download_link(st.session_state.audio_file, "Download Audio File"),
                            unsafe_allow_html=True)

                # Show information about text chunking if applicable
                if st.session_state.has_multiple_chunks:
                    st.info(
                        f"The explanation has been split into {len(st.session_state.text_chunks)} parts for audio generation. Currently playing part 1.")

                    # Add option to generate audio for other chunks
                    chunk_options = [f"Part {i + 1}" for i in range(len(st.session_state.text_chunks))]
                    selected_chunk_index = st.selectbox(
                        "Select part to play:",
                        range(len(chunk_options)),
                        format_func=lambda x: chunk_options[x]
                    )

                    if st.button("Generate Audio for Selected Part"):
                        with st.spinner(f"Generating audio for {chunk_options[selected_chunk_index]}..."):
                            chunk_text = st.session_state.text_chunks[selected_chunk_index]
                            st.session_state.audio_file = generate_audio(chunk_text, "en-US", 1.0)
                            st.experimental_rerun()

        with tab3:
            st.subheader("Visual Aids")

            # Display image descriptions
            if hasattr(st.session_state, 'image_descriptions'):
                for i, desc in enumerate(st.session_state.image_descriptions):
                    st.markdown(f"**Image {i + 1}**: {desc}")

            # Display images in a grid
            if st.session_state.images:
                cols = st.columns(min(3, len(st.session_state.images)))
                for i, img in enumerate(st.session_state.images):
                    col_idx = i % 3
                    with cols[col_idx]:
                        st.image(img, use_column_width=True, caption=f"Concept {i + 1}")

        with tab4:
            st.subheader("Study Materials")

            sub_tab1, sub_tab2 = st.tabs(["Structured Notes", "Bullet-Point Summary"])

            with sub_tab1:
                st.markdown(st.session_state.notes)

            with sub_tab2:
                st.markdown(st.session_state.summary)

            # Navigation to other pages
            st.info(
                "Visit the Quizzes, Practice Problems, and Visual Learning pages in the sidebar for more study materials!")

    # Show prompt to use sidebar navigation when no content is generated
    else:
        st.info("Enter a topic above to get started, or select a recent topic from the sidebar.")
        st.write("Check out other features using the sidebar navigation:")

        feature_col1, feature_col2 = st.columns(2)

        with feature_col1:
            st.markdown("### 📊 Study Dashboard")
            st.write("Track your learning progress and get personalized learning paths")

            st.markdown("### 🧩 Interactive Quizzes")
            st.write("Test your knowledge with AI-generated quizzes")

            st.markdown("### 🖼️ Visual Learning")
            st.write("Access mind maps and enhanced visual aids")

        with feature_col2:
            st.markdown("### ✏️ Practice Problems")
            st.write("Solve AI-generated practice problems with explanations")

            st.markdown("### 💬 Learning Chat")
            st.write("Have a conversation with AI about your topic")

            st.markdown("### ⚙️ Settings")
            st.write("Customize your learning experience")


# Run the app
if __name__ == "__main__":
    main()