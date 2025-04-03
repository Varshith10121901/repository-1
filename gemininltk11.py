import nltk
import random
import string
import pyjokes
import requests
import webbrowser
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

# Weather API Key (replace with your own)
WEATHER_API_KEY = "YOUR_WEATHER_API_KEY"  # Replace with your actual API key

# Knowledge Base and Responses
knowledge_base = {
    "greetings": ["hello", "hi", "hey", "greetings", "good morning", "good evening"],
    "farewells": ["bye", "goodbye", "see you later", "farewell", "take care"],
    "about_me": ["who are you", "what are you", "tell me about yourself", "what's your purpose", "what can you do"],
    "weather": ["what is the weather", "weather", "forecast", "temperature", "is it raining"],
    "capital": ["what is the capital of", "capital of", "city of"],
    "joke": ["tell me a joke", "joke", "make me laugh", "funny story"],
    "map": ["show me a map of", "map of", "where is", "location of"],
    "default": ["I'm sorry, I don't understand.", "Could you please rephrase that?", "I'm still learning.", "Can you provide more details?", "I don't have that information."],
}

responses = {
    "greetings": ["Hello!", "Hi there!", "Hey!", "Good day!"],
    "farewells": ["Goodbye!", "See you later!", "Bye!", "Take care!", "Farewell!"],
    "about_me": ["I'm a helpful chatbot designed to assist with your questions.", "I can provide information and have conversations.", "I'm here to help you find answers."],
    "weather": ["I can't provide real-time weather information. Try checking a weather app."],
    "capital": {
        "france": "Paris", "japan": "Tokyo", "germany": "Berlin", "australia": "Canberra", "canada": "Ottawa", "brazil": "Brasília",
        "india": "New Delhi", "china": "Beijing", "italy": "Rome", "spain": "Madrid", "egypt": "Cairo"
    },
    "joke": [],  # Jokes will be added dynamically
    "map": ["Opening map..."],
    "default": ["I'm sorry, I don't understand.", "Could you please rephrase that?", "I'm still learning.", "Can you provide more details?", "I don't have that information."],
}

def preprocess(text):
    text = text.lower()
    text = "".join([char for char in text if char not in string.punctuation])
    tokens = nltk.word_tokenize(text)
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return lemmatized_tokens

def get_weather(city):
    """Retrieves weather information using the OpenWeatherMap API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"The temperature in {city} is {temperature}°C with {description}."
    except requests.exceptions.RequestException as e:
        return f"Sorry, I couldn't retrieve weather information. Error: {e}"
    except (KeyError, IndexError):
        return "Sorry, I couldn't parse the weather data."

def get_response(user_input):
    user_tokens = preprocess(user_input)
    for intent, keywords in knowledge_base.items():
        for keyword in keywords:
            keyword_tokens = preprocess(keyword)
            if all(token in user_tokens for token in keyword_tokens):
                if intent == "capital":
                    for city in responses["capital"]:
                        if city in user_input.lower():
                            return responses["capital"][city]
                    return "Please specify which country's capital you want."

                elif intent == "weather":
                    city = " ".join([word for word in user_input.split() if word.lower() not in knowledge_base['weather']])
                    return get_weather(city)

                elif intent == "joke":
                    return pyjokes.get_joke()

                elif intent == "map":
                  location = " ".join([word for word in user_input.split() if word.lower() not in knowledge_base['map']])
                  webbrowser.open(f"https://www.google.com/maps/place/{location}")
                  return "Opening map..."

                return random.choice(responses[intent])

    # TF-IDF and Cosine Similarity for more advanced matching
    all_texts = list(knowledge_base.values())
    all_texts_flat = [item for sublist in all_texts for item in sublist]
    all_texts_flat.append(user_input)
    vectorizer = TfidfVectorizer(tokenizer=preprocess)
    tfidf = vectorizer.fit_transform(all_texts_flat)
    values = cosine_similarity(tfidf[-1], tfidf)
    index = values.argsort()[0][-2]
    flat = values.flatten()
    flat.sort()
    req_tfidf = flat[-2]

    if req_tfidf == 0:
        return random.choice(responses["default"])
    else:
        for intent, keywords in knowledge_base.items():
            if all_texts_flat[index] in keywords:
                return random.choice(responses[intent])
    return random.choice(responses["default"])

def chatbot():
    print("Chatbot: Hello! I'm here to chat. Type 'bye' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "bye":
            print("Chatbot: Goodbye!")
            break
        response = get_response(user_input)
        print("Chatbot:", response)

if __name__ == "__main__":
    chatbot()
