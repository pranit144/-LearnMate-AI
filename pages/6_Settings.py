import streamlit as st
import os
import sys
import json
from datetime import datetime
import pandas as pd

# Add the parent directory to sys.path to import utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.storage import save_user_preferences, get_user_preferences, get_usage_statistics

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")


def main():
    st.title("⚙️ Settings")
    st.markdown("""
    Customize your learning experience and manage your account settings.
    """)

    # Get current preferences
    user_prefs = get_user_preferences()

    tabs = st.tabs(
        ["Learning Preferences", "Interface Settings", "Audio Settings", "Data Management", "Usage Statistics"])

    with tabs[0]:
        st.subheader("Learning Preferences")

        col1, col2 = st.columns(2)
        with col1:
            default_difficulty = user_prefs.get("default_difficulty", "Intermediate")
            difficulty = st.select_slider(
                "Default Difficulty Level:",
                options=["Beginner", "Intermediate", "Advanced"],
                value=default_difficulty
            )

            default_learning_style = user_prefs.get("learning_style", "Visual")
            learning_style = st.selectbox(
                "Primary Learning Style:",
                ["Visual", "Auditory", "Reading/Writing", "Kinesthetic", "Mixed"],
                index=["Visual", "Auditory", "Reading/Writing", "Kinesthetic", "Mixed"].index(default_learning_style)
            )

        with col2:
            default_session_length = user_prefs.get("session_length", 30)
            session_length = st.slider(
                "Default Study Session Length (minutes):",
                15, 120, default_session_length, 15
            )

            default_reminder = user_prefs.get("study_reminder", False)
            reminder = st.checkbox(
                "Enable study reminders",
                value=default_reminder
            )

            if reminder:
                default_reminder_freq = user_prefs.get("reminder_frequency", "Daily")
                reminder_freq = st.selectbox(
                    "Reminder Frequency:",
                    ["Daily", "Every other day", "Weekly"],
                    index=["Daily", "Every other day", "Weekly"].index(default_reminder_freq)
                )

        st.subheader("Subject Preferences")

        default_subjects = user_prefs.get("favorite_subjects", [])
        subjects = st.multiselect(
            "Favorite Subjects:",
            ["Mathematics", "Science", "History", "Literature", "Computer Science",
             "Languages", "Art", "Music", "Psychology", "Economics"],
            default=default_subjects
        )

        default_goals = user_prefs.get("learning_goals", "")
        goals = st.text_area(
            "Learning Goals:",
            value=default_goals,
            help="What do you hope to achieve with this learning tool?"
        )

    with tabs[1]:
        st.subheader("Interface Settings")

        col1, col2 = st.columns(2)
        with col1:
            default_theme = user_prefs.get("theme", "Light")
            theme = st.selectbox(
                "Theme:",
                ["Light", "Dark", "System default"],
                index=["Light", "Dark", "System default"].index(default_theme)
            )

            default_font_size = user_prefs.get("font_size", "Medium")
            font_size = st.selectbox(
                "Font Size:",
                ["Small", "Medium", "Large", "Extra Large"],
                index=["Small", "Medium", "Large", "Extra Large"].index(default_font_size)
            )

        with col2:
            default_layout = user_prefs.get("layout", "Compact")
            layout = st.selectbox(
                "Layout Style:",
                ["Compact", "Comfortable", "Spacious"],
                index=["Compact", "Comfortable", "Spacious"].index(default_layout)
            )

            default_animations = user_prefs.get("animations", True)
            animations = st.checkbox(
                "Enable UI animations",
                value=default_animations
            )

        st.subheader("Notification Settings")

        default_email_notif = user_prefs.get("email_notifications", False)
        email_notif = st.checkbox(
            "Email Notifications",
            value=default_email_notif
        )

        default_browser_notif = user_prefs.get("browser_notifications", True)
        browser_notif = st.checkbox(
            "Browser Notifications",
            value=default_browser_notif
        )

    with tabs[2]:
        st.subheader("Audio Settings")

        enable_audio = st.checkbox(
            "Enable audio responses",
            value=user_prefs.get("enable_audio", False)
        )

        if enable_audio:
            col1, col2 = st.columns(2)
            with col1:
                default_voice = user_prefs.get("voice_type", "Friendly")
                voice_type = st.selectbox(
                    "Voice Type:",
                    ["Friendly", "Professional", "Instructional", "Energetic"],
                    index=["Friendly", "Professional", "Instructional", "Energetic"].index(default_voice)
                )

                default_speed = user_prefs.get("speech_speed", 1.0)
                speech_speed = st.slider(
                    "Speech Speed:",
                    0.5, 2.0, default_speed, 0.1
                )

            with col2:
                default_volume = user_prefs.get("volume", 80)
                volume = st.slider(
                    "Default Volume:",
                    0, 100, default_volume, 5
                )

                text_highlight = st.checkbox(
                    "Highlight text during audio playback",
                    value=user_prefs.get("text_highlight", True)
                )

        st.subheader("Advanced Audio Settings")
        with st.expander("Advanced Audio Settings", expanded=False):
            background_music = st.checkbox(
                "Enable subtle background music during study sessions",
                value=user_prefs.get("background_music", False)
            )

            if background_music:
                music_type = st.selectbox(
                    "Background Music Type:",
                    ["Ambient", "Classical", "Lo-fi", "Nature Sounds", "White Noise"],
                    index=["Ambient", "Classical", "Lo-fi", "Nature Sounds", "White Noise"].index(
                        user_prefs.get("music_type", "Lo-fi"))
                )

    with tabs[3]:
        st.subheader("Data Management")

        st.markdown("""
        Manage your learning data, history, and account settings.
        """)

        export_col, delete_col = st.columns(2)

        with export_col:
            st.subheader("Export Your Data")
            export_options = st.multiselect(
                "Select data to export:",
                ["Learning history", "Practice sessions", "Quiz results", "Chat history", "Visual aids"]
            )

            export_format = st.selectbox(
                "Export format:",
                ["JSON", "CSV", "PDF"]
            )

            if st.button("Export Selected Data"):
                if export_options:
                    st.success(f"Data export initiated in {export_format} format!")
                    st.download_button(
                        label="Download Exported Data",
                        data="Placeholder for actual data export",
                        file_name=f"learning_data_export_{datetime.now().strftime('%Y%m%d')}.{export_format.lower()}",
                        mime="application/json" if export_format == "JSON" else "text/csv"
                    )
                else:
                    st.warning("Please select at least one data category to export.")

        with delete_col:
            st.subheader("Delete Data")
            delete_options = st.multiselect(
                "Select data to delete:",
                ["Learning history", "Practice sessions", "Quiz results", "Chat history", "Visual aids",
                 "All user data"]
            )

            if "All user data" in delete_options:
                st.warning("⚠️ Warning: This will delete ALL of your data and cannot be undone!")

            confirm_delete = st.text_input("Type 'DELETE' to confirm deletion:")

            if st.button("Delete Selected Data"):
                if not delete_options:
                    st.warning("Please select data to delete.")
                elif "All user data" in delete_options and confirm_delete != "DELETE":
                    st.error("Please type 'DELETE' to confirm full data deletion.")
                elif confirm_delete != "DELETE":
                    st.error("Please type 'DELETE' to confirm deletion.")
                else:
                    st.success("Selected data has been deleted.")

    with tabs[4]:
        st.subheader("Usage Statistics")

        # Get usage stats
        usage_data = get_usage_statistics()

        if not usage_data:
            st.info("No usage data available yet. Start learning to see your statistics!")
        else:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Study Time", f"{usage_data.get('total_study_time', 0)} hours")
            with col2:
                st.metric("Practice Problems Completed", usage_data.get('total_problems', 0))
            with col3:
                st.metric("Quiz Success Rate", f"{usage_data.get('quiz_success_rate', 0)}%")

            st.subheader("Study Time by Subject")
            subject_data = usage_data.get('subject_distribution', {})
            if subject_data:
                st.bar_chart(subject_data)

            st.subheader("Learning Activity")
            activity_data = usage_data.get('activity_timeline', {})
            if activity_data:
                activity_df = pd.DataFrame(list(activity_data.items()), columns=['Date', 'Minutes'])
                activity_df['Date'] = pd.to_datetime(activity_df['Date'])
                activity_df = activity_df.sort_values('Date')
                st.line_chart(activity_df.set_index('Date'))

            st.subheader("Improvement Over Time")
            improvement_data = usage_data.get('improvement_metrics', {})
            if improvement_data:
                st.line_chart(improvement_data)

    # Save button (at the bottom of the page)
    if st.button("Save Settings", type="primary"):
        # Collect all settings
        new_preferences = {
            # Learning Preferences
            "default_difficulty": difficulty,
            "learning_style": learning_style,
            "session_length": session_length,
            "study_reminder": reminder,
            "favorite_subjects": subjects,
            "learning_goals": goals,

            # Interface Settings
            "theme": theme,
            "font_size": font_size,
            "layout": layout,
            "animations": animations,
            "email_notifications": email_notif,
            "browser_notifications": browser_notif,

            # Audio Settings
            "enable_audio": enable_audio,
        }

        if enable_audio:
            new_preferences.update({
                "voice_type": voice_type,
                "speech_speed": speech_speed,
                "volume": volume,
                "text_highlight": text_highlight,
                "background_music": background_music,
            })

            if background_music:
                new_preferences["music_type"] = music_type

        if reminder:
            new_preferences["reminder_frequency"] = reminder_freq

        # Save the preferences
        save_user_preferences(new_preferences)
        st.success("Settings saved successfully!")


# Run the main function when the script is executed
if __name__ == "__main__":
    main()