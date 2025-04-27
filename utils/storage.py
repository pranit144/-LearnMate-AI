
# utils/storage.py
import os
import json
import streamlit as st
from datetime import datetime
import tempfile


# Create data directory if it doesn't exist
def ensure_data_dir():
    """Ensure data directories exist"""
    data_dir = os.path.join(tempfile.gettempdir(), "personal_audio_tutor")
    user_sessions_dir = os.path.join(data_dir, "user_sessions")

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if not os.path.exists(user_sessions_dir):
        os.makedirs(user_sessions_dir)

    return data_dir, user_sessions_dir


def save_session(session_id, session_data):
    """Save session data to file"""
    try:
        _, user_sessions_dir = ensure_data_dir()

        # Create a file for this session
        session_file = os.path.join(user_sessions_dir, f"{session_id}.json")

        with open(session_file, 'w') as f:
            json.dump(session_data, f)

        return True
    except Exception as e:
        st.error(f"Error saving session: {e}")
        return False


def load_session(session_id):
    """Load session data from file"""
    try:
        _, user_sessions_dir = ensure_data_dir()

        # Find the session file
        session_file = os.path.join(user_sessions_dir, f"{session_id}.json")

        if not os.path.exists(session_file):
            st.warning(f"Session file not found: {session_id}")
            return False

        with open(session_file, 'r') as f:
            session_data = json.load(f)

        # Update session state with loaded data
        st.session_state.current_topic = session_data.get('topic', '')
        st.session_state.explanation = session_data.get('explanation', '')
        st.session_state.notes = session_data.get('notes', '')
        st.session_state.summary = session_data.get('summary', '')

        # Update image descriptions if available
        if 'image_descriptions' in session_data:
            from utils.image_utils import generate_placeholder_images
            st.session_state.image_descriptions = session_data['image_descriptions']
            st.session_state.images = generate_placeholder_images(session_data['image_descriptions'])

        # Generate fresh audio file based on the explanation
        if st.session_state.explanation:
            from utils.audio_utils import generate_audio, split_text_into_chunks

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

        return True
    except Exception as e:
        st.error(f"Error loading session: {e}")
        return False


def get_session_list():
    """Get list of all saved sessions"""
    try:
        _, user_sessions_dir = ensure_data_dir()

        sessions = []
        for filename in os.listdir(user_sessions_dir):
            if filename.endswith('.json'):
                session_id = filename.replace('.json', '')

                # Get basic info from the session file
                with open(os.path.join(user_sessions_dir, filename), 'r') as f:
                    try:
                        data = json.load(f)
                        sessions.append({
                            'session_id': session_id,
                            'topic': data.get('topic', 'Unknown Topic'),
                            'date': data.get('date', 'Unknown Date'),
                            'type': data.get('topic_type', 'Topic')
                        })
                    except json.JSONDecodeError:
                        # Skip invalid JSON files
                        continue

        return sessions
    except Exception as e:
        st.error(f"Error listing sessions: {e}")
        return []