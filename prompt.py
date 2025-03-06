def get_prompt_preference(num_days, destination, total_budget, companions, interests_str, child_ages, accommodation, transportation, dining, pace, special_requests, dietary_restrictions, accessibility_needs, nationality, travel_month, pace_definitions, companion_guidance, transportation_guidance, dining_guidance):
    return f"""
            Create a {num_days}-day itinerary for {destination} with a total budget of ₹{total_budget}. 
            The traveler is a {companions.lower()} who prioritizes interests as follows: {interests_str}. 
            {'For family travelers, include activities suitable for children aged ' + child_ages + '.' if companions == 'Family' and child_ages else ''}
            They prefer {accommodation.lower()} for accommodations, {transportation.lower()} for transportation, and {dining.lower()} for dining. 
            The overall pace should be {pace.lower()}, meaning {pace_definitions.get(pace, 'a balanced pace')}. 

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
            - For companions: {companion_guidance.get(companions, '')}
            - For transportation: {transportation_guidance.get(transportation, '')}
            - For dining: {dining_guidance.get(dining, '')}

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

def get_prompt_cost(destination, num_days, travel_month ,total_budget):
    return f"""
            Based on a trip to {destination} for {num_days} days in {travel_month},,
            and a total budget of ₹{total_budget} INR,
            provide detailed cost estimates in INR for accommodation, dining, and transportation.
            For accommodation, provide estimates for the following types: Hotel, Hostel, Vacation rental, Boutique hotel, and Eco-lodge.
            For dining, provide estimates for the following types: Street food, Casual dining, Fine dining, Local cuisine, and International cuisine.
            For transportation, provide estimates for the following types: Taxi, Public transit, and Car rental.
            Provide average cost ranges rather than absolute values.
            Respond with a JSON object having the structure:
            {{
                "accommodation": {{
                    "hotel": {{"cost": {{"min": 2500, "max": 3000}}, "unit": "per night"}},
                    "hostel": {{"cost": {{"min": 800, "max": 1200}}, "unit": "per night"}},
                    "vacation rental": {{"cost": {{"min": 1500, "max": 2500}}, "unit": "per night"}},
                    "boutique hotel": {{"cost": {{"min": 3000, "max": 5000}}, "unit": "per night"}},
                    "eco-lodge": {{"cost": {{"min": 2000, "max": 3500}}, "unit": "per night"}}
                }},
                "dining": {{
                    "street food": {{"cost": {{"min": 100, "max": 200}}, "unit": "per meal"}},
                    "casual dining": {{"cost": {{"min": 500, "max": 800}}, "unit": "per meal"}},
                    "fine dining": {{"cost": {{"min": 1000, "max": 2000}}, "unit": "per meal"}},
                    "local cuisine": {{"cost": {{"min": 300, "max": 600}}, "unit": "per meal"}},
                    "international cuisine": {{"cost": {{"min": 800, "max": 1500}}, "unit": "per meal"}}
                }},
                "transportation": {{
                    "taxi": {{"cost": {{"min": 4, "max": 5}}, "unit": "per km"}},
                    "public transit": {{"cost": {{"min": 50, "max": 100}}, "unit": "per trip"}},
                    "car rental": {{"cost": {{"min": 800, "max": 1500}}, "unit": "per day"}}
                }}
            }}
            Ensure 'cost' values are numeric (in INR) and 'unit' values are strings.
    """
