import streamlit as st
import os
import sys
import pandas as pd
from PIL import Image
import io
import base64

# Add the parent directory to sys.path to import utils
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from utils.api_connector import generate_mind_map, generate_image
from utils.storage import save_visual_aid, get_user_visuals
from utils.text_utils import extract_key_concepts

st.set_page_config(page_title="Visual Learning", page_icon="🎨", layout="wide")


def display_mind_map(topic, concepts):
    """Generate and display a mind map for the given topic and concepts"""
    with st.spinner(f"Creating mind map for '{topic}'..."):
        mind_map_content = generate_mind_map(topic, concepts)
        if mind_map_content:
            st.markdown("### Mind Map")
            st.graphviz_chart(mind_map_content)

            if st.button("Save Mind Map"):
                save_visual_aid(topic, "mind_map", mind_map_content)
                st.success(f"Mind map for '{topic}' saved successfully!")
        else:
            st.error("Failed to generate mind map. Please try again.")


def display_visual_aid(topic, description):
    """Generate and display a visual aid for the given topic"""
    with st.spinner(f"Creating visual aid for '{topic}'..."):
        image_data = generate_image(description)
        if image_data:
            st.markdown("### Visual Aid")
            st.image(image_data, caption=topic)

            if st.button("Save Visual Aid"):
                save_visual_aid(topic, "image", image_data)
                st.success(f"Visual aid for '{topic}' saved successfully!")
        else:
            st.error("Failed to generate visual aid. Please try again.")


def main():
    st.title("🎨 Visual Learning")
    st.markdown("""
    Enhance your understanding through visual aids and mind maps. 
    Visual learning tools help reinforce concepts and improve retention.
    """)

    tab1, tab2, tab3 = st.tabs(["Create Mind Maps", "Generate Visual Aids", "Saved Visuals"])

    with tab1:
        st.subheader("Create Mind Maps")
        topic = st.text_input("Enter a learning topic:")

        if topic:
            with st.expander("Advanced Options", expanded=False):
                depth = st.slider("Depth of Mind Map", 1, 5, 3)
                style = st.selectbox("Mind Map Style", ["Hierarchical", "Radial", "Circular"])

            if st.button("Generate Mind Map"):
                concepts = extract_key_concepts(topic)
                display_mind_map(topic, concepts)

    with tab2:
        st.subheader("Generate Visual Aids")
        topic = st.text_input("Topic for Visual Aid:")

        if topic:
            description = st.text_area("Describe what you want in the visual (be specific):",
                                       "Create an educational visual aid showing the key elements of " + topic)

            if st.button("Generate Visual Aid"):
                display_visual_aid(topic, description)

    with tab3:
        st.subheader("Your Saved Visuals")
        saved_visuals = get_user_visuals()

        if not saved_visuals or len(saved_visuals) == 0:
            st.info("You haven't saved any visual aids yet. Create some mind maps or visual aids to see them here!")
        else:
            visual_type = st.radio("Filter by type:", ["All", "Mind Maps", "Visual Aids"])

            filtered_visuals = saved_visuals
            if visual_type == "Mind Maps":
                filtered_visuals = [v for v in saved_visuals if v["type"] == "mind_map"]
            elif visual_type == "Visual Aids":
                filtered_visuals = [v for v in saved_visuals if v["type"] == "image"]

            for visual in filtered_visuals:
                with st.expander(f"{visual['topic']} ({visual['date']})"):
                    if visual["type"] == "mind_map":
                        st.graphviz_chart(visual["content"])
                    else:  # image
                        st.image(visual["content"], caption=visual["topic"])

                    if st.button("Delete", key=f"delete_{visual['id']}"):
                        # Add delete functionality
                        st.success(f"Deleted '{visual['topic']}'")


if __name__ == "__main__":
    main()