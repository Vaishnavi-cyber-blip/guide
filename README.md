# AI based City specific Tour guide for Trip Bharat
This Flask-based backend powers the Trip Bharat app, enabling a city-specific chatbot feature to assist users with personalized travel guidance in Indian cities. It integrates an external API for city verification and uses LLM (llama3-70b-8192) for generating AI-based chat responses.

## Key Features
**City Verification:**  
The backend ensures that the queried city is located in India using the countriesnow.space API, which retrieves a list of Indian cities.  

**Local Travel Guide:**
The chatbot acts as a friendly local tour guide, offering city-specific recommendations and answering user queries.

**AI-Powered Chat:**
The backend integrates Groq's AI model (llama3-70b-8192) to generate context-aware and personalized chat responses.

**Dynamic System Prompt:**
The chatbot uses a dynamic system prompt to adapt its responses based on the city name, enhancing the user experience with city-specific information.

## How it Works
### 1. Chat Endpoint (/chat):
- Receives user input (message) and the selected city name (cityName) via a POST request.
- Verifies if the city is in India by calling an external API.
- If valid, initializes a system prompt and appends user input to the chat history.
- Sends the chat history to Groq's AI API for generating a response.
- 
### 2. City Validation:
- Calls the countriesnow.space API to retrieve a list of Indian cities.
- Compares the queried city with the list, ignoring case sensitivity.

### 3. AI Chat Response:  
- Generates responses using the Groq API with parameters such as model, max_tokens, and temperature for fine-tuning outputs.
- Appends the AI's response to the chat history and returns it to the frontend.
  



![Screenshot 2024-07-24 133250](https://github.com/user-attachments/assets/999de503-eb45-42e7-8224-73cfcea50597)






