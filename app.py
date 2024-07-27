# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from crewai import Agent, Task, Crew, Process
# from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
# from langchain_community.tools.tavily_search.tool import TavilySearchResults
# import sys
# import os
# import threading
# from crewai_tools import SerperDevTool
# import queue
# from langchain_groq import ChatGroq
# from dotenv import load_dotenv

# crew_result_store = {}

# app = Flask(__name__)
# CORS(app, )
# load_dotenv()

# groq_api_key = os.getenv("GROQ_API_KEY")
# tavily_api_key = os.getenv("TAVILY_API_KEY")
# serper_api_key = os.getenv("SERPER_API_KEY")
# llm = ChatGroq(api_key=groq_api_key, model="llama3-8b-8192")
# search = TavilySearchAPIWrapper(tavily_api_key=tavily_api_key)
# tavily_tool = TavilySearchResults(api_wrapper=search)
# tool = SerperDevTool(serper_api_key=serper_api_key)

# output_queue = queue.Queue()

# class StreamToQueue:
#     def __init__(self, queue):
#         self.queue = queue

#     def write(self, message):
#         self.queue.put(message)

#     def flush(self):
#         pass

# sys.stdout = StreamToQueue(output_queue)
# sys.stderr = StreamToQueue(output_queue)

# def create_crewai_setup(tripfrom, budget, days, tripto):
#     Travel_Agent = Agent(
#         role="Itinerary Planner",
#         goal=f"""Plan a detailed itinerary based on the factors like number of days, travelling from, travelling to, budget of trip.
#                 travelling from: {tripfrom}
#                 Budget: {budget}
#                 Number of Days: {days}
#                 Trip to: {tripto}

#                 Important:
#                     - Final output must contain all the detailed plan of the locations perfect for customs, culture 
#                     information, tourist attractions, activities, food a traveller can follow.
#                     - Avoid reusing the same input.""",
#         backstory=f"""Travel itinerary planner who has expertise in planning an itinerary for any place within India.""",
#         verbose=True,
#         allow_delegation=True,
#         tools=[tavily_tool, tool],
#         llm=llm,
#     )

#     city_insights = Agent(
#         role="Tour and travel agent",
#         goal=f"""Perform detailed research about {tripfrom} and {tripto} to provide the Itinerary planner 
#                 deep analysis of accommodation, transport, culture, and other insights of the place.

#             Important:
#                     - Once you know the selected city, provide keenly researched insights of the city.
#                     - Research local events, activities, food, transport, and accommodation information.
#                     - Keep the information detailed.
#                     - Avoid reusing the same input.""",
#         backstory=f"""A knowledgeable Tour and travel agent with extensive information 
#                     about every city of India, its attractions, customs, and always updated 
#                     about current events in the city.""",
#         verbose=True,
#         allow_delegation=True,
#         tools=[tavily_tool, tool],
#         llm=llm,
#     )

#     task1 = Task(
#         description=f"""Provide end to end detailed itinerary for each day to the traveller. 
            
#                 Helpful Tips:
#                 - To find blog articles and Google results, perform searches on Google such as the following:
#                 - "Plan a travel itinerary from {tripfrom} to {tripto} in India under {budget}."

#                 Important:
#                 - Do not generate fake information or improper budget breakdown. Only return the information you find. Nothing else!""",
#         expected_output="Detailed planned itinerary.",
#         agent=Travel_Agent,
#     )

#     travel_crew = Crew(
#         agents=[Travel_Agent, city_insights],
#         tasks=[task1],
#         verbose=2,
#         process=Process.sequential,
#     )

#     crew_result = travel_crew.kickoff()
#     crew_result_store[(tripfrom, days, budget, tripto)] = crew_result
#     return crew_result

# @app.route('/logs', methods=['GET'])
# def get_logs():
#     logs = []
#     while not output_queue.empty():
#         logs.append(output_queue.get())
#     return jsonify({'logs': logs})

# @app.route('/analyze', methods=['POST'])
# def analyze():
#     data = request.get_json()
#     tripfrom = data.get('tripfrom')
#     budget = data.get('budget')
#     days = data.get('days')
#     tripto = data.get('tripto')

#     if not (tripfrom and budget and days and tripto):
#         return jsonify({'error': 'There is a missing identity'}), 400

#     threading.Thread(target=create_crewai_setup, args=(tripfrom, budget, days, tripto)).start()
#     return jsonify({'status': 'Processing started'})

# @app.route('/crew_result', methods=['GET'])
# def get_crew_result():
#     tripfrom = request.args.get('tripfrom')
#     budget = request.args.get('budget')
#     days = request.args.get('days')
#     tripto = request.args.get('tripto')

#     key = (tripfrom, days, budget, tripto)
#     result = crew_result_store.get(key, "Result not available yet.")
#     return jsonify({'crew_result': result})



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
