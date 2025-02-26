import streamlit as st
import requests
import re

# Predefined dictionaries for prompt guidance
pace_definitions = {
    "Relaxed": "a leisurely pace with ample downtime",
    "Moderate": "a balanced pace with a mix of activities and rest",
    "Packed": "a fast-paced schedule with many activities"
}
companion_guidance = {
    "Solo": "Focus on independent exploration and flexibility.",
    "Couple": "Include romantic or paired activities where suitable.",
    "Family": "Prioritize family-friendly activities and convenience.",
    "Group": "Emphasize group-friendly activities and coordination."
}
transportation_guidance = {
    "Public transit": "Use buses, trains, or subways where possible.",
    "Rental car": "Plan for driving routes and parking.",
    "Walking": "Keep distances short and walkable.",
    "Cycling": "Include bike-friendly routes or rentals.",
    "Taxi": "Allow for quick, convenient transport."
}
dining_guidance = {
    "Street food": "Highlight affordable, local street vendors.",
    "Casual dining": "Suggest relaxed, mid-range eateries.",
    "Fine dining": "Recommend upscale restaurants with reservations.",
    "Local cuisine": "Focus on authentic regional dishes.",
    "International cuisine": "Include globally inspired options."
}

# Set up the Streamlit app
st.title("Custom Itinerary Generator")

# Trip Details Section
st.subheader("Trip Details")
destination = st.text_input(
    "Destination", 
    placeholder="e.g., Paris, France", 
    help="Enter a specific city or location."
)
num_days = st.number_input("Number of days", min_value=1, step=1)
st.subheader("Budget Breakdown (INR)")
accom_budget = st.number_input("Accommodation budget", min_value=0.0, step=500.0)
activity_budget = st.number_input("Activities budget", min_value=0.0, step=500.0)
dining_budget = st.number_input("Dining budget", min_value=0.0, step=500.0)
transport_budget = st.number_input("Transportation budget", min_value=0.0, step=500.0)
total_budget = accom_budget + activity_budget + dining_budget + transport_budget
st.write(f"**Total Budget:** ₹{total_budget}")
st.write("All costs will be converted to INR using current exchange rates.")
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
interest_ratings = {}
if interests:
    for interest in interests:
        interest_ratings[interest] = st.slider(f"Importance of {interest}", 1, 5, 3)
    interests_str = ', '.join([f"{k} (rated {v}/5)" for k, v in interest_ratings.items()])
else:
    st.error("Please select at least one interest.")
companions = st.radio("Travel companions", options=["Solo", "Couple", "Family", "Group"])
if companions == "Family":
    child_ages = st.text_input(
        "Ages of children (e.g., 5, 8, 12)", 
        help="Enter ages separated by commas"
    )
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
    placeholder="e.g., 'I prefer vegetarian options' or 'Need quiet areas'",
    help="Include anything specific to tailor your trip."
)

# User Constraints
st.subheader("User Constraints")
dietary_restrictions = st.text_input("Dietary restrictions (e.g., vegetarian, gluten-free)")
accessibility_needs = st.text_input("Accessibility needs (e.g., wheelchair access)")
nationality = st.text_input("Nationality (for visa considerations)", value="Indian")

# Generate Itinerary Button
if st.button("Generate Itinerary"):
    # Input Validation
    if not destination:
        st.error("Please enter a destination.")
    elif not any(char.isalpha() for char in destination):
        st.error("Destination must contain letters.")
    elif num_days < 1:
        st.error("Number of days must be at least 1.")
    elif total_budget <= 0:
        st.error("Total budget must be greater than 0.")
    elif not interests:
        st.error("Please select at least one interest.")
    else:
        with st.spinner("Generating your personalized itinerary... (this may take a few seconds)"):
            # Construct the prompt
            prompt = f"""
Create a {num_days}-day itinerary for {destination} with a total budget of ₹{total_budget}. 
The traveler is a {companions.lower()} who prioritizes interests as follows: {interests_str}. 
{'For family travelers, include activities suitable for children aged ' + child_ages + '.' if companions == 'Family' and child_ages else ''}
They prefer {accommodation.lower()} for accommodations, {transportation.lower()} for transportation, and {dining.lower()} for dining. 
The overall pace should be {pace.lower()}, meaning {pace_definitions[pace]}.

**Budget Allocation:**
- Accommodation: ₹{accom_budget}
- Activities: ₹{activity_budget}
- Dining: ₹{dining_budget}
- Transportation: ₹{transport_budget}

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
  - When referencing specific places, destinations, museums, restaurants, or activities, output the place name as a clickable Markdown hyperlink. Use this format: 
    [Place Name](https://www.google.com/maps/search/?api=1&query=Activity+Name+at+Location+Name).
- At the end of each day, provide a total estimated cost for that day in INR.

**Cultural Notes:**
- Briefly explain any local terms, cuisines, or customs that may be unfamiliar to Indian travelers. 
  For example, if mentioning 'Gelato' in Italy, note: '(Gelato is a creamy Italian frozen dessert similar to ice cream but richer in texture).'
- Integrate these explanations naturally within the activity descriptions.

**Budget Instructions:**
- Ensure the total cost (accommodation, activities, dining, and transportation) does not exceed ₹{total_budget}.
- Allocate the budget across all categories as specified and convert all costs to INR using up-to-date exchange rates.
- Itemize costs for each activity and provide a daily total.

**Summary Section:**
- At the end of the itinerary, include a summary table in markdown breaking down the total estimated cost by category (e.g., accommodation, activities, dining, transportation) to confirm it stays within ₹{total_budget}.

**Additional Notes:**
- Strictly adhere to dietary restrictions ({dietary_restrictions}), accessibility needs ({accessibility_needs}), and special requests ({special_requests}).
- Since travel is in {travel_month}, include seasonal activities or events, e.g., festivals or weather-specific options.

**Personalized Tips:**
- Since you’re interested in {interests_str}, try these local experiences: [list 2-3 suggestions].

**Weather Information:**
- For {travel_month} in {destination}, expect average temperatures of X°C and [weather condition]. Pack accordingly!
"""

            # Call Groq API (replace with your API key and endpoint)
            api_key = st.secrets["api_key"]  # Ensure API key is stored in Streamlit secrets
            headers = {"Authorization": f"Bearer {api_key}"}
            data = {
                "model": "qwen-2.5-32b",  # Replace with the correct Groq model name
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 1.0,
            }
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions", 
                headers=headers, 
                json=data
            )

            # Handle API Response
            if response.status_code == 200:
                itinerary = response.json()["choices"][0]["message"]["content"]
                st.subheader("Your Custom Itinerary")
                
                # Handle the first section separately if it doesn't start with a 'Day' header
                if not itinerary.startswith('Day'):
                    first_section, *days = re.split(r'^Day \d+:', itinerary, flags=re.MULTILINE)
                    if first_section.strip():
                        st.markdown(first_section.strip())
                else:
                    days = re.split(r'^Day \d+:', itinerary, flags=re.MULTILINE)

                for day in days:
                    if day.strip():  # Check if the day section is not empty
                        lines = day.splitlines()
                        day_header = lines[0].strip()  # e.g., "Day 1:"
                        day_content = "\n".join(lines[1:]).strip()  # Content after the header
                        with st.expander(f"Day {day_header}"):
                            st.markdown(day_content)
                
                st.download_button(
                    "Download Itinerary",
                    itinerary,
                    file_name=f"{destination}_itinerary.md",
                    mime="text/markdown"
                )
                st.warning(
                    "The generated itinerary is based on AI suggestions and may not reflect real-time availability or accuracy. "
                    "Please verify details before booking."
                )
            else:
                error_messages = {
                    401: "Authentication failed. Please check your API key.",
                    400: f"Bad request: {response.json().get('error', 'Invalid input')}",
                    404: "API endpoint not found. Verify the URL.",
                }
                st.error(
                    error_messages.get(
                        response.status_code, 
                        f"Failed to generate itinerary. Error {response.status_code}: {response.json().get('error', 'Unknown issue')}. "
                        "Try again or adjust your inputs."
                    )
                )
