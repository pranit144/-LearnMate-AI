# utils/api_connector.py
import google.generativeai as genai
import streamlit as st
import re

def setup_gemini(api_key):
    """Setup connection to Google Gemini API"""
    try:
        genai.configure(api_key=api_key)
        # Initialize models once and store in session state
        st.session_state.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        return True
    except Exception as e:
        st.error(f"Error setting up Gemini API: {e}")
        return False

def is_valid_api_key_format(api_key):
    """Check if string matches typical Gemini API key format"""
    # Basic check for Google API key format
    return bool(api_key and len(api_key) > 20 and api_key.startswith("AIza"))
