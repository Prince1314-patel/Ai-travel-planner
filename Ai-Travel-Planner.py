import streamlit as st
import requests

# Set up the Streamlit app
st.title("Custom Itinerary Generator")

# Trip Details Section
st.subheader("Trip Details")
destination = st.text_input("Destination")
num_days = st.number_input("Number of days", min_value=1, step=1)
budget = st.number_input("Budget (INR)", min_value=0.0, step=1000.0)
travel_month = st.selectbox("Travel month", options=[
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
])

# Preferences Section
st.subheader("Preferences")
interests = st.multiselect(
    "Interests",
    options=["Art", "History", "Food", "Adventure", "Relaxation", "Culture", "Shopping"]
)
if not interests:
    st.error("Please select at least one interest.")
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
special_requests = st.text_area(
    "Any special requests or notes",
    help="E.g., 'I need wheelchair-accessible activities' or 'I prefer vegetarian dining options'"
)

# User Constraints
st.subheader("User Constraints")
dietary_restrictions = st.text_input("Dietary restrictions (e.g., vegetarian, gluten-free)")
accessibility_needs = st.text_input("Accessibility needs (e.g., wheelchair access)")
nationality = st.text_input("Nationality (for visa considerations)")

# Generate Itinerary Button
if st.button("Generate Itinerary"):
    if not destination:
        st.error("Please enter a destination.")
    elif num_days < 1:
        st.error("Number of days must be at least 1.")
    elif budget <= 0:
        st.error("Budget must be greater than 0.")
    elif not interests:
        st.error("Please select at least one interest.")
    elif len(destination.split()) > 1:  # Simple check for destination specificity
        st.error("Please enter a specific city or location.")
    else:
        with st.spinner("Generating itinerary..."):
            # Construct the prompt with solutions
            interests_str = ', '.join(interests)
            companion_guidance = {
                "Solo": "Prioritize independent and flexible activities.",
                "Couple": "Include romantic and couple-friendly activities.",
                "Family": "Focus on family-friendly and kid-friendly activities.",
                "Group": "Include group-friendly activities and discounts."
            }
            pace_definitions = {
                "Relaxed": "1-2 activities per day",
                "Moderate": "3-4 activities per day",
                "Packed": "5+ activities per day"
            }
            transportation_guidance = {
                "Walking": "Ensure activities are within a 2 km radius.",
                "Public transit": "Ensure activities are accessible via public transit.",
                "Rental car": "Activities can be spread out, assuming car availability.",
                "Cycling": "Ensure activities are within a 5 km radius.",
                "Taxi": "Activities can be spread out, assuming taxi availability."
            }
            dining_guidance = {
                "Street food": "Include street food options for dining.",
                "Casual dining": "Include casual dining restaurants.",
                "Fine dining": "Include fine dining restaurants.",
                "Local cuisine": "Include restaurants featuring local cuisine.",
                "International cuisine": "Include restaurants featuring international cuisine."
            }
            prompt = f"""
                        Create a {num_days}-day itinerary for {destination} with a budget of ₹{budget}. 
                        The traveler is a {companions.lower()} who is interested in {interests_str}. They prefer {accommodation.lower()} for accommodations, 
                        {transportation.lower()} for transportation, and {dining.lower()} for dining. The overall pace should be {pace.lower()}, 
                        meaning {pace_definitions[pace]}.

                        **Traveler Details:**
                        - Special requests: {special_requests if special_requests else 'None'}
                        - Dietary restrictions: {dietary_restrictions if dietary_restrictions else 'None'}
                        - Accessibility needs: {accessibility_needs if accessibility_needs else 'None'}
                        - Nationality: {nationality if nationality else 'None'}
                        - Travel month: {travel_month} (prioritize activities suitable for this season)

                        **Guidance:**
                        - For companions: {companion_guidance[companions]}
                        - For transportation: {transportation_guidance[transportation]}
                        - For dining: {dining_guidance[dining]}

                        **Itinerary Requirements:**
                        - Format the itinerary in markdown using ### for each day (e.g., ### Day 1) and #### for time slots (e.g., #### Morning, #### Afternoon, #### Evening).
                        - Use bullet points to list activities under each time slot.
                        - For each activity or dining option, include:
                        - A brief description (1-2 sentences).
                        - Estimated cost in INR (covering entrance fees and meals, excluding transportation costs).
                        - When referencing specific places, destinations, museums, restaurants, or activities, enclose their names in double asterisks (e.g., **Place Name**).
                        - Don't provide the whole link to the user, just make the 'place' a href link that will take the user to the Google Maps search page for that location.
                        - When referencing specific places, destinations, museums, restaurants, or activities, output the place name as a clickable Markdown hyperlink. Use this format: 
                            [Place Name](https://www.google.com/maps/search/?api=1&query=Activity+Name+at+Location+Name). Replace 'Activity Name' and 'Location Name' with 
                            the appropriate values. For example, if the activity is 'Eiffel Tower' and the location is 'Paris', the output should be: 
                            [Eiffel Tower](https://www.google.com/maps/search/?api=1&query=Eiffel+Tower+at+Paris)."

                        
                        - At the end of each day, provide a total estimated cost for that day in INR.

                        **Cultural Notes:**
                        - Briefly explain any local terms, cuisines, or customs that may be unfamiliar to Indian travelers. For example, if mentioning 'Gelato' in Italy, note: '(Gelato is a creamy Italian frozen dessert similar to ice cream but richer in texture).'
                        - Integrate these explanations naturally within the activity descriptions.

                        **Budget Instructions:**
                        - Ensure the total cost (accommodation, activities, dining, and transportation) does not exceed ₹{budget}.
                        - Allocate the budget across all categories and convert all costs to INR using up-to-date exchange rates.
                        - Itemize costs for each activity and provide a daily total.

                        **Summary Section:**
                        - At the end of the itinerary, include a summary table in markdown breaking down the total estimated cost by category (e.g., accommodation, activities, dining, transportation) to confirm it stays within ₹{budget}.
                    """

            # Call Groq API
            api_key = st.secrets["api_key"]
            headers = {"Authorization": f"Bearer {api_key}"}
            data = {
                "model": "qwen-2.5-32b",  # Example Groq model name; replace with the correct one
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 1.0,
            }
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)

            if response.status_code == 200:
                itinerary = response.json()["choices"][0]["message"]["content"]
                st.subheader("Your Custom Itinerary")
                st.markdown(itinerary)
                st.warning("The generated itinerary is based on AI suggestions and may not reflect real-time availability or accuracy. Please verify details before booking.")
            elif response.status_code == 401:
                st.error("Authentication failed. Please check your API key.")
            elif response.status_code == 400:
                error_message = response.json().get("error", "Bad request")
                st.error(f"Bad request: {error_message}")
            elif response.status_code == 404:
                st.error("API endpoint not found. Verify the URL.")
            else:
                st.error(f"Failed to generate itinerary. Error: {response.status_code}")