from flask import Flask, request, jsonify, render_template_string
import os
import logging
import nltk
nltk.download('wordnet')
nltk.download('punkt')  # For word_tokenize
import random
import string
import pyjokes
import PyDictionary 
import requests
import wikipedia
import feedparser
import re
import mysql.connector
from datetime import datetime
from nltk.stem import WordNetLemmatizer
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',  # Add your password if needed
    'database': 'tommy'
}

# Initialize database
def initialize_database():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cluadnltk (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp DATETIME NOT NULL
        )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

# Call database initialization
initialize_database()

# Function to store chat messages
def store_chat(user_message, bot_response):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Insert the chat exchange into the database
        cursor.execute(
            "INSERT INTO cluadnltk (user_message, bot_response, timestamp) VALUES (%s, %s, %s)",
            (user_message, bot_response, datetime.now())
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Chat stored in database")
    except Exception as e:
        logger.error(f"Database storage error: {e}")

# Initialize NLTK
def initialize_nltk():
    for resource in ['punkt', 'wordnet']:
        try:
            nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
        except LookupError:
            nltk.download(resource)

initialize_nltk()
lemmatizer = WordNetLemmatizer()

# Configuration
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
HEADERS = {'User-Agent': USER_AGENT}

# Knowledge Base
class KnowledgeBase:
    def __init__(self):
        self.intents = {
    "greetings": ["hello", "hi", "hey", "greetings", "good morning", "good evening", "howdy", "what's up", "hola", "bonjour"],
    
    "farewells": ["bye", "goodbye", "see you later", "farewell", "take care", "until next time", "have a good day", "adios", "au revoir", "catch you later"],
    
    "about_me": ["who are you", "what are you", "tell me about yourself", "what's your purpose", "what can you do", "your capabilities", "how do you work", "your features", "tell me about your functions"],
    
    "weather": ["what is the weather", "weather", "forecast", "temperature", "is it raining", "humidity", "precipitation", "sunny", "cloudy", "weather report", "weather alert"],
    
    "capital": ["what is the capital of", "capital of", "city of", "capital city", "main city of", "administrative center of"],
    
    "joke": ["tell me a joke", "joke", "make me laugh", "funny story", "humorous anecdote", "comedy", "tell something funny", "lighten the mood"],
    
    "map": ["show me a map of", "map of", "where is", "location of", "directions to", "navigate to", "find on map", "geographical location"],
    
    "time": ["what time is it", "current time", "tell me the time", "what's the time", "clock", "hour"],
    
    "date": ["what's today's date", "what day is it", "today's date", "current date", "calendar", "what's the date"],
    
    "math": ["calculate", "solve", "compute", "what is the sum of", "multiply", "divide", "subtract", "equation", "mathematical problem"],
    
    "definition": ["define", "what does mean", "meaning of", "definition of", "explain the term", "what is the meaning of", "what is", "who is"],
    
    "translation": ["translate", "how do you say", "in spanish", "in french", "in german", "language translation"],
    
    "health": ["medical advice", "health tips", "symptoms of", "treatment for", "how to cure", "medical condition"],
    
    "recipe": ["how to make", "recipe for", "cooking instructions", "ingredients for", "baking", "food preparation"],
    
    "news": ["latest news", "current events", "what's happening", "news update", "breaking news", "headlines", "recent news"],
    
    "sports": ["sports scores", "game results", "match outcome", "tournament", "championship", "sports news"],
    
    "music": ["play music", "song recommendation","say other", "music" , "music artist", "album", "playlist", "genres"],
    
    "movies": ["movie recommendation", "say other", "film suggestion", "tv show", "movies", "movie", "cinema", "what to watch"],
    
    "travel": ["travel recommendations", "vacation spots", "tourist attractions", "places to visit", "travel tips", "best destinations"],
    
    "shopping": ["where to buy", "purchase", "shopping recommendations", "best deals", "price comparison", "online shopping"],
    
    "tech_support": ["how to fix", "troubleshoot", "technical problem", "error message", "device not working", "software issue"],
    
    "education": ["learn about", "educational resources", "study materials", "courses", "tutorials", "learning platforms"],
    
    "personal_assistant": ["remind me to", "set alarm", "schedule appointment", "add to calendar", "create list", "make note"],
    
    "gratitude": ["thank you", "thanks", "appreciate it", "grateful", "much appreciated"],
    
    "apology": ["sorry", "apologize", "my mistake", "excuse me", "pardon"],
    
    "search": ["search for", "look up", "find information about", "google", "search"],
    
    "wiki": ["wiki", "wikipedia", "tell me about", "information on", "who was", "what is"],
    
    "stock": ["stock price", "stock market", "share price", "investment", "stock quote"],
    
    "currency": ["exchange rate", "convert currency", "currency exchange", "dollar to", "euro to"],
    
    "default": ["I'm sorry, I don't understand.", "Could you please rephrase that?", "I'm still learning.", 
                "Can you provide more details?", "I don't have that information.", 
                "I'm not sure I follow.", "Could you elaborate on that?", 
                "That's beyond my current capabilities.", "I'm drawing a blank on that one.",
                "Let me know if there's something else I can help with."],
}
        
        self.responses = {
    "greetings": ["Hello!", "Hi there!", "Hey!", "Good day!"],
    "farewells": ["Goodbye!", "See you later!", "Bye!", "Take care!", "Farewell!"],
    "movie": ["kgf", "salaar", "kgf 2", "kantara", "inception", "thor ragnorak", "toxic"],
    "music": ["Tum Hi Ho - Arijit Singh (Hindi)", "Kesariya - Arijit Singh (Hindi)", "Channa Mereya - Arijit Singh (Hindi)", "Agar Tum Saath Ho - Arijit Singh (Hindi)", "Muskurane Ki Wajah Tum Ho - Arijit Singh (Hindi)", "The Night We Met - Lord Huron (English - similar feel)", "Say You Won't Let Go - James Arthur (English - similar feel)"],
    "about_me": ["I am AURA trained by aurafied group"],
    "weather": ["Let me check the weather for you."],
    "education": ["What subject are you interested in learning about?", "Are you looking for resources for a specific age group or level?", "I can help you find study materials for various subjects.", "Would you like me to search for online courses or in-person classes?", "Are you interested in video tutorials or written guides?", "There are many excellent learning platforms available online.", "Do you have a preferred learning style?", "What are your educational goals?", "I can help you find information on different educational institutions.", "Are you looking for information on certifications or degrees?"],
    "capital": {
        # Capital city data remains the same as in the original code
        "france": "Paris", "japan": "Tokyo", "germany": "Berlin", "australia": "Canberra","france": "Paris", "japan": "Tokyo", "germany": "Berlin", "australia": "Canberra", "canada": "Ottawa", "brazil": "Brasília", "india": "new delhi", "united kingdom": "London", "united states": "Washington, D.C.", "china": "Beijing", "russia": "Moscow", "italy": "Rome", "spain": "Madrid", "south africa": "Pretoria", "argentina": "Buenos Aires", "mexico": "Mexico City", "egypt": "Cairo", "nigeria": "Abuja", "saudi arabia": "Riyadh", "indonesia": "Jakarta", "turkey": "Ankara", "south korea": "Seoul", "netherlands": "Amsterdam", "belgium": "Brussels", "switzerland": "Bern", "sweden": "Stockholm", "norway": "Oslo", "denmark": "Copenhagen", "finland": "Helsinki", "greece": "Athens", "portugal": "Lisbon", "ireland": "Dublin", "austria": "Vienna", "poland": "Warsaw", "hungary": "Budapest", "czech republic": "Prague", "slovakia": "Bratislava", "romania": "Bucharest", "bulgaria": "Sofia", "croatia": "Zagreb", "serbia": "Belgrade", "albania": "Tirana", "ukraine": "Kyiv", "belarus": "Minsk", "kazakhstan": "Nur-Sultan", "uzbekistan": "Tashkent", "iran": "Tehran", "thailand": "Bangkok", "vietnam": "Hanoi", "philippines": "Manila", "malaysia": "Kuala Lumpur", "singapore": "Singapore", "new zealand": "Wellington", "chile": "Santiago", "colombia": "Bogotá", "peru": "Lima", "venezuela": "Caracas", "ecuador": "Quito", "bolivia": "Sucre", "paraguay": "Asunción", "uruguay": "Montevideo", "kenya": "Nairobi", "ethiopia": "Addis Ababa", "morocco": "Rabat", "algeria": "Algiers", "tunisia": "Tunis", "ghana": "Accra", "ivory coast": "Yamoussoukro", "cameroon": "Yaoundé", "democratic republic of the congo": "Kinshasa", "angola": "Luanda", "zambia": "Lusaka", "zimbabwe": "Harare", "uganda": "Kampala", "tanzania": "Dodoma", "sudan": "Khartoum", "afghanistan": "Kabul", "iraq": "Baghdad", "syria": "Damascus", "jordan": "Amman", "israel": "Jerusalem", "lebanon": "Beirut", "oman": "Muscat", "kuwait": "Kuwait City", "qatar": "Doha", "bahrain": "Manama", "united arab emirates": "Abu Dhabi", "yemen": "Sana'a", "nepal": "Kathmandu", "sri lanka": "Sri Jayawardenepura Kotte", "myanmar": "Naypyidaw", "cambodia": "Phnom Penh", "laos": "Vientiane", "bangladesh": "Dhaka", "pakistan": "Islamabad", "mongolia": "Ulaanbaatar", "canada": "Ottawa", "brazil": "Brasília", "india": "new delhi"
        # ... rest of capital cities ...
    },
    "joke": [],  # Jokes will be added dynamically
    "defnation": [],
    "map": ["Opening map..."],
    "default": ["I'm sorry, I don't understand.", "Could you please rephrase that?", "I'm still learning.", "Can you provide more details?", "I don't have that information."],
    
}

class WebSearchEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def search_wikipedia(self, query):
        try:
            cleaned_query = re.sub(r'\b(what|who|where|when|why|how|is|are|was|were|tell me about|define|information on)\b', '', query, flags=re.IGNORECASE).strip()
            page = wikipedia.page(wikipedia.search(cleaned_query)[0])
            return {
                'title': page.title,
                'summary': wikipedia.summary(page.title, sentences=3),
                'url': page.url
            }
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return None

    def get_news(self, category="general"):
        rss_feeds = {
            "general": "http://rss.cnn.com/rss/edition.rss",
            "technology": "http://rss.cnn.com/rss/edition_technology.rss"
        }
        try:
            feed = feedparser.parse(rss_feeds.get(category, rss_feeds["general"]))
            return [{
                'title': entry.title,
                'link': entry.link,
                'published': entry.published
            } for entry in feed.entries[:5]]
        except Exception as e:
            logger.error(f"News fetch error: {e}")
            return []

class NLPProcessor:
    @staticmethod
    def preprocess(text):
        text = text.lower().translate(str.maketrans("", "", string.punctuation))
        return [lemmatizer.lemmatize(token) for token in nltk.word_tokenize(text)]

    @staticmethod
    def classify_intent(user_input, knowledge_base):
        user_tokens = NLPProcessor.preprocess(user_input)
        
        for intent, keywords in knowledge_base.intents.items():
            for keyword in keywords:
                if all(token in user_tokens for token in NLPProcessor.preprocess(keyword)):
                    return intent
        return "unknown"

    @staticmethod
    def extract_entity(user_input, keywords):
        for keyword in keywords:
            if keyword in user_input.lower():
                return user_input.lower().split(keyword, 1)[1].strip()
        return user_input.strip()

def get_weather(city):
    if not WEATHER_API_KEY:
        return "Weather API key not configured."
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        return (f"The temperature in {city} is {response['main']['temp']}°C "
                f"with {response['weather'][0]['description']}.")
    except Exception as e:
        logger.error(f"Weather fetch error: {e}")
        return f"Couldn't get weather for {city}."

class Chatbot:
    def __init__(self):
        self.kb = KnowledgeBase()
        self.web = WebSearchEngine()
        self.nlp = NLPProcessor()

    def get_response(self, user_input):
        intent = self.nlp.classify_intent(user_input, self.kb)
        
        if intent == "greetings":
            return random.choice(self.kb.responses["greetings"])
        elif intent == "farewells":
            return random.choice(self.kb.responses["farewells"])
        elif intent == "movies":
            return random.choice(self.kb.responses["movie"])
        elif intent == "music":
            return random.choice(self.kb.responses["music"])
        elif intent == "education":
            return random.choice(self.kb.responses["education"])
        elif intent == "about_me":
            return self.kb.responses["about_me"][0]
        elif intent == "weather":
            city = self.nlp.extract_entity(user_input, self.kb.intents["weather"])
            return get_weather(city)
        elif intent == "capital":
            for country in self.kb.responses["capital"]:
                if country in user_input.lower():
                    return self.kb.responses["capital"][country]
            return "Please specify a country."
        elif intent == "joke":
            return pyjokes.get_joke()
        elif intent == "defnation":
            return PyDictionary.get_definition()  
        elif intent == "time":
            return f"The current time is {datetime.now().strftime('%H:%M:%S')}."
        elif intent == "date":
            return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
        elif intent == "news":
            return "\n".join([f"{i+1}. {h['title']}" 
                            for i, h in enumerate(self.web.get_news())])
        elif intent == "wiki":
            query = self.nlp.extract_entity(user_input, self.kb.intents["wiki"])
            result = self.web.search_wikipedia(query)
            return f"{result['title']}: {result['summary']}" if result else "No info found."
        elif intent == "mike":
            return random.choice(self.kb.responses["mike"])
        return random.choice(self.kb.responses["default"])

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant</title>
    <style>
        :root {
            --primary-color: #6b46c1;
            --secondary-color: #805ad5;
            --background-color: #f7fafc;
            --chat-bg: #ffffff;
            --text-color: #2d3748;
            --light-text: #718096;
            --message-user: #e9d8fd;
            --message-bot: #f0f5ff;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --aura-mode-color: #2dd4bf;
            --mike-color: #f56565;
            --recording-color: #e53e3e;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        header {
            background-color: var(--primary-color);
            color: white;
            padding: 1rem;
            box-shadow: var(--shadow);
            z-index: 10;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }

        .chat-container {
            background-color: var(--chat-bg);
            border-radius: 12px;
            box-shadow: var(--shadow);
            flex-grow: 1;
            margin: 1rem auto;
            display: flex;
            flex-direction: column;
            width: 70%; /* Set chatbox to 70% of screen width */
        }

        .chat-messages {
            padding: 1rem;
            flex-grow: 1;
            overflow-y: auto;
            max-height: 600px; /* Larger chat box */
            min-height: 500px; /* Ensure minimum height */
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .message {
            max-width: 80%;
            padding: 0.75rem 1rem;
            border-radius: 1rem;
            animation: fadeIn 0.3s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message-user {
            align-self: flex-end;
            background-color: var(--message-user);
            border-bottom-right-radius: 0.25rem;
        }

        .message-bot {
            align-self: flex-start;
            background-color: var(--message-bot);
            border-bottom-left-radius: 0.25rem;
        }

        .message-time {
            font-size: 0.6rem;
            color: var(--light-text);
            text-align: right;
            margin-top: 0.25rem;
        }

        .input-container {
            display: flex;
            gap: 0.5rem;
            padding: 1rem;
            background-color: white;
            border-top: 1px solid #e2e8f0;
            align-items: center;
        }

        .chat-input {
            flex-grow: 1;
            border: 1px solid #e2e8f0;
            border-radius: 24px;
            padding: 0.75rem 1.25rem;
            font-size: 0.875rem;
            outline: none;
            resize: none;
            min-height: 48px;
        }

        .button {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            border: none;
            color: white;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: all 0.3s ease;
        }

        .send-button {
            background-color: var(--primary-color);
        }

        .mike-button {
            background-color: var(--mike-color);
        }

        .mike-button.recording {
            background-color: var(--recording-color);
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(229, 62, 62, 0.7);
            }
            70% {
                transform: scale(1.05);
                box-shadow: 0 0 0 10px rgba(229, 62, 62, 0);
            }
            100% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(229, 62, 62, 0);
            }
        }

        .tooltip {
            position: relative;
            display: inline-block;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 120px;
            background-color: black;
            color: white;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -60px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.75rem;
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }

        .status-indicator {
            font-size: 0.75rem;
            color: var(--light-text);
            margin-left: 10px;
            display: none;
        }

        .status-indicator.visible {
            display: block;
            animation: fadeIn 0.3s ease-out;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>AURA</h1>
        </div>
    </header>

    <div class="container">
        <div class="chat-container">
            <div class="chat-messages" id="chatbox">
                <div class="message message-bot">
                    Hello! I'm your AI assistant. How can I help you today?
                    <div class="message-time">{{ time }}</div>
                </div>
            </div>

            <div class="input-container">
                <textarea class="chat-input" id="chat-input" placeholder="Type your message here..." rows="1"></textarea>
                
                <div class="status-indicator" id="voice-status">Listening...</div>
                
                <div class="tooltip">
                    <button class="button mike-button" id="mike-button">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                            <line x1="12" y1="19" x2="12" y2="23"></line>
                            <line x1="8" y1="23" x2="16" y2="23"></line>
                        </svg>
                    </button>
                    <span class="tooltiptext" id="mic-tooltip">Start Voice Input</span>
                </div>
                
                <div class="tooltip">
                    <button class="button send-button" id="send-button">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                    <span class="tooltiptext">Send</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const chatInput = document.getElementById('chat-input');
            const sendButton = document.getElementById('send-button');
            const mikeButton = document.getElementById('mike-button');
            const chatbox = document.getElementById('chatbox');
            const voiceStatus = document.getElementById('voice-status');
            const micTooltip = document.getElementById('mic-tooltip');
            
            // Check if browser supports speech recognition
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            let recognition;
            let isRecording = false;
            
            if (SpeechRecognition) {
                recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.lang = 'en-US';
                recognition.interimResults = false;
                recognition.maxAlternatives = 1;
                
                // Speech recognition event handlers
                recognition.onstart = function() {
                    isRecording = true;
                    mikeButton.classList.add('recording');
                    voiceStatus.textContent = 'Listening...';
                    voiceStatus.classList.add('visible');
                    micTooltip.textContent = 'Stop Voice Input';
                };
                
                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript;
                    chatInput.value = transcript;
                    voiceStatus.textContent = 'Processing...';
                };
                
                recognition.onend = function() {
                    isRecording = false;
                    mikeButton.classList.remove('recording');
                    voiceStatus.classList.remove('visible');
                    micTooltip.textContent = 'Start Voice Input';
                    
                    // Auto-send if we have text
                    if (chatInput.value.trim()) {
                        sendMessage();
                    }
                };
                
                recognition.onerror = function(event) {
                    voiceStatus.textContent = 'Error: ' + event.error;
                    setTimeout(() => {
                        voiceStatus.classList.remove('visible');
                    }, 3000);
                    isRecording = false;
                    mikeButton.classList.remove('recording');
                    micTooltip.textContent = 'Start Voice Input';
                };
            } else {
                mikeButton.style.display = 'none';
                console.log('Speech recognition not supported');
            }

            function appendMessage(text, sender) {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message', sender);
                messageElement.textContent = text;
                
                const timeElement = document.createElement('div');
                timeElement.classList.add('message-time');
                timeElement.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                messageElement.appendChild(timeElement);
                
                chatbox.appendChild(messageElement);
                chatbox.scrollTop = chatbox.scrollHeight;
            }

            async function sendMessage() {
                const message = chatInput.value.trim();
                if (!message) return;

                appendMessage(message, 'message-user');
                chatInput.value = '';
                chatInput.style.height = 'auto'; // Reset height

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message})
                    });
                    const data = await response.json();
                    appendMessage(data.response, 'message-bot');
                } catch (error) {
                    appendMessage('Error communicating with server', 'message-bot');
                    console.error('Error:', error);
                }
            }

            function toggleMic() {
                if (isRecording) {
                    recognition.stop();
                } else {
                    recognition.start();
                }
            }

            sendButton.addEventListener('click', sendMessage);
            mikeButton.addEventListener('click', toggleMic);
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            // Auto-resize textarea
            chatInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });
        });
    </script>
</body>
</html>
"""

# Flask Routes
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, time=datetime.now().strftime('%I:%M %p'))

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    chatbot = Chatbot()
    response = chatbot.get_response(message)
    
    # Store the chat in the database
    store_chat(message, response)
    
    return jsonify({'response': response})
    print("http://127.0.0.1:5000/")

if __name__ == '__main__':
    app.run(debug=True)