# AI Travel Planner

An innovative AI-powered travel itinerary planner that dynamically generates personalized travel itineraries based on your destination, travel preferences, and budget. This application delivers a seamless, interactive, and visually appealing travel planning experience.

## Features

- **Dynamic Itinerary Generation:**  
  Generate personalized travel itineraries based on user inputs such as destination, number of days, budget, and interests.

- **Interactive UI:**  
  Enjoy a modern, responsive interface with custom CSS styling, bounding boxes for each day's plan, and engaging hover effects.

- **Customizable Interests:**  
  Select from predefined interests or add your own to tailor the itinerary to your unique preferences.

- **Secure API Integration:**  
  Securely integrates with the Groq API using environment variables, ensuring your API keys remain confidential.

- **Modern Design:**  
  Utilizes the Google Font "Quintessential" for an elegant look, paired with a travel-themed background for a captivating user experience.

## Demo

![Demo Screenshot]
Screenshot.png

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/ai-travel-planner.git
   cd ai-travel-planner
   ```

2. **Create a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**

   Create a `.env` file in the project root and add your Groq API key:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Running the App

Launch the app using Streamlit:

```bash
streamlit run app.py
```

Then open your web browser and navigate to [http://localhost:8501](http://localhost:8501) to view the app.

## Project Structure

```
ai-travel-planner/
│
├── app.py            # Main application file
├── requirements.txt  # List of dependencies
├── .env              # Environment variables (not tracked by Git)
├── README.md         # This file
└── assets/           # Directory for images and other assets
```

## Customization

- **Styling:**  
  Adjust the custom CSS in `app.py` to fine-tune the visual design, layout, and hover effects.

- **Itinerary Format:**  
  Modify the prompt within the `generate_itinerary` function to change the structure and format of the generated itinerary.

- **Interest Options:**  
  Update or expand the predefined interest options in the UI as per your use case.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements. For major changes, open an issue first to discuss your ideas.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions, suggestions, or issues, please open an issue on GitHub or contact [your email address].
```

Feel free to customize any sections as needed before uploading your project to GitHub.
