
# utils/audio_utils.py
import os
import tempfile
from gtts import gTTS
import base64
import streamlit as st

def generate_audio(text, voice='en-US', speed=1.0):
    """Generate audio file from text using gTTS"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
            tts = gTTS(text=text, lang=voice[:2], slow=False)
            tts.save(temp_audio.name)
            return temp_audio.name
    except Exception as e:
        st.error(f"Error generating audio: {e}")
        return None

def get_download_link(file_path, label):
    """Create a download link for a file"""
    with open(file_path, "rb") as file:
        contents = file.read()
    b64 = base64.b64encode(contents).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{os.path.basename(file_path)}">{label}</a>'
    return href


# utils/audio_utils.py (continued)
def split_text_into_chunks(text, max_length=4000):
    """Split long text into chunks for audio generation"""
    paragraphs = text.split('\n')
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) > max_length:
            chunks.append(current_chunk)
            current_chunk = paragraph + '\n'
        else:
            current_chunk += paragraph + '\n'

    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


