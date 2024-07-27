import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

groq_api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=groq_api_key)


CITIES_API_URL = "https://countriesnow.space/api/v0.1/countries/cities"

# Function to create the system prompt
def get_system_prompt(city_name):
    return {
        "role": "system",
        "content": f"You are the expert local tour guide of {city_name}. Be friendly and act as a travel companion by guiding the user."
    }

# Function to check if a city exists in India
def check_city_in_india(city_name):
    try:
        # Call the external API to get the list of cities in India
        response = requests.post(CITIES_API_URL, json={"country": "India"})
        if response.status_code == 200:
            cities_list = response.json().get("data", [])
            print("Cities retrieved successfully: ", cities_list)  # Debug print
            # Normalize city names to lowercase for comparison
            city_name_lower = city_name.lower()
            cities_list_lower = [city.lower() for city in cities_list]
            return city_name_lower in cities_list_lower
        else:
            print("Error retrieving cities list:", response.text)
            return False
    except requests.RequestException as e:
        print("Exception occurred while checking city:", e)
        return False

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("message")
    city_name = data.get("cityName")

    # Print city name for debugging
    print(f"Received city name: {city_name}")

    # Check if the city is in India
    if not check_city_in_india(city_name):
        return jsonify({
            "response": "City not found in India.",  # Update response to reflect check
            "history": []
        })

    chat_history = data.get("history", [])
    if len(chat_history) == 0:
        system_prompt = get_system_prompt(city_name)
        chat_history.append(system_prompt)
        # Print system prompt for debugging
        print(f"System prompt added: {system_prompt}")

    chat_history.append({"role": "user", "content": user_input})

    # Print the complete chat history for debugging
    print("Chat history before sending to model:")
    for message in chat_history:
        print(message)

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=chat_history,
            max_tokens=100,
            temperature=1.2
        )
    except Exception as e:
        print("Error communicating with Groq API:", e)
        return jsonify({
            "response": "Error processing your request.",
            "history": chat_history
        })

    # Check if the response is valid and contains expected content
    if response and response.choices and len(response.choices) > 0:
        assistant_content = response.choices[0].message.content
        chat_history.append({
            "role": "assistant",
            "content": assistant_content
        })

        # Print the response for debugging
        print("Assistant response:")
        print(assistant_content)

        return jsonify({
            "response": assistant_content,
            "history": chat_history
        })
    else:
        print("Invalid response from Groq API")
        return jsonify({
            "response": "Invalid response from assistant.",
            "history": chat_history
        })

if __name__ == '__main__':
    app.run(debug=True)
