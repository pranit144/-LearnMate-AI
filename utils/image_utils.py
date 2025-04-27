# utils/image_utils.py
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
import re


def generate_image_descriptions(topic, explanation, num_images=3):
    """Generate descriptions for educational images based on the topic explanation"""
    try:
        prompt = f"""
        Based on this explanation about '{topic}':

        {explanation}

        Create {num_images} detailed descriptions for educational diagrams or illustrations that would help visualize key concepts from this topic.
        Each description should:
        1. Focus on a single important concept from the topic
        2. Be clear about what elements should be in the image
        3. Emphasize educational value rather than artistic quality
        4. Be suitable for a diagram, chart, or simple illustration

        Format your response as a numbered list with only the descriptions, nothing else.
        """
        response = st.session_state.gemini_model.generate_content(prompt)

        # Extract image descriptions
        descriptions_text = response.text
        descriptions = []

        # Simple parsing of numbered items
        pattern = r'\d+\.\s+(.*?)(?=\d+\.|$)'
        matches = re.findall(pattern, descriptions_text, re.DOTALL)

        if matches:
            descriptions = [match.strip() for match in matches]
        else:
            # Fallback: just split by lines and filter
            lines = [line.strip() for line in descriptions_text.split('\n') if line.strip()]
            descriptions = [line.split('. ', 1)[1] if '. ' in line else line for line in lines]

        return descriptions[:num_images]  # Return only the requested number
    except Exception as e:
        st.error(f"Error generating image descriptions: {e}")
        return []


def generate_placeholder_images(image_descriptions):
    """Create placeholder images with text overlay for each description"""
    images = []

    for i, description in enumerate(image_descriptions):
        try:
            # Create a placeholder image with the topic text
            width, height = 800, 600
            img = Image.new('RGB', (width, height), color=(240, 248, 255))  # Light blue background

            # Add topic text as an overlay
            draw = ImageDraw.Draw(img)

            # Try to load a font, use default if not available
            try:
                font = ImageFont.truetype("Arial.ttf", 28)
                small_font = ImageFont.truetype("Arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()

            # Add a title at the top
            title = f"Concept {i + 1}"
            draw.text((width // 2, 50), title, fill=(0, 0, 128), font=font)

            # Wrap text to fit in the image
            words = description.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 40:  # Adjust based on your needs
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

            # Draw the wrapped text
            y_position = 150
            for line in lines:
                text_width = draw.textlength(line, font=small_font)
                draw.text((width // 2 - text_width // 2, y_position), line, fill=(0, 0, 0), font=small_font)
                y_position += 30

            # Draw a border
            draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(0, 0, 128), width=2)

            images.append(img)
        except Exception as e:
            st.error(f"Error creating placeholder image {i + 1}: {e}")
            # Create a very simple fallback image with error message
            img = Image.new('RGB', (800, 600), color=(255, 240, 240))  # Light red background
            draw = ImageDraw.Draw(img)
            draw.text((400, 300), f"Error creating image: {str(e)}", fill=(128, 0, 0))
            images.append(img)

    return images


