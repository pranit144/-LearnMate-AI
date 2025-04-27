# pages/1_Study_Dashboard.py - Progress tracking and learning paths

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
import time
import random

# Import utility functions
from utils.storage import load_session, get_session_list
from utils.api_connector import setup_gemini

# Page configuration
st.set_page_config(
    page_title="Study Dashboard - Personal Audio Tutor",
    page_icon="📊",
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

# Check if API is configured
if 'api_configured' not in st.session_state or not st.session_state.api_configured:
    st.warning("Please configure your API key on the main page before using this feature.")
    st.stop()

# Main dashboard
st.title("📊 Study Dashboard")
st.write("Track your learning journey and get personalized recommendations")

# Initialize session state for dashboard metrics if not exists
if 'study_streak' not in st.session_state:
    st.session_state.study_streak = random.randint(1, 5)  # Simulated data
if 'total_study_time' not in st.session_state:
    st.session_state.total_study_time = random.randint(120, 480)  # Simulated minutes
if 'topics_covered' not in st.session_state:
    st.session_state.topics_covered = len(st.session_state.study_history) if 'study_history' in st.session_state else 0
if 'last_study_date' not in st.session_state:
    st.session_state.last_study_date = datetime.now().strftime("%Y-%m-%d")

# Get study history
if 'study_history' not in st.session_state:
    st.session_state.study_history = []

# Dashboard metrics section
st.subheader("Learning Metrics")
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric("Study Streak", f"{st.session_state.study_streak} days")

with metric_col2:
    st.metric("Total Study Time", f"{st.session_state.total_study_time} min")

with metric_col3:
    st.metric("Topics Covered", st.session_state.topics_covered)

with metric_col4:
    st.metric("Last Study", st.session_state.last_study_date)

# Study history visualization
if st.session_state.study_history:
    st.subheader("Your Learning Journey")

    # Create a DataFrame from study history
    history_data = []
    for entry in st.session_state.study_history:
        # Add random study duration for demonstration purposes
        study_duration = random.randint(15, 60)
        history_data.append({
            'Topic': entry['topic'],
            'Date': entry['date'],
            'Type': entry.get('type', 'Topic'),
            'Detail Level': entry.get('detail_level', 'medium'),
            'Study Duration (min)': study_duration
        })

    history_df = pd.DataFrame(history_data)

    # Display as table
    with st.expander("View Study History Table"):
        st.dataframe(history_df)

    # Create visualizations
    viz_tab1, viz_tab2 = st.tabs(["Topic Distribution", "Study Time"])

    with viz_tab1:
        # Topic type distribution
        fig1 = px.pie(history_df, names='Type', title='Distribution of Learning Types',
                      color_discrete_sequence=px.colors.sequential.Viridis)
        st.plotly_chart(fig1, use_container_width=True)

    with viz_tab2:
        # Study time by topic
        fig2 = px.bar(history_df, x='Topic', y='Study Duration (min)',
                      title='Time Spent on Each Topic',
                      color='Detail Level',
                      color_discrete_sequence=px.colors.sequential.Plasma)
        st.plotly_chart(fig2, use_container_width=True)

# Learning recommendations
st.subheader("Personalized Learning Recommendations")

# Check if we have enough study history for recommendations
if len(st.session_state.study_history) >= 2:
    with st.spinner("Generating personalized recommendations..."):
        # In a real implementation, you would call the Gemini API here
        # For this example, we'll use mock recommendations

        # Get topics from history
        topics = [entry['topic'] for entry in st.session_state.study_history]

        # Mock recommendations based on topic names
        recommendations = [
            {
                "topic": f"Advanced {topics[-1]}",
                "reason": f"Build on your recent study of {topics[-1]}",
                "difficulty": "Advanced",
                "estimated_time": f"{random.randint(30, 60)} minutes"
            },
            {
                "topic": f"{topics[-1]} Applications in Real World",
                "reason": "Apply theoretical knowledge to practical scenarios",
                "difficulty": "Intermediate",
                "estimated_time": f"{random.randint(20, 45)} minutes"
            },
            {
                "topic": f"Relationship between {topics[-1]} and {topics[-2] if len(topics) > 1 else 'Related Fields'}",
                "reason": "Connect concepts across different areas of study",
                "difficulty": "Intermediate",
                "estimated_time": f"{random.randint(25, 50)} minutes"
            }
        ]

        # Display recommendations as cards
        rec_cols = st.columns(3)
        for i, rec in enumerate(recommendations):
            with rec_cols[i]:
                st.markdown(f"""
                <div style='padding: 20px; border-radius: 10px; border: 1px solid #ddd; height: 200px;'>
                    <h3>{rec['topic']}</h3>
                    <p><strong>Why: </strong>{rec['reason']}</p>
                    <p><strong>Difficulty: </strong>{rec['difficulty']}</p>
                    <p><strong>Est. Time: </strong>{rec['estimated_time']}</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Study This Topic", key=f"rec_{i}"):
                    # Set as current topic and redirect to main page
                    st.session_state.redirect_topic = rec['topic']
                    st.experimental_rerun()
else:
    st.info("Study at least 2 topics to get personalized recommendations!")

    # Provide some generic recommendations
    st.write("Here are some popular topics to explore:")

    generic_topics = [
        "Introduction to Machine Learning",
        "World History: Ancient Civilizations",
        "Basic Principles of Economics",
        "Understanding Quantum Physics",
        "Introduction to Psychology"
    ]

    gen_cols = st.columns(3)
    for i, topic in enumerate(generic_topics[:3]):
        with gen_cols[i]:
            st.markdown(f"""
            <div style='padding: 20px; border-radius: 10px; border: 1px solid #ddd; height: 150px;'>
                <h3>{topic}</h3>
                <p>Popular introductory topic</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Study This Topic", key=f"gen_{i}"):
                # Set as current topic and redirect to main page
                st.session_state.redirect_topic = topic
                st.experimental_rerun()

# Spaced repetition section
st.subheader("Review Reminders")
st.write("Based on spaced repetition principles, here are topics you should review:")

# Create some mock review suggestions
if 'study_history' in st.session_state and st.session_state.study_history:
    # Take up to 3 oldest topics
    review_topics = st.session_state.study_history[:3]

    review_cols = st.columns(len(review_topics))
    for i, topic in enumerate(review_topics):
        days_ago = random.randint(3, 14)
        review_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        with review_cols[i]:
            st.markdown(f"""
            <div style='padding: 15px; border-radius: 10px; background-color: #f0f8ff; border: 1px solid #ddd;'>
                <h4>{topic['topic']}</h4>
                <p>Last studied: {review_date}</p>
                <p>Review now to strengthen retention</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Review This Topic", key=f"review_{i}"):
                # Load the session for this topic
                if 'session_id' in topic:
                    load_session(topic['session_id'])
                    st.success(f"Loaded '{topic['topic']}' for review!")
                    st.experimental_rerun()
else:
    st.info("Your review schedule will appear here after you study some topics.")

# Learning path generator
with st.expander("Generate Learning Path"):
    st.write("Let AI create a personalized learning path for a subject of your choice.")

    path_subject = st.text_input("Enter a subject you want to master:")
    path_goal = st.text_input("What is your learning goal?")
    path_timeframe = st.selectbox("Timeframe", ["1 week", "1 month", "3 months", "6 months"])

    if path_subject and path_goal and st.button("Generate Learning Path"):
        with st.spinner("Creating your personalized learning path..."):
            # In a real implementation, you would call the Gemini API here
            # For this example, we'll use a mock learning path

            st.success(f"Your learning path for {path_subject} has been created!")

            # Create a mock learning path
            weeks = 1 if path_timeframe == "1 week" else 4 if path_timeframe == "1 month" else 12 if path_timeframe == "3 months" else 24

            st.markdown(f"## Learning Path: {path_subject}")
            st.markdown(f"**Goal:** {path_goal}")
            st.markdown(f"**Timeframe:** {path_timeframe}")

            # Create a mock milestone chart
            milestones = []
            for i in range(1, min(weeks + 1, 10)):
                milestone_name = f"Milestone {i}: {path_subject} - " + \
                                 ["Fundamentals", "Core Concepts", "Intermediate Knowledge",
                                  "Advanced Applications", "Practical Projects", "Expert Topics",
                                  "Specialization", "Mastery", "Teaching Others"][min(i - 1, 8)]
                milestones.append({
                    "Week": i,
                    "Milestone": milestone_name,
                    "Status": "Not Started"
                })

            # Display as table
            milestone_df = pd.DataFrame(milestones)
            st.dataframe(milestone_df)

            # Sample topics for the first few milestones
            st.markdown("### Week 1 Topics:")
            week1_topics = [
                f"Introduction to {path_subject}",
                f"History of {path_subject}",
                f"Basic {path_subject} Terminology",
                f"{path_subject} Fundamentals"
            ]

            for topic in week1_topics:
                st.markdown(f"- {topic}")

            st.markdown("### Week 2 Topics:")
            week2_topics = [
                f"Core {path_subject} Principles",
                f"{path_subject} in Practice",
                f"Common {path_subject} Problems",
                f"Building Your First {path_subject} Project"
            ]

            for topic in week2_topics:
                st.markdown(f"- {topic}")
    else:
        st.write("Need a structured learning plan? Expand the 'Generate Learning Path' section above.")

# Footer with navigation help
st.markdown("---")
st.info("📚 Navigate to other pages using the sidebar to continue your learning journey!")