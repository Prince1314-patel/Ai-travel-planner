import streamlit as st
import requests

# Set up the Streamlit app
st.title("Custom Itinerary Generator")

# Trip Details Section
st.subheader("Trip Details")
destination = st.text_input("Destination")
num_days = st.number_input("Number of days", min_value=1, step=1)
budget = st.number_input("Budget (INR)", min_value=0.0, step=1000.0)

# Preferences Section
st.subheader("Preferences")
interests = st.multiselect(
    "Interests",
    options=["Art", "History", "Food", "Adventure", "Relaxation", "Culture", "Shopping"]
)
companions = st.radio("Travel companions", options=["Solo", "Couple", "Family", "Group"])
accommodation = st.selectbox(
    "Accommodation preference",
    options=["Hotel", "Hostel", "Vacation rental", "Boutique hotel", "Eco-lodge"]
)
transportation = st.selectbox(
    "Transportation preference",
    options=["Public transit", "Rental car", "Walking", "Cycling", "Taxi"]
)
dining = st.selectbox(
    "Dining preference",
    options=["Street food", "Casual dining", "Fine dining", "Local cuisine", "International cuisine"]
)
pace = st.radio("Pace of travel", options=["Relaxed", "Moderate", "Packed"])

# Special Requests Section
st.subheader("Special Requests")
special_requests = st.text_area("Any special requests or notes")

# Generate Itinerary Button
if st.button("Generate Itinerary"):
    if not destination:
        st.error("Please enter a destination.")
    elif num_days < 1:
        st.error("Number of days must be at least 1.")
    elif budget <= 0:
        st.error("Budget must be greater than 0.")
    else:
        with st.spinner("Generating itinerary..."):
            # Construct the prompt
            interests_str = ', '.join(interests) if interests else "various activities"
            prompt = ( f"Create a {num_days}-day itinerary for {destination} with a budget of ${budget}. " 
            f"The traveler is a {companions.lower()} who is interested in {interests_str}. " 
            f"They prefer {accommodation.lower()} for accommodations, {transportation.lower()} for transportation, " 
            f"and {dining.lower()} for dining. The overall pace should be {pace.lower()}. " 
            f"Special requests: {special_requests if special_requests else 'None'}. " 
            "Please generate the itinerary in the following format:\n\n" 
            "Day 1 (Place):\n" 
            "\n Morning: \n" 
            " Afternoon: \n" 
            " Evening: \n\n"
            f"At the end of each activity or day, display the user estimated cost for that particular activity in INR rupees."
            )

            # Call Groq API
            api_key = st.secrets["api_key"]
            headers = {"Authorization": f"Bearer {api_key}"}
            data = {
                "model": "mixtral-8x7b-32768",  # Example Groq model name; replace with the correct one
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
            }
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)

            if response.status_code == 200:
                itinerary = response.json()["choices"][0]["message"]["content"]
                st.subheader("Your Custom Itinerary")
                st.markdown(itinerary)
            elif response.status_code == 401:
                st.error("Authentication failed. Please check your API key.")
            elif response.status_code == 400:
                st.error("Bad request. Check your input or request format.")
            elif response.status_code == 404:
                st.error("API endpoint not found. Verify the URL.")
            else:
                st.error(f"Failed to generate itinerary. Error: {response.status_code}")