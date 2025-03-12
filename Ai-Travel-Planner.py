import streamlit as st
import requests
import json
import re
import urllib3
import markdown2
import pdfkit
from prompt import get_prompt_preference, get_prompt_cost

# Disable insecure HTTPS request warnings (short-term workaround)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set background image
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://img.freepik.com/free-photo/abstract-luxury-soft-red-background-christmas-valentines-layout-design-studio-room-web-template-business-report-with-smooth-circle-gradient-color_1258-63949.jpg?t=st=1741764479~exp=1741768079~hmac=0fc1a9cb3fdd74202cdec1f891a55e27a589ec0941bf8540875b9a04659e9d15&w=1480");
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Predefined dictionaries for additional prompt guidance
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
    "Taxi": "Allow for quick, convenient transport.",
    "Public transit": "Use buses, trains, or subways where possible.",
    "Car rental": "Plan for driving routes and parking."
}
dining_guidance = {
    "Street food": "Highlight affordable, local street vendors.",
    "Casual dining": "Suggest relaxed, mid-range eateries.",
    "Fine dining": "Recommend upscale restaurants with reservations.",
    "Local cuisine": "Focus on authentic regional dishes.",
    "International cuisine": "Include globally inspired options."
}

# -------------------------------
# Step 1: Travel Cost Estimator
# -------------------------------
st.title("Travel Planner")

## Trip Details Section
st.subheader("Trip Details")
destination = st.text_input(
    "Destination",
    placeholder="e.g., Paris, France",
    help="Enter a specific city or location."
)
num_days = st.number_input("Number of days", min_value=1, step=1)
travel_month = st.selectbox("Travel month", options=[
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
])

## Budget Section
st.subheader("Budget (INR)")
total_budget = st.number_input("Total budget", min_value=0.0, step=500.0)
st.write(f"**Total Budget:** ₹{total_budget}")
st.write("All costs will be estimated in INR.")

# Automatically generate cost estimates after receiving inputs
if destination and any(char.isalpha() for char in destination) and num_days >= 1 and total_budget > 0:
    if 'cost_estimates_generated' not in st.session_state:
        st.session_state['destination'] = destination
        st.session_state['num_days'] = num_days
        st.session_state['travel_month'] = travel_month
        st.session_state['total_budget'] = total_budget

        with st.spinner("Fetching cost estimates..."):
            prompt = get_prompt_cost(
                destination=destination,
                num_days=num_days,
                travel_month=travel_month,
                total_budget=total_budget
            )
            api_key = st.secrets["api_key"]
            headers = {"Authorization": f"Bearer {api_key}"}
            data = {
                "model": "qwen-2.5-32b",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 1.0,
            }
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                verify=False  # Temporary workaround for SSL issues
            )
            if response.status_code == 200:
                raw_response = response.json()["choices"][0]["message"]["content"]
                try:
                    json_start = raw_response.find('{')
                    json_end = raw_response.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = raw_response[json_start:json_end]
                        estimates_dict = json.loads(json_str)
                        st.session_state.estimates = estimates_dict
                        st.session_state['cost_estimates_generated'] = True
                        st.success("Cost estimates generated and stored successfully!")
                    else:
                        st.error("No JSON object found in the response.")
                except json.JSONDecodeError:
                    st.error("Failed to parse estimates. The extracted response is not valid JSON.")
            else:
                st.error(f"Failed to fetch estimates. Status Code: {response.status_code}, Response: {response.text}")

# -------------------------------
# Step 2: Itinerary Preferences
# -------------------------------
st.subheader("Preferences")

## Interests
interests = st.multiselect(
    "Select your interests",
    options=["Art", "History", "Food", "Adventure", "Relaxation", "Culture", "Shopping"],
    key="itinerary_interests"
)
interest_ratings = {}
if interests:
    for interest in interests:
        interest_ratings[interest] = st.slider(f"Importance of {interest}", 1, 5, 3, key=f"slider_{interest}")
    interests_str = ', '.join([f"{k} (rated {v}/5)" for k, v in interest_ratings.items()])
else:
    interests_str = ""
    st.error("Please select at least one interest.")

## Travel Companions
companions_itinerary = st.radio("Travel companions", options=["Solo", "Couple", "Family", "Group"], key="itinerary_companions")
child_ages = ""
if companions_itinerary == "Family":
    child_ages = st.text_input(
        "Children's Ages (comma-separated)",
        placeholder="e.g., 5, 8, 12",
        help="Enter ages of children traveling",
        key="itinerary_child_ages"
    )

## Accommodation Options (Dynamic with Estimates)
accommodation_options = []
if "estimates" in st.session_state and "accommodation" in st.session_state.estimates:
    accom_estimates = st.session_state.estimates["accommodation"]
    for key, value in accom_estimates.items():
        if isinstance(value, dict):
            cost_info = value.get("cost", {})
            min_cost = cost_info.get("min", "")
            max_cost = cost_info.get("max", "")
            unit = value.get("unit", "")
        else:
            min_cost = max_cost = value
            unit = ""
        option_str = f"{key.capitalize()} - ₹{min_cost} to ₹{max_cost} {unit}"
        accommodation_options.append(option_str)
else:
    accommodation_options = ["Hotel", "Hostel", "Vacation rental", "Boutique hotel", "Eco-lodge"]

accommodation = st.selectbox(
    "Accommodation preference",
    options=accommodation_options,
    key="itinerary_accommodation"
)

## Transportation Options (Dynamic with Estimates)
transport_options = []
if "estimates" in st.session_state and "transportation" in st.session_state.estimates:
    trans_estimates = st.session_state.estimates["transportation"]
    for key, value in trans_estimates.items():
        if isinstance(value, dict):
            cost_info = value.get("cost", {})
            min_cost = cost_info.get("min", "")
            max_cost = cost_info.get("max", "")
            unit = value.get("unit", "")
        else:
            min_cost = max_cost = value
            unit = ""
        option_str = f"{key.capitalize()} - ₹{min_cost} to ₹{max_cost} {unit}"
        transport_options.append(option_str)
else:
    transport_options = ["Taxi", "Public transit", "Car rental"]

transportation = st.selectbox(
    "Transportation preference",
    options=transport_options,
    key="itinerary_transportation"
)
normalized_transport = transportation.split(" -")[0]  # Normalize for guidance lookup

## Dining Options (Dynamic with Estimates)
dining_options = []
if "estimates" in st.session_state and "dining" in st.session_state.estimates:
    dining_estimates = st.session_state.estimates["dining"]
    for key, value in dining_estimates.items():
        if isinstance(value, dict):
            cost_info = value.get("cost", {})
            min_cost = cost_info.get("min", "")
            max_cost = cost_info.get("max", "")
            unit = value.get("unit", "")
        else:
            min_cost = max_cost = value
            unit = ""
        option_str = f"{key.capitalize()} - ₹{min_cost} to ₹{max_cost} {unit}"
        dining_options.append(option_str)
else:
    dining_options = ["Street food", "Casual dining", "Fine dining", "Local cuisine", "International cuisine"]

dining = st.selectbox(
    "Dining preference",
    options=dining_options,
    key="itinerary_dining"
)

## Pace of Travel
pace = st.radio("Pace of travel", options=["Relaxed", "Moderate", "Packed"], key="itinerary_pace")

## Special Requests and Constraints
special_requests = st.text_area(
    "Any special requests or notes",
    placeholder="e.g., 'I prefer vegetarian options' or 'Need quiet areas'",
    help="Include anything specific to tailor your trip.",
    key="itinerary_special_requests"
)
dietary_restrictions = st.text_input("Dietary restrictions (e.g., vegetarian, gluten-free)", key="itinerary_dietary")
accessibility_needs = st.text_input("Accessibility needs (e.g., wheelchair access)", key="itinerary_accessibility")
nationality = st.text_input("Nationality (for visa considerations)", value="Indian", key="itinerary_nationality")

## Generate Itinerary
if st.button("Generate Itinerary"):
    if not interests:
        st.error("Please select at least one interest.")
    else:
        # Retrieve stored details from Step 1
        dest = st.session_state.get('destination', None)
        days = st.session_state.get('num_days', None)
        travel_month_value = st.session_state.get('travel_month', None)
        total_budget_value = st.session_state.get('total_budget', None)
        
        if not dest or not days or not total_budget_value or not travel_month_value:
            st.error("Missing key travel details from the first form. Please complete the cost estimation section first.")
        else:
            with st.spinner("Generating your personalized itinerary..."):
                # Construct prompt with all preferences
                prompt = get_prompt_preference(
                    num_days=days,
                    destination=dest,
                    total_budget=total_budget_value,
                    companions=companions_itinerary,
                    interests_str=interests_str,
                    child_ages=child_ages if companions_itinerary == 'Family' and child_ages else None,
                    accommodation=accommodation,
                    transportation=normalized_transport,
                    dining=dining,
                    pace=pace,
                    special_requests=special_requests,
                    dietary_restrictions=dietary_restrictions,
                    accessibility_needs=accessibility_needs,
                    nationality=nationality,
                    travel_month=travel_month_value,
                    pace_definitions=pace_definitions,
                    companion_guidance=companion_guidance,
                    transportation_guidance=transportation_guidance,
                    dining_guidance=dining_guidance,
                )

                api_key = st.secrets["api_key"]
                headers = {"Authorization": f"Bearer {api_key}"}
                data = {
                    "model": "qwen-2.5-32b",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 1.0,
                }
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                if response.status_code == 200:
                    itinerary = response.json()["choices"][0]["message"]["content"]
                    st.subheader("Your Custom Itinerary")

                    ### Display Itinerary with Day Expanders
                    if not re.search(r'^Day \d+:', itinerary, flags=re.MULTILINE):
                        st.markdown(itinerary)
                    else:
                        split_result = re.split(r'^(Day \d+):', itinerary, flags=re.MULTILINE)
                        if split_result[0].strip():
                            st.markdown(split_result[0].strip())
                        for i in range(1, len(split_result), 2):
                            day_header = split_result[i].strip()
                            day_content = split_result[i+1].strip()
                            with st.expander(day_header):
                                st.markdown(day_content)

                    ### Generate PDF
                    # Preprocess for Markdown headers
                    itinerary_md = re.sub(r'^Day (\d+):', r'## Day \1:', itinerary, flags=re.MULTILINE)
                    # Convert to HTML
                    html_body = markdown2.markdown(itinerary_md, extras=["fenced-code-blocks", "tables"])
                    # Construct HTML with Google Fonts and meta charset
                    html_content = f"""
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <link href="https://fonts.googleapis.com/css2?family=Open+Sans&display=swap" rel="stylesheet">
                        <style>
                            body {{
                                font-family: 'Open Sans', sans-serif;
                            }}
                            table {{
                                width: 100%;
                                border-collapse: collapse;
                            }}
                            th, td {{
                                border: 1px solid #ddd;
                                padding: 8px;
                                text-align: left;
                            }}
                            th {{
                                background-color: #f2f2f2;
                            }}
                        </style>
                    </head>
                    <body>
                        {html_body}
                    </body>
                    </html>
                    """

                    # Generate PDF with encoding option
                    pdf_output = pdfkit.from_string(html_content, False, options={'encoding': 'UTF-8'})

                    st.download_button(
                        label="Download Itinerary as PDF",
                        data=pdf_output,
                        file_name="itinerary.pdf",
                        mime="application/pdf"
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