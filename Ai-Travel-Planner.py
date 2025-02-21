import streamlit as st
import requests
import json
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- Custom CSS for an eye-catching look, including Google Font "Raleway" and highlight style ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,100..900;1,100..900&display=swap');
    
    /* Apply Raleway font globally with !important */
    body, .stApp, h1, h2, h3, h4, h5, h6, p, div {
        font-family: 'Raleway', sans-serif !important;
    }
    
    /* Set a fixed travel-themed background image */
    .stApp {
        background-image: url('https://source.unsplash.com/1600x900/?travel');
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* Style for the header image container */
    .header-img {
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Custom button style */
    div.stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #45a049;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: rgba(0, 0, 0, 0.7);
    }
    
    /* Text input field border styling */
    .stTextInput>div>div>input {
         border: 2px solid #4CAF50;
         border-radius: 4px;
    }
    
    /* Day Box Styling */
    .day-box {
       background-color: rgba(255, 255, 255, 0.2);
       padding: 15px;
       border-radius: 10px;
       margin-bottom: 15px;
       transition: transform 0.3s, box-shadow 0.3s;
    }
    .day-box:hover {
       transform: scale(1.02);
       box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    /* Highlight style to replace markdown bold */
    .highlight {
        background-color: #FFFF99;
        padding: 0 2px;
        border-radius: 3px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Header Image with Base64 Embedding ---
import base64

def get_base64_image(image_path):
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

header_image_data = get_base64_image('header-image.png')
st.markdown(
    f"""
    <div class="header-img">
        <img src="data:image/png;base64,{header_image_data}" alt="Travel" style="border-radius: 10px;">
    </div>
    """,
    unsafe_allow_html=True
)

# --- Sidebar for Additional Information ---
st.sidebar.title("About This App")
st.sidebar.info(
    """
    This innovative AI Travel Planner uses advanced AI technology to create personalized travel itineraries tailored to your preferences.
    
    **Features:**
    - Dynamic itinerary generation based on your destination, budget, and interests
    - Interactive bounding boxes for each day’s plan with engaging hover effects
    - A modern, visually appealing interface designed for an exceptional user experience
    """
)

# Set up Groq API credentials and configuration
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

# Improved function to convert markdown bold (**text**) to HTML with highlight styling.
def convert_markdown_to_html(text):
    pattern = r'(^|\s)\*\*(.+?)\*\*'
    replacement = r'\1<span class="highlight">\2</span>'
    return re.sub(pattern, replacement, text)

# Function to generate travel itinerary using Groq AI
def generate_itinerary(destination, days, budget, interests):
    prompt = f"""
    You are an AI travel planner. Create a {days}-day itinerary for {destination} considering:
    - Budget: {budget}
    - Interests: {interests}
    
    Format each day like:
    
    **Day 1:**
    - Morning: Activity
    - Afternoon: Activity
    - Evening: Activity

    Continue for {days} days.
    """
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload)
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.json()}"

# Function to display each day in its own bounding box with hover effect.
def display_bounding_boxes(itinerary_text):
    # Ensure sections like Afternoon and Evening start on new lines.
    itinerary_text = itinerary_text.replace(" - Afternoon:", "\n- Afternoon:")
    itinerary_text = itinerary_text.replace(" - Evening:", "\n- Evening:")
    
    # Split the itinerary into lines and group them by day based on lines starting with "**Day"
    lines = itinerary_text.split("\n")
    days = {}
    current_day = None
    for line in lines:
        line = line.strip()
        if line.startswith("**Day"):
            # Convert markdown bold to HTML for the day heading.
            day_heading = line.strip("*").strip()
            current_day = day_heading
            days[current_day] = []
        elif current_day:
            days[current_day].append(convert_markdown_to_html(line))
    
    # Render each day's content in its own styled box.
    for day, content_lines in days.items():
        content = "<br>".join(content_lines)
        html = f'<div class="day-box"><h3>{day}</h3><p>{content}</p></div>'
        st.markdown(html, unsafe_allow_html=True)

# Optional function to display text with a typewriter effect (if needed)
def typewriter_effect(text, speed=0.02):
    placeholder = st.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        placeholder.markdown(displayed_text)
        time.sleep(speed)

# --- Main App UI ---
st.title("AI Travel Planner ")

with st.form("trip_form"):
    destination = st.text_input("Enter your destination", placeholder="E.g., Paris, Tokyo")
    days = st.number_input("Number of days", min_value=1, max_value=30, value=5)
    budget = st.radio("Select Budget", options=["Normal", "Mid-range", "Luxury"])
    
    st.markdown("**Select Your Interests:**")
    interest_options = ["Adventure", "Food", "Culture", "History", "Nature"]
    cols = st.columns(len(interest_options))
    for idx, option in enumerate(interest_options):
        _ = cols[idx].checkbox(option, key=f"interest_{option}")
    
    selected_interests = [option for option in interest_options if st.session_state.get(f"interest_{option}")]
    st.markdown(f"**Selected Interests:** {', '.join(selected_interests) if selected_interests else 'None'}")
    
    additional_interest = st.text_input("Other Interests (optional)", placeholder="E.g., museums, hiking")
    
    submit_button = st.form_submit_button("Plan Trip")

if submit_button:
    if destination and days and budget and (selected_interests or additional_interest):
        st.subheader("Your AI-Generated Itinerary ")
        interests_combined = ", ".join(selected_interests)
        if additional_interest:
            interests_combined = interests_combined + ", " + additional_interest if interests_combined else additional_interest
        
        with st.spinner("Generating your travel itinerary..."):
            itinerary = generate_itinerary(destination, days, budget, interests_combined)
            time.sleep(1)  # Optional delay for effect
        
        # Display the itinerary using bounding boxes for each day.
        display_bounding_boxes(itinerary)
        # Uncomment the line below to use the typewriter effect if desired.
        # typewriter_effect(itinerary, speed=0.02)
    else:
        st.error("Please fill in all the fields before planning your trip.")
