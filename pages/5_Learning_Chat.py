import streamlit as st
import os
import sys
from datetime import datetime
import pandas as pd
import time

# Add the parent directory to sys.path to import utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.api_connector import generate_response, generate_audio
from utils.storage import save_chat_history, get_chat_history
from utils.text_utils import extract_key_concepts
from utils.audio_utils import play_audio

st.set_page_config(page_title="Learning Chat", page_icon="💬", layout="wide")


def display_message(role, content, with_audio=False):
    """Display a chat message with optional audio playback"""
    if role == "user":
        st.markdown(f"**You**: {content}")
    else:
        st.markdown(f"**Tutor**: {content}")
        if with_audio and content:
            audio_data = generate_audio(content)
            if audio_data:
                st.audio(audio_data, format="audio/mp3")


def initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_topic" not in st.session_state:
        st.session_state.current_topic = ""


def main():
    st.title("💬 Learning Chat")
    st.markdown("""
    Have a conversation with your personal learning assistant. Ask questions,
    request explanations, or discuss concepts to deepen your understanding.
    """)

    initialize_chat_history()

    # Sidebar for topic selection and settings
    with st.sidebar:
        st.subheader("Chat Settings")

        # Set or change current topic
        new_topic = st.text_input("Current Learning Topic:", value=st.session_state.current_topic)
        if new_topic != st.session_state.current_topic:
            st.session_state.current_topic = new_topic
            if new_topic:
                st.success(f"Topic set to: {new_topic}")

        # Audio settings
        enable_audio = st.checkbox("Enable Audio Responses", value=False)

        if enable_audio:
            voice_style = st.selectbox("Voice Style:",
                                       ["Friendly", "Professional", "Instructional"],
                                       index=0)

        # Tutor persona
        tutor_persona = st.selectbox("Tutor Persona:",
                                     ["Helpful Guide", "Socratic Teacher", "Expert Explainer", "Patient Coach"],
                                     index=0)

        # Save and load chats
        st.divider()
        st.subheader("Manage Chats")

        if st.button("Save Current Chat"):
            if len(st.session_state.messages) > 0:
                topic = st.session_state.current_topic or "General Chat"
                save_chat_history(topic, st.session_state.messages)
                st.success(f"Chat saved as '{topic}'")
            else:
                st.warning("No messages to save")

        st.subheader("Previous Chats")
        chat_history = get_chat_history()

        if chat_history and len(chat_history) > 0:
            selected_chat = st.selectbox("Select a chat to load:",
                                         [f"{chat['topic']} ({chat['timestamp']})" for chat in chat_history])

            if st.button("Load Selected Chat"):
                selected_index = [f"{chat['topic']} ({chat['timestamp']})" for chat in chat_history].index(
                    selected_chat)
                st.session_state.messages = chat_history[selected_index]["messages"]
                st.session_state.current_topic = chat_history[selected_index]["topic"]
                st.experimental_rerun()

        if st.button("Start New Chat"):
            st.session_state.messages = []
            st.session_state.current_topic = ""
            st.experimental_rerun()

    # Display chat history
    for message in st.session_state.messages:
        display_message(message["role"], message["content"])

    # Input for new message
    user_input = st.chat_input("Ask a question or discuss a concept...")

    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        display_message("user", user_input)

        # Generate response
        with st.spinner("Thinking..."):
            # Prepare context for better response
            context = {
                "topic": st.session_state.current_topic,
                "persona": tutor_persona,
                "chat_history": st.session_state.messages[-5:] if len(
                    st.session_state.messages) > 5 else st.session_state.messages,
            }

            response = generate_response(user_input, context)

            if response:
                # Add assistant message to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Display with audio if enabled
                display_message("assistant", response, with_audio=enable_audio)

                # If no topic is set, try to extract one from the conversation
                if not st.session_state.current_topic and len(st.session_state.messages) >= 3:
                    combined_text = " ".join([msg["content"] for msg in st.session_state.messages])
                    potential_topics = extract_key_concepts(combined_text, max_concepts=1)
                    if potential_topics:
                        st.session_state.current_topic = potential_topics[0]
                        st.sidebar.success(f"Topic detected: {st.session_state.current_topic}")
            else:
                st.error("I couldn't generate a response. Please try again.")

    # Bottom buttons for helpful prompts
    st.markdown("---")
    st.subheader("Helpful Prompts")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Explain this concept"):
            if st.session_state.current_topic:
                prompt = f"Please explain the concept of {st.session_state.current_topic} in simple terms."
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.experimental_rerun()
            else:
                st.warning("Please set a learning topic first")
    with col2:
        if st.button("Give me practice questions"):
            if st.session_state.current_topic:
                prompt = f"Can you provide 3 practice questions about {st.session_state.current_topic}?"
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.experimental_rerun()
            else:
                st.warning("Please set a learning topic first")
    with col3:
        if st.button("Summarize our discussion"):
            if len(st.session_state.messages) > 2:
                prompt = "Can you summarize what we've discussed so far?"
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.experimental_rerun()
            else:
                st.warning("We need more conversation to summarize")


if __name__ == "__main__":
    main()