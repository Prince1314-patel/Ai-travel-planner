"""Prompt templates and guidance tables for the Groq itinerary/cost-estimate calls.

Ported from the original Streamlit app's prompt.py and Ai-Travel-Planner.py, unchanged
in substance — only the call site (FastAPI instead of Streamlit) is new.
"""

PACE_DEFINITIONS = {
    "Relaxed": "a leisurely pace with ample downtime",
    "Moderate": "a balanced pace with a mix of activities and rest",
    "Packed": "a fast-paced schedule with many activities",
}

COMPANION_GUIDANCE = {
    "Solo": "Focus on independent exploration and flexibility.",
    "Couple": "Include romantic or paired activities where suitable.",
    "Family": "Prioritize family-friendly activities and convenience.",
    "Group": "Emphasize group-friendly activities and coordination.",
}

TRANSPORTATION_GUIDANCE = {
    "Taxi": "Allow for quick, convenient transport.",
    "Public transit": "Use buses, trains, or subways where possible.",
    "Car rental": "Plan for driving routes and parking.",
}

DINING_GUIDANCE = {
    "Street food": "Highlight affordable, local street vendors.",
    "Casual dining": "Suggest relaxed, mid-range eateries.",
    "Fine dining": "Recommend upscale restaurants with reservations.",
    "Local cuisine": "Focus on authentic regional dishes.",
    "International cuisine": "Include globally inspired options.",
}


def get_prompt_preference(
    num_days,
    destination,
    total_budget,
    companions,
    interests_str,
    child_ages,
    accommodation,
    transportation,
    dining,
    pace,
    special_requests,
    dietary_restrictions,
    accessibility_needs,
    nationality,
    travel_month,
):
    return f"""
            Create a {num_days}-day itinerary for {destination} with a total budget of ₹{total_budget}.
            The traveler is a {companions.lower()} who prioritizes interests as follows: {interests_str}.
            {'For family travelers, include activities suitable for children aged ' + child_ages + '.' if companions == 'Family' and child_ages else ''}
            They prefer {accommodation.lower()} for accommodations, {transportation.lower()} for transportation, and {dining.lower()} for dining.
            The overall pace should be {pace.lower()}, meaning {PACE_DEFINITIONS.get(pace, 'a balanced pace')}.

            **Budget Allocation:**
            - Accommodation: ₹{total_budget}
            - Activities: ₹{total_budget}
            - Dining: ₹{total_budget}
            - Transportation: ₹{total_budget}

            **Traveler Details:**
            - Special requests: {special_requests if special_requests else 'None'}
            - Dietary restrictions: {dietary_restrictions if dietary_restrictions else 'None'}
            - Accessibility needs: {accessibility_needs if accessibility_needs else 'None'}
            - Nationality: {nationality if nationality else 'None'}
            - Travel month: {travel_month} (prioritize activities suitable for this season)

            **Guidance:**
            - For companions: {COMPANION_GUIDANCE.get(companions, '')}
            - For transportation: {TRANSPORTATION_GUIDANCE.get(transportation, '')}
            - For dining: {DINING_GUIDANCE.get(dining, '')}

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
            - Since you're interested in {interests_str}, try these local experiences: [list 2-3 suggestions].

            **Weather Information:**
            - For {travel_month} in {destination}, expect average temperatures of X°C and [weather condition]. Pack accordingly!
    """


def get_prompt_cost(destination, num_days, travel_month, total_budget, price_context=None):
    price_context = price_context or {}
    grounding_lines = [
        f"- {category.capitalize()} > {subcategory}: {answer}"
        for category, subcategories in price_context.items()
        for subcategory, answer in subcategories.items()
        if answer
    ]
    grounding_block = (
        "\n            **Live web search results for this exact destination and month "
        "— one real result per line item below. Use these as your values directly "
        "(convert to an INR min/max range); do not substitute your own estimate "
        "where a real result is given. Only reason from general knowledge for any "
        "line item with no result listed here:**\n" + "\n".join(grounding_lines) + "\n"
        if grounding_lines
        else ""
    )

    return f"""
            Based on a trip to {destination} for {num_days} days in {travel_month}, with a total budget of ₹{total_budget} INR, provide a detailed breakdown of estimated costs for accommodation, dining, and transportation.
            {grounding_block}
            Requirements:
            - Provide cost estimates in INR (Indian Rupees) using average cost ranges rather than absolute values. Convert non-INR figures to INR.
            - Reason about {destination} specifically — a budget city and a major capital do not share pricing, and neither should your answer.
            - Structure the response as a JSON object with the following categories:
                - Accommodation: Include cost estimates for Hotel, Hostel, Vacation rental, Boutique hotel, and Eco-lodge (cost per night).
                - Dining: Include cost estimates for Street food, Casual dining, Fine dining, Local cuisine, and International cuisine (cost per meal).
                - Transportation: Include cost estimates for Taxi, Public transit, and Car rental (cost per km, per trip, or per day as applicable).
            - Ensure that 'cost' values are numeric (in INR) and 'unit' values are strings.
            Respond with a JSON object having exactly this shape (the numbers below are placeholders showing the required format only — do not reuse them, compute real destination-specific values):
            {{
                "accommodation": {{
                    "hotel": {{"cost": {{"min": "<number>", "max": "<number>"}}, "unit": "per night"}},
                    "hostel": {{"cost": {{"min": "<number>", "max": "<number>"}}, "unit": "per night"}},
                    "vacation rental": {{"cost": {{"min": "<number>", "max": "<number>"}}, "unit": "per night"}},
                    "boutique hotel": {{"cost": {{"min": "<number>", "max": "<number>"}}, "unit": "per night"}},
                    "eco-lodge": {{"cost": {{"min": "<number>", "max": "<number>"}}, "unit": "per night"}}
                }},
                "dining": {{
                    "street food": {{"cost": {{"min": "<number>", "max": "<number>"}}, "unit": "per meal"}},
                    "casual dining": {{"cost": {{"min": "<number>", "max": "<number>"}}, "unit": "per meal"}},
                    "fine dining": {{"cost": {{"min": "<number>", "max": "<number>"}}, "unit": "per meal"}},
                    "local cuisine": {{"cost": {{"min": "<number>", "max": "<number>"}}, "unit": "per meal"}},
                    "international cuisine": {{"cost": {{"min": "<number>", "max": "<number>"}}, "unit": "per meal"}}
                }},
                "transportation": {{
                    "taxi": {{"cost": {{"min": "<number>", "max": "<number>"}}, "unit": "per km"}},
                    "public transit": {{"cost": {{"min": "<number>", "max": "<number>"}}, "unit": "per trip"}},
                    "car rental": {{"cost": {{"min": "<number>", "max": "<number>"}}, "unit": "per day"}}
                }}
            }}
            The placeholders above ("<number>") must be replaced with real numeric values (no quotes) in your response. Ensure 'cost' values are numeric (in INR) and 'unit' values are strings.
            """
