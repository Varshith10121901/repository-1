from flask import Flask, render_template, request, jsonify
import nltk
import random
import string
import pyjokes
import webbrowser
from nltk.stem import WordNetLemmatizer
from datetime import datetime

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

app = Flask(__name__)

# Knowledge Base and Responses
knowledge_base = {
    "greetings": ["hello", "hi", "hey", "greetings", "good morning", "good evening", "howdy", "what's up", "hola", "bonjour"],
    
    "farewells": ["bye", "goodbye", "see you later", "farewell", "take care", "until next time", "have a good day", "adios", "au revoir", "catch you later"],
    
    "about_me": ["who are you", "what are you", "tell me about yourself", "what's your purpose", "what can you do"],
    
    "capital": ["what is the capital of", "capital of", "capital city"],
    
    "joke": ["tell me a joke", "joke", "make me laugh", "funny story"],
    
    "map": ["show me a map of", "map of", "where is", "location of", "directions to"],
    
    "movies": ["movie recommendation", "film suggestion", "tv show", "what to watch"],
    
    "gratitude": ["thank you", "thanks", "appreciate it", "grateful"],
    
    "apology": ["sorry", "apologize", "my mistake", "excuse me", "pardon"],
    
    "default": ["I'm sorry, I don't understand.", "Could you please rephrase that?", "I'm still learning."]
}

responses = {
    "greetings": ["Hello!", "Hi there!", "Hey!", "Good day!"],
    "farewells": ["Goodbye!", "See you later!", "Bye!", "Take care!", "Farewell!"],
    "about_me": ["I'm a helpful chatbot designed to assist with your questions."],
    "capital": {
        "france": "Paris", "japan": "Tokyo", "germany": "Berlin", "australia": "Canberra", 
        "canada": "Ottawa", "brazil": "Brasília", "india": "New Delhi", "china": "Beijing", 
        "italy": "Rome", "spain": "Madrid", "united kingdom": "London", 
        "united states": "Washington D.C.", "russia": "Moscow"
    },
    "movies": [
        "The Godfather", "Inception", "Pulp Fiction", "The Shawshank Redemption", "Titanic",
        "Jurassic Park", "Star Wars", "The Matrix", "Avatar", "E.T. the Extra-Terrestrial",
        "Forrest Gump", "The Dark Knight", "Jaws", "The Lion King", "Toy Story",
        "Casablanca", "Gone with the Wind", "The Wizard of Oz", "Schindler's List", "Goodfellas",
        "Back to the Future", "Indiana Jones", "The Lord of the Rings", "Harry Potter", "The Avengers",
        "Fight Club", "The Silence of the Lambs", "Gladiator", "The Departed", "Interstellar"
    ],
    "joke": [],  # Jokes will be added dynamically
    "map": ["Opening map..."],
    "gratitude": ["You're welcome!", "Glad I could help!"],
    "apology": ["That's okay!", "No problem at all."],
    "music": ["energetic", "chill", "pop", "rock", "jazz", "classical", "hip-hop"],
    
    "default": ["I'm sorry, I don't understand.", "Could you please rephrase that?", "I'm still learning."]
}

def preprocess(text):
    text = text.lower()
    text = "".join([char for char in text if char not in string.punctuation])
    tokens = nltk.word_tokenize(text)
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return lemmatized_tokens

def get_response(user_input):
    user_tokens = preprocess(user_input)
    
    # Simple keyword matching
    for intent, keywords in knowledge_base.items():
        for keyword in keywords:
            keyword_tokens = preprocess(keyword)
            if all(token in user_tokens for token in keyword_tokens):
                if intent == "capital":
                    for country in responses["capital"]:
                        if country in user_input.lower():
                            return f"The capital of {country} is {responses['capital'][country]}."
                    return "Please specify which country's capital you want."

                elif intent == "joke":
                    return pyjokes.get_joke()

                elif intent == "map":
                    location = " ".join([word for word in user_input.split() if word.lower() not in knowledge_base['map']])
                    # For web app, we'll return instructions instead of opening directly
                    return f"I would show you a map of {location}. In a complete app, this would open a map."
                
                elif intent == "movies":
                    return f"Here's a movie recommendation: {random.choice(responses['movies'])}"

                return random.choice(responses[intent])
    
    return random.choice(responses["default"])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_bot_response', methods=['POST'])
def bot_response():
    user_message = request.json['message']
    response = get_response(user_message)
    current_time = datetime.now().strftime("%I:%M %p")
    return jsonify({'response': response, 'time': current_time})

@app.route('/toggle_aura_mode', methods=['POST'])
def toggle_aura_mode():
    # This is just a placeholder for state management
    # In a real app, you might store this in a session or database
    current_mode = request.json['current_mode']
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)