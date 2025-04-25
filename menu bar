from flask import Flask, request, jsonify, render_template_string
import os
import logging
import nltk
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('vader_lexicon')  # For sentiment analysis
nltk.download('omw-1.4')  # Open Multilingual WordNet
import random
import string
import pyjokes
import requests
import wikipedia
import feedparser
import spacy
import re
import mysql.connector
from datetime import datetime, timedelta
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
import numpy as np
import pandas as pd
from textblob import TextBlob
import calendar
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from newspaper import Article

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
            timestamp DATETIME NOT NULL,
            sentiment FLOAT,
            intent VARCHAR(255)
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
def store_chat(user_message, bot_response, sentiment=0.0, intent="unknown"):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Insert the chat exchange into the database
        cursor.execute(
            "INSERT INTO cluadnltk (user_message, bot_response, timestamp, sentiment, intent) VALUES (%s, %s, %s, %s, %s)",
            (user_message, bot_response, datetime.now(), sentiment, intent)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Chat stored in database")
    except Exception as e:
        logger.error(f"Database storage error: {e}")

# Initialize NLTK
def initialize_nltk():
    for resource in ['punkt', 'wordnet', 'vader_lexicon', 'omw-1.4']:
        try:
            nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
        except LookupError:
            nltk.download(resource)

initialize_nltk()
lemmatizer = WordNetLemmatizer()
sentiment_analyzer = SentimentIntensityAnalyzer()

# Initialize spaCy
try:
    nlp = spacy.load('en_core_web_sm')
except:
    os.system('python -m spacy download en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

# Knowledge Base
class KnowledgeBase:
    def __init__(self):
        self.intents = {
            "greetings": ["hello", "hi", "hey", "good morning", "good evening", "yo", "what's up"],
            "farewells": ["bye", "goodbye", "see you later", "catch you later", "peace out"],
            "about_me": ["who are you", "what are you", "tell me about yourself"],
            "weather": ["weather", "forecast", "temperature", "is it raining", "how's the weather"],
            "capital": ["capital of", "what is the capital of", "capital city"],
            "joke": ["tell me a joke", "make me laugh", "i got bored", "funny stuff", "got a joke?"],
            "time": ["what time is it", "current time", "time now", "tell me the time"],
            "spacy": ["spacy", "what is spacy", "tell me about spacy", "use spacy", "explain spacy", "spaCy features"],
            "date": ["what's today's date", "current date", "what day is it", "date?"],
            "news": ["latest news", "current events", "news headlines", "any news"],
            "search": ["search for", "look up", "find information on", "google"],
            "wiki": ["wiki", "tell me about","tell about","explain", "define"],
            "music": ["play music", "start a song", "play a song", "music please","music"],
            "games": ["let's play a game", "start a game", "play something", "i want to play"],
            "math": ["solve", "calculate", "what's the answer", "math question"],
            "translate": ["translate", "how do you say", "say in another language"],
            "reminder": ["set a reminder", "remind me", "schedule a reminder"],
            "alarm": ["set an alarm", "wake me up", "alarm for"],
            "message": ["send a message", "text", "message someone"],
            "location": ["where am i", "current location", "my location"],
            "help": ["help", "assist me", "i need help", "support"],
            "mike": ["mike", "about mike", "who is mike"],
            "sentiment": ["how do i feel", "analyze my sentiment", "sentiment analysis"],
            "stocks": ["stock price", "stock market", "investing", "shares"],
            "crypto": ["bitcoin", "ethereum", "crypto", "cryptocurrency"],
            "currency": ["exchange rate", "convert currency", "dollar to euro"],
            "summarize": ["summarize", "give me a summary", "tldr"],
            "image": ["analyze image", "describe image", "what's in this picture"],
            "health": ["health tips", "fitness advice", "nutrition"],
            "trivia": ["random fact", "trivia", "tell me something interesting"],
            "horoscope": ["horoscope", "astrology", "zodiac sign"],
            "quotes": ["inspirational quote", "famous quote", "quote of the day"]
        }
        
        self.responses = {
            "greetings": ["Hello!", "Hi there!", "Hey!"],
            "farewells": ["Goodbye!", "See you later!", "Take care!"],
            "music": ["Blinding Lights by The Weeknd", "Bohemian Rhapsody by Queen", "Shape of You by Ed Sheeran", "Levitating by Dua Lipa", "Smells Like Teen Spirit by Nirvana", "Bad Guy by Billie Eilish", "Hotel California by Eagles", "Rolling in the Deep by Adele", "Uptown Funk by Bruno Mars", "Hey Jude by The Beatles"],
            "about_me": ["I'm an AI assistant created to help with various tasks."],
            "capital": {
                "france": "Paris", "japan": "Tokyo", "germany": "Berlin",
                "usa": "Washington, D.C.", "uk": "London", "canada": "Ottawa",
                "india": "New Delhi", "australia": "Canberra", "brazil": "Brasília",
                "china": "Beijing", "russia": "Moscow", "italy": "Rome",
                "spain": "Madrid", "mexico": "Mexico City", "egypt": "Cairo",
                "south africa": "Pretoria (administrative), Cape Town (legislative), Bloemfontein (judicial)"
            },
            "mike": ["Mike is my creator! He's passionate about AI and developing helpful assistants."],
            "spacy": ["spaCy is an advanced NLP library designed for production use, featuring pre-trained models for various languages."],
            "health_tips": [
                "Stay hydrated by drinking at least 8 glasses of water daily.",
                "Try to get 7-9 hours of sleep every night.",
                "Incorporate 30 minutes of physical activity into your daily routine.",
                "Eat a balanced diet with plenty of fruits and vegetables.",
                "Practice mindfulness or meditation to reduce stress."
            ],
            "trivia": [
                "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
                "A day on Venus is longer than a year on Venus. It takes Venus longer to rotate once on its axis than to complete one orbit of the Sun.",
                "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.",
                "The average person walks the equivalent of five times around the world in a lifetime.",
                "Octopuses have three hearts, nine brains, and blue blood."
            ],
            "quotes": [
                "The only way to do great work is to love what you do. - Steve Jobs",
                "Life is what happens when you're busy making other plans. - John Lennon",
                "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
                "It does not matter how slowly you go as long as you do not stop. - Confucius",
                "The only impossible journey is the one you never begin. - Tony Robbins"
            ],
            "default": ["I'm not sure I understand.", "Could you please rephrase that?"]
        }
        
        # Add more comprehensive capital data
        self.capitals_data = pd.DataFrame({
            'country': ['france', 'japan', 'germany', 'usa', 'uk', 'canada', 'india', 
                       'australia', 'brazil', 'china', 'russia', 'italy', 'spain', 
                       'mexico', 'egypt', 'south africa', 'argentina', 'sweden', 
                       'norway', 'finland', 'denmark', 'netherlands', 'belgium', 
                       'portugal', 'greece', 'turkey', 'poland', 'ukraine', 'romania'],
            'capital': ['Paris', 'Tokyo', 'Berlin', 'Washington, D.C.', 'London', 'Ottawa', 
                       'New Delhi', 'Canberra', 'Brasília', 'Beijing', 'Moscow', 'Rome', 
                       'Madrid', 'Mexico City', 'Cairo', 'Pretoria (administrative)', 
                       'Buenos Aires', 'Stockholm', 'Oslo', 'Helsinki', 'Copenhagen', 
                       'Amsterdam', 'Brussels', 'Lisbon', 'Athens', 'Ankara', 'Warsaw', 
                       'Kyiv', 'Bucharest']
        })

        # Horoscope data
        self.zodiac_signs = {
            'aries': 'March 21 - April 19',
            'taurus': 'April 20 - May 20',
            'gemini': 'May 21 - June 20',
            'cancer': 'June 21 - July 22',
            'leo': 'July 23 - August 22',
            'virgo': 'August 23 - September 22',
            'libra': 'September 23 - October 22',
            'scorpio': 'October 23 - November 21',
            'sagittarius': 'November 22 - December 21',
            'capricorn': 'December 22 - January 19',
            'aquarius': 'January 20 - February 18',
            'pisces': 'February 19 - March 20'
        }
        
        self.horoscopes = {
            'aries': ['You\'re feeling particularly energetic today. Channel that energy into productive pursuits.',
                     'Your assertiveness will serve you well in negotiations today.',
                     'Take time to cool down before making important decisions.'],
            'taurus': ['Your persistence is paying off. Keep pushing toward your goals.',
                      'Financial opportunities may present themselves today.',
                      'Take time to appreciate the beautiful things in life.'],
            'gemini': ['Your communication skills are sharp today. Use them to resolve misunderstandings.',
                      'Learning something new will satisfy your curiosity.',
                      'Be mindful not to spread yourself too thin across multiple tasks.'],
            'cancer': ['Your intuition is particularly strong today. Trust your gut feelings.',
                      'Focus on self-care and emotional well-being.',
                      'Home improvements or family matters may require your attention.'],
            'leo': ['Your natural leadership qualities shine today. Others will look to you for guidance.',
                   'Creative pursuits will bring you joy and fulfillment.',
                   'Be mindful of the fine line between confidence and arrogance.'],
            'virgo': ['Your analytical skills will help solve a complex problem.',
                     'Pay attention to details, but don\'t get lost in them.',
                     'Your help will be appreciated by someone in need.'],
            'libra': ['Focus on finding balance in your relationships today.',
                     'Artistic endeavors will bring you satisfaction.',
                     'Don\'t avoid difficult decisions just to keep the peace.'],
            'scorpio': ['Your intensity and focus will help you overcome obstacles.',
                       'Trust issues may arise, but open communication will help.',
                       'Your intuition about others\' motives is spot on.'],
            'sagittarius': ['Adventure calls! Try something new that expands your horizons.',
                           'Your optimism will inspire those around you.',
                           'Be careful not to promise more than you can deliver.'],
            'capricorn': ['Your discipline and hard work are noticed by those in positions of power.',
                         'Consider the long-term impact of your current decisions.',
                         'Don\'t neglect your personal life while pursuing professional goals.'],
            'aquarius': ['Your innovative ideas will be well-received today.',
                        'Connect with friends or groups that share your ideals.',
                        'Remember that change requires patience and persistence.'],
            'pisces': ['Your compassion and empathy make you a valuable friend today.',
                      'Artistic inspiration flows freely; capture your creative ideas.',
                      'Set boundaries to protect your emotional energy.']
        }

class WebSearchEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"})

    def search_wikipedia(self, query):
        try:
            cleaned_query = re.sub(r'\b(what|who|where|is|what|who|where|when|why|which|whose|whom|how)\b', '', query, flags=re.IGNORECASE).strip()
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
            "technology": "http://rss.cnn.com/rss/edition_technology.rss",
            "business": "http://rss.cnn.com/rss/money_latest.rss",
            "health": "http://rss.cnn.com/rss/edition_health.rss",
            "entertainment": "http://rss.cnn.com/rss/edition_entertainment.rss",
            "sports": "http://rss.cnn.com/rss/edition_sport.rss"
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
    
    def summarize_article(self, url):
        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()
            return {
                'title': article.title,
                'summary': article.summary,
                'keywords': article.keywords
            }
        except Exception as e:
            logger.error(f"Article summarization error: {e}")
            return None

class NLPProcessor:
    @staticmethod
    def preprocess(text):
        text = text.lower().translate(str.maketrans("", "", string.punctuation))
        return [lemmatizer.lemmatize(token) for token in nltk.word_tokenize(text)]

    @staticmethod
    def classify_intent(user_input, knowledge_base):
        # Try the trained classifier first
        if 'intent_classifier' in globals() and intent_classifier:
            try:
                intent = intent_classifier.predict([user_input.lower()])[0]
                return intent
            except:
                pass
        
        # Fall back to keyword matching
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
    
    @staticmethod
    def analyze_sentiment(text):
        # NLTK VADER sentiment analysis
        scores = sentiment_analyzer.polarity_scores(text)
        
        # TextBlob sentiment analysis
        blob = TextBlob(text)
        textblob_sentiment = blob.sentiment
        
        # Combine results
        return {
            'vader': scores,
            'textblob': {
                'polarity': textblob_sentiment.polarity,
                'subjectivity': textblob_sentiment.subjectivity
            },
            'overall': scores['compound']
        }
    
    @staticmethod
    def extract_entities_spacy(text):
        doc = nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        return entities
    
    @staticmethod
    def extract_noun_phrases(text):
        doc = nlp(text)
        return [chunk.text for chunk in doc.noun_chunks]

# Train a simple classifier for intent recognition
def train_intent_classifier():
    try:
        # Simple dataset for intent classification
        X = [
            "hello", "hi there", "hey", "good morning",
            "goodbye", "bye", "see you later",
            "what's the weather like", "is it raining",
            "tell me a joke", "make me laugh",
            "who are you", "what can you do",
            "search for cats", "find information on AI",
            "what's the capital of France", "capital of Japan",
            "what time is it", "current time",
            "set a reminder", "remind me to call mom",
            "translate hello to Spanish", "how do you say goodbye in French",
            "calculate 5 plus 7", "what is 10 divided by 2",
            "latest news", "current events",
            "play music", "recommend a song",
            "where am I", "my location",
            "stock price of Apple", "Bitcoin price",
            "tell me about neural networks", "explain quantum computing"
        ]
        
        y = [
            "greeting", "greeting", "greeting", "greeting",
            "farewell", "farewell", "farewell",
            "weather", "weather",
            "joke", "joke",
            "about", "about",
            "search", "search",
            "capital", "capital",
            "time", "time",
            "reminder", "reminder",
            "translate", "translate",
            "math", "math",
            "news", "news",
            "music", "music",
            "location", "location",
            "finance", "finance",
            "wiki", "wiki"
        ]
        
        # Train a simple Naive Bayes classifier
        intent_classifier = Pipeline([
            ('vectorizer', CountVectorizer()),
            ('classifier', MultinomialNB())
        ])
        
        intent_classifier.fit(X, y)
        return intent_classifier
    except Exception as e:
        logger.error(f"Error training intent classifier: {e}")
        return None

# Try to initialize the intent classifier
try:
    intent_classifier = train_intent_classifier()
except:
    intent_classifier = None

def get_reminders():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message TEXT NOT NULL,
            reminder_time DATETIME NOT NULL,
            created_at DATETIME NOT NULL
        )
        """)
        
        # Get current reminders
        cursor.execute("SELECT * FROM reminders WHERE reminder_time > NOW() ORDER BY reminder_time")
        reminders = cursor.fetchall()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return reminders
    except Exception as e:
        logger.error(f"Error fetching reminders: {e}")
        return []

def set_reminder(message, time_str):
    try:
        # Parse the time string to datetime
        reminder_time = datetime.now()
        
        # Handle relative time
        if "minute" in time_str:
            minutes = int(re.findall(r'\d+', time_str)[0])
            reminder_time += timedelta(minutes=minutes)
        elif "hour" in time_str:
            hours = int(re.findall(r'\d+', time_str)[0])
            reminder_time += timedelta(hours=hours)
        elif "day" in time_str:
            days = int(re.findall(r'\d+', time_str)[0])
            reminder_time += timedelta(days=days)
        else:
            # Try to parse specific time
            try:
                reminder_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            except:
                try:
                    reminder_time = datetime.strptime(time_str, "%H:%M")
                    reminder_time = datetime.now().replace(hour=reminder_time.hour, minute=reminder_time.minute, second=0, microsecond=0)
                    # If the time has already passed today, set it for tomorrow
                    if reminder_time < datetime.now():
                        reminder_time += timedelta(days=1)
                except:
                    return f"I couldn't understand the time format: {time_str}"
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message TEXT NOT NULL,
            reminder_time DATETIME NOT NULL,
            created_at DATETIME NOT NULL
        )
        """)
        
        cursor.execute(
            "INSERT INTO reminders (message, reminder_time, created_at) VALUES (%s, %s, %s)",
            (message, reminder_time, datetime.now())
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return f"Reminder set for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}: {message}"
    except Exception as e:
        logger.error(f"Error setting reminder: {e}")
        return f"Failed to set reminder: {str(e)}"

def play_game(game_name):
    games = {
        "number_guess": {
            "description": "I'm thinking of a number between 1-100. Try to guess it!",
            "play": lambda: random.randint(1, 100)
        },
        "rock_paper_scissors": {
            "description": "Let's play Rock, Paper, Scissors! Type your choice.",
            "play": lambda: random.choice(["rock", "paper", "scissors"])
        },
        "dice_roll": {
            "description": "Rolling a dice...",
            "play": lambda: random.randint(1, 6)
        },
        "coin_flip": {
            "description": "Flipping a coin...",
            "play": lambda: random.choice(["heads", "tails"])
        },
        "word_scramble": {
            "description": "Unscramble this word!",
            "words": ["python", "computer", "artificial", "intelligence", "machine", "learning"],
            "play": lambda words=None: ''.join(random.sample(random.choice(words), len(random.choice(words))))
        }
    }
    
    if game_name.lower() in games:
        game = games[game_name.lower()]
        if game_name.lower() == "word_scramble":
            scrambled = game["play"](game["words"])
            return {
                "game": game_name,
                "description": game["description"],
                "scrambled_word": scrambled
            }
        else:
            result = game["play"]()
            return {
                "game": game_name,
                "description": game["description"],
                "result": result
            }
    else:
        available_games = list(games.keys())
        return {
            "error": f"Game '{game_name}' not found",
            "available_games": available_games
        }

# Main processing function
def process_input(user_input):
    sentiment_result = NLPProcessor.analyze_sentiment(user_input)
    kb = KnowledgeBase()
    web_search = WebSearchEngine()
    
    # Classify intent
    intent = NLPProcessor.classify_intent(user_input, kb)
    
    # Process based on intent
    response = "I'm not sure how to help with that."
    
    if intent == "greetings":
        response = random.choice(kb.responses["greetings"])
    
    elif intent == "farewells":
        response = random.choice(kb.responses["farewells"])
    
    elif intent == "about_me":
        response = random.choice(kb.responses["about_me"])
    
    elif intent == "spacy":
        response = random.choice(kb.responses["spacy"])
    
    elif intent == "mike":
        response = random.choice(kb.responses["mike"])
    
    elif intent == "joke":
        try:
            response = pyjokes.get_joke()
        except:
            response = "Why did the AI go to therapy? It had too many unresolved dependencies!"
    
    elif intent == "weather":
        city = NLPProcessor.extract_entity(user_input, ["weather in", "forecast for", "temperature in", "weather", "forecast"])
        if city:
            response = f"To provide weather information for {city}, I need a weather API key."
        else:
            response = "Which city would you like the weather for?"
    
    elif intent == "capital":
        country = NLPProcessor.extract_entity(user_input, ["capital of", "what is the capital of", "capital city of"])
        
        # Try to find the country in our database
        match = kb.capitals_data[kb.capitals_data['country'] == country.lower()]
        
        if not match.empty:
            capital = match.iloc[0]['capital']
            response = f"The capital of {country.title()} is {capital}."
        else:
            response = f"I'm not sure what the capital of {country} is."
    
    elif intent == "wiki":
        entity = NLPProcessor.extract_entity(user_input, ["tell me about", "tell about", "explain", "define", "wiki"])
        if entity:
            wiki_result = web_search.search_wikipedia(entity)
            if wiki_result:
                response = f"{wiki_result['summary']}\nSource: {wiki_result['url']}"
            else:
                response = f"I couldn't find information about {entity}."
        else:
            response = "What would you like to know about?"
    
    elif intent == "time":
        now = datetime.now()
        response = f"The current time is {now.strftime('%H:%M:%S')}."
    
    elif intent == "date":
        today = datetime.now()
        response = f"Today is {today.strftime('%A, %B %d, %Y')}."
    
    elif intent == "search":
        query = NLPProcessor.extract_entity(user_input, ["search for", "look up", "find", "google"])
        if query:
            response = f"Here's what I found for '{query}':\n"
            wiki_result = web_search.search_wikipedia(query)
            if wiki_result:
                response += f"\nFrom Wikipedia: {wiki_result['summary']}\n"
        else:
            response = "What would you like to search for?"
    
    elif intent == "news":
        category = "general"
        for cat in ["technology", "business", "health", "entertainment", "sports"]:
            if cat in user_input.lower():
                category = cat
                break
        
        news = web_search.get_news(category)
        if news:
            response = f"Here are the latest {category} headlines:\n\n"
            for i, item in enumerate(news, 1):
                response += f"{i}. {item['title']}\n"
        else:
            response = f"I couldn't fetch the latest {category} news."
    
    elif intent == "math":
        problem = user_input.lower()
        # Remove common phrases to isolate the math problem
        for phrase in ["calculate", "compute", "solve", "what is", "what's", "evaluate"]:
            problem = problem.replace(phrase, "")
        problem = problem.strip()
        
        # Try to solve it with Python's eval
        try:
            # Remove any non-math characters for safety
            safe_problem = re.sub(r'[^0-9+\-*/() ]', '', problem)
            result = eval(safe_problem)
            response = f"The result is {result}"
        except:
            response = f"I couldn't solve this math problem: {problem}"
    
    elif intent == "translate":
        response = "To provide translation services, I would need access to translation APIs."
    
    elif intent == "reminder":
        # Try to extract message and time
        match = re.search(r'remind me to (.+?) (in|at) (.+)', user_input, re.IGNORECASE)
        if match:
            message = match.group(1)
            time_type = match.group(2)  # "in" or "at"
            time_str = match.group(3)
            
            response = set_reminder(message, time_str)
        else:
            response = "Please specify what you want me to remind you about and when."
    
    elif intent == "location":
        response = "To provide location services, I would need access to geolocation APIs."
    
    elif intent == "sentiment":
        sentiment = sentiment_result
        if sentiment['overall'] >= 0.05:
            emotion = "positive"
        elif sentiment['overall'] <= -0.05:
            emotion = "negative"
        else:
            emotion = "neutral"
        
        response = f"Your message seems {emotion} with a sentiment score of {sentiment['overall']:.2f}."
    
    elif intent == "stocks":
        # Extract the stock symbol
        match = re.search(r'stock price for (.+?)\b', user_input, re.IGNORECASE) or re.search(r'stock (.+?)\b', user_input, re.IGNORECASE)
        if match:
            stock_symbol = match.group(1).upper()
            response = f"To provide stock information for {stock_symbol}, I would need access to a financial data API."
        else:
            response = "Which stock would you like to check?"
    
    elif intent == "crypto":
        # Extract the cryptocurrency
        match = re.search(r'(bitcoin|ethereum|dogecoin|crypto|cryptocurrency) (.+?)\b', user_input, re.IGNORECASE)
        if match:
            crypto = match.group(1).lower()
            response = f"To provide cryptocurrency information for {crypto}, I would need access to a cryptocurrency data API."
        else:
            response = "Which cryptocurrency would you like to check?"
    
    elif intent == "currency":
        response = "To provide currency conversion, I would need access to an exchange rate API."
    
    elif intent == "summarize":
        # Extract URL if present
        url_match = re.search(r'https?://[^\s]+', user_input)
        if url_match:
            url = url_match.group(0)
            summary = web_search.summarize_article(url)
            if summary:
                response = f"Summary of '{summary['title']}':\n\n{summary['summary']}"
            else:
                response = "I couldn't summarize that article."
        else:
            response = "Please provide a URL to summarize."
    
    elif intent == "image":
        response = "I don't have image analysis capabilities at the moment."
    
    elif intent == "health":
        response = random.choice(kb.responses["health_tips"])
    
    elif intent == "trivia":
        response = random.choice(kb.responses["trivia"])
    
    elif intent == "horoscope":
        # Try to extract zodiac sign
        user_input_lower = user_input.lower()
        found_sign = None
        
        for sign in kb.zodiac_signs:
            if sign in user_input_lower:
                found_sign = sign
                break
        
        if found_sign:
            date_range = kb.zodiac_signs[found_sign]
            horoscope = random.choice(kb.horoscopes[found_sign])
            response = f"{found_sign.capitalize()} ({date_range}): {horoscope}"
        else:
            response = "Which zodiac sign would you like the horoscope for?"
    
    elif intent == "quotes":
        response = random.choice(kb.responses["quotes"])
    
    elif intent == "games":
        # Extract game name if present
        game_name = None
        for game in ["number_guess", "rock_paper_scissors", "dice_roll", "coin_flip", "word_scramble"]:
            if game.replace("_", " ") in user_input.lower():
                game_name = game
                break
        
        if game_name:
            game_result = play_game(game_name)
            if "error" in game_result:
                response = f"{game_result['error']}. Available games: {', '.join(game_result['available_games'])}"
            else:
                response = f"{game_result['description']}\n"
                if "result" in game_result:
                    response += f"Result: {game_result['result']}"
                elif "scrambled_word" in game_result:
                    response += f"Scrambled word: {game_result['scrambled_word']}"
        else:
            response = "Which game would you like to play? I know number guess, rock paper scissors, dice roll, coin flip, and word scramble."
    
    elif intent == "music":
        response = "I would play: " + random.choice(kb.responses["music"])
    
    else:
        # Default response
        response = random.choice(kb.responses["default"])
    
    # Store the chat in the database
    store_chat(user_input, response, sentiment_result['overall'], intent)
    
    return {
        "response": response,
        "intent": intent,
        "sentiment": sentiment_result,
        "entities": NLPProcessor.extract_entities_spacy(user_input)
    }

# Routes
@app.route('/')
def index():
    # ADD YOUR HTML CODE HERE - This is where you should add your HTML code for the main interface
    return render_template_string('''
   <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant</title>
    <!-- Barba.js for smooth page transitions -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/barba.js/1.0.0/barba.min.js"></script>
    <!-- GSAP for animations -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.11.4/gsap.min.js"></script>
    <!-- Font Awesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css">
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary-color: #6366f1;
            --primary-dark: #4f46e5;
            --secondary-color: #8b5cf6;
            --accent-color: #06b6d4;
            --background-color: #f8fafc;
            --chat-bg: #ffffff;
            --text-color: #1e293b;
            --light-text: #64748b;
            --message-user: #ede9fe;
            --message-user-text: #5b21b6;
            --message-bot: #e0f2fe;
            --message-bot-text: #0369a1;
            --shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
            --mike-color: #ec4899;
            --recording-color: #ef4444;
            --read-color: #10b981;
            --border-radius: 16px;
        }

        /* Dark mode colors */
        .dark-mode {
            --primary-color: #6366f1;
            --primary-dark: #4f46e5;
            --secondary-color: #8b5cf6;
            --accent-color: #06b6d4;
            --background-color: #1e293b;
            --chat-bg: #0f172a;
            --text-color: #f8fafc;
            --light-text: #cbd5e1;
            --message-user: #4c1d95;
            --message-user-text: #ede9fe;
            --message-bot: #075985;
            --message-bot-text: #e0f2fe;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Poppins', sans-serif;
            background-color: var(--background-color);
            color: var(--text-color);
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            transition: all 0.3s ease;
        }

        header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 1.2rem;
            box-shadow: var(--shadow);
            z-index: 10;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: relative;
            overflow: hidden;
        }

        header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
            transform: rotate(30deg);
            pointer-events: none;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
        }

        .app-title {
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }

        .app-icon {
            font-size: 1.8rem;
            animation: pulse 2s infinite ease-in-out;
        }

        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        .header-actions {
            display: flex;
            gap: 1rem;
        }

        .theme-toggle {
            background: none;
            border: none;
            color: white;
            font-size: 1.2rem;
            cursor: pointer;
            transition: transform 0.3s ease;
        }

        .theme-toggle:hover {
            transform: rotate(30deg);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1.5rem;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            width: 100%;
        }

        .barba-container {
            width: 100%;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }

        .chat-container {
            background-color: var(--chat-bg);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            flex-grow: 1;
            margin: 1rem auto;
            display: flex;
            flex-direction: column;
            width: 85%;
            max-width: 1000px;
            overflow: hidden;
            position: relative;
            transition: all 0.3s ease;
        }

        .chat-header {
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 1rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top-left-radius: var(--border-radius);
            border-top-right-radius: var(--border-radius);
        }

        .chat-title {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1.2rem;
        }

        .chat-status {
            display: flex;
            align-items: center;
            font-size: 0.8rem;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            margin-right: 0.5rem;
            animation: blink 1.5s infinite;
        }

        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0.4; }
            100% { opacity: 1; }
        }

        .chat-messages {
            padding: 1.5rem;
            flex-grow: 1;
            overflow-y: auto;
            max-height: 600px;
            min-height: 450px;
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
            scroll-behavior: smooth;
        }

        .message {
            max-width: 75%;
            padding: 0.9rem 1.2rem;
            border-radius: 1.2rem;
            position: relative;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }

        .message:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        .message-user {
            align-self: flex-end;
            background-color: var(--message-user);
            color: var(--message-user-text);
            border-bottom-right-radius: 0.3rem;
        }

        .message-bot {
            align-self: flex-start;
            background-color: var(--message-bot);
            color: var(--message-bot-text);
            border-bottom-left-radius: 0.3rem;
        }

        .message-actions {
            position: absolute;
            bottom: -1.5rem;
            right: 0.5rem;
            display: flex;
            gap: 0.5rem;
            opacity: 0;
            transition: opacity 0.2s ease;
        }

        .message-bot:hover .message-actions {
            opacity: 1;
        }

        .message-action {
            background: none;
            border: none;
            color: var(--light-text);
            cursor: pointer;
            font-size: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.2rem;
            padding: 0.2rem 0.5rem;
            border-radius: 12px;
            transition: all 0.2s ease;
        }

        .message-action:hover {
            background-color: rgba(0,0,0,0.05);
            color: var(--accent-color);
        }

        .message-action i {
            font-size: 0.9rem;
        }

        .message-time {
            font-size: 0.65rem;
            color: var(--light-text);
            text-align: right;
            margin-top: 0.3rem;
            opacity: 0.8;
        }

        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.5rem 1rem;
            background-color: var(--message-bot);
            border-radius: 1rem;
            align-self: flex-start;
            margin-bottom: 0.5rem;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .typing-indicator.visible {
            opacity: 1;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background-color: var(--message-bot-text);
            border-radius: 50%;
            opacity: 0.7;
        }

        .typing-dot:nth-child(1) {
            animation: bounce 1.3s infinite 0.2s;
        }
        .typing-dot:nth-child(2) {
            animation: bounce 1.3s infinite 0.4s;
        }
        .typing-dot:nth-child(3) {
            animation: bounce 1.3s infinite 0.6s;
        }

        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            30% { transform: translateY(-5px); }
        }

        .input-container {
            display: flex;
            gap: 0.7rem;
            padding: 1.2rem;
            background-color: var(--chat-bg);
            border-top: 1px solid rgba(0,0,0,0.05);
            align-items: flex-end;
        }

        .input-wrapper {
            flex-grow: 1;
            position: relative;
            display: flex;
            align-items: center;
            background-color: var(--background-color);
            border-radius: 24px;
            padding: 0 1rem;
            border: 1px solid rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }

        .input-wrapper:focus-within {
            box-shadow: 0 0 0 2px var(--primary-color);
            border-color: transparent;
        }

        .chat-input {
            flex-grow: 1;
            border: none;
            border-radius: 24px;
            padding: 0.9rem 0;
            font-size: 0.95rem;
            outline: none;
            resize: none;
            background: transparent;
            color: var(--text-color);
            font-family: 'Poppins', sans-serif;
            max-height: 120px;
        }

        .input-icon {
            color: var(--light-text);
            font-size: 1.2rem;
            padding: 0 0.5rem;
        }

        .button {
            width: 48px;
            height: 48px;
            border-radius: 50%;
            border: none;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: all 0.2s ease;
            font-size: 1.1rem;
        }

        .button:active {
            transform: scale(0.95);
        }

        .send-button {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .send-button:hover {
            background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-color) 100%);
            transform: translateY(-2px);
        }

        .mike-button {
            background: linear-gradient(135deg, var(--mike-color) 0%, #db2777 100%);
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .mike-button:hover {
            transform: translateY(-2px);
        }

        .read-button {
            background: linear-gradient(135deg, var(--read-color) 0%, #059669 100%);
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .read-button:hover {
            transform: translateY(-2px);
        }

        .mike-button.recording {
            background: linear-gradient(135deg, var(--recording-color) 0%, #b91c1c 100%);
            animation: pulse-recording 1.5s infinite;
        }

        @keyframes pulse-recording {
            0% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
            }
            70% {
                transform: scale(1.05);
                box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
            }
            100% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
            }
        }

        .tooltip {
            position: relative;
            display: inline-block;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 120px;
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            text-align: center;
            border-radius: 6px;
            padding: 6px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -60px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.75rem;
        }

        .tooltip .tooltiptext::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: rgba(0, 0, 0, 0.8) transparent transparent transparent;
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }

        .status-indicator {
            font-size: 0.85rem;
            color: var(--light-text);
            margin-left: 10px;
            padding: 0.4rem 0.8rem;
            border-radius: 1rem;
            background-color: rgba(0,0,0,0.05);
            display: none;
        }

        .status-indicator.visible {
            display: block;
            animation: fadeIn 0.3s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .page-transition {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: var(--primary-color);
            z-index: 9999;
            opacity: 0;
            pointer-events: none;
        }

        /* Suggestions */
        .suggestions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
            padding: 0 0.5rem;
        }

        .suggestion-chip {
            background-color: var(--background-color);
            color: var(--text-color);
            padding: 0.5rem 1rem;
            border-radius: 16px;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid rgba(0,0,0,0.1);
        }

        .suggestion-chip:hover {
            background-color: var(--primary-color);
            color: white;
        }

        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .chat-container {
                width: 95%;
                margin: 0.5rem auto;
            }

            .message {
                max-width: 85%;
            }

            .header-content h1 {
                font-size: 1.3rem;
            }
        }

        /* Show message actions on mobile with tap */
        @media (hover: none) {
            .message-actions {
                opacity: 0.8;
                position: relative;
                bottom: 0;
                margin-top: 0.5rem;
                justify-content: flex-end;
            }
        }

        /* Animation classes */
        .fade-in {
            animation: fadeIn 0.5s ease-out forwards;
        }

        .fade-out {
            animation: fadeOut 0.5s ease-out forwards;
        }

        @keyframes fadeOut {
            from { opacity: 1; transform: translateY(0); }
            to { opacity: 0; transform: translateY(-10px); }
        }

        .slide-in {
            animation: slideIn 0.5s ease-out forwards;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }

        .slide-out {
            animation: slideOut 0.5s ease-out forwards;
        }

        @keyframes slideOut {
            from { opacity: 1; transform: translateX(0); }
            to { opacity: 0; transform: translateX(20px); }
        }

        /* Accessibility improvements */
        .visuallyhidden {
            border: 0;
            clip: rect(0 0 0 0);
            height: 1px;
            margin: -1px;
            overflow: hidden;
            padding: 0;
            position: absolute;
            width: 1px;
        }
    </style>
</head>
<body>
    <div class="page-transition"></div>
    
    <header>
        <div class="header-content">
            <div class="app-title">
                <div class="app-icon">
                    <i class="fas fa-robot"></i>
                </div>
                <h1>AI Assistant</h1>
            </div>
            <div class="header-actions">
                <button class="theme-toggle" id="theme-toggle" aria-label="Toggle dark mode">
                    <i class="fas fa-moon"></i>
                </button>
            </div>
        </div>
    </header>

    <div id="barba-wrapper">
        <div class="barba-container">
            <div class="container">
                <div class="chat-container" data-barba="container" data-barba-namespace="chat">
                    <div class="chat-header">
                        <div class="chat-title">
                            <i class="fas fa-comment-dots"></i>
                            <span>Chat Session</span>
                        </div>
                        <div class="chat-status">
                            <div class="status-dot"></div>
                            <span>Online</span>
                        </div>
                    </div>
                    
                    <div class="chat-messages" id="chatbox">
                        <div class="message message-bot slide-in">
                            Hello! I'm your AI assistant. How can I help you today?
                            <div class="message-time">Now</div>
                            <div class="message-actions">
                                <button class="message-action" data-action="read">
                                    <i class="fas fa-volume-up"></i>
                                    <span>Read</span>
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="suggestions">
                        <div class="suggestion-chip">Tell me a joke</div>
                        <div class="suggestion-chip">Weather forecast</div>
                        <div class="suggestion-chip">Latest news</div>
                        <div class="suggestion-chip">Who is Mike?</div>
                    </div>

                    <div class="typing-indicator" id="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>

                    <div class="input-container">
                        <div class="tooltip">
                            <button class="button mike-button" id="mike-button" aria-label="Voice input">
                                <i class="fas fa-microphone"></i>
                            </button>
                            <span class="tooltiptext" id="mic-tooltip">Start Voice Input</span>
                        </div>
                        
                        <div class="input-wrapper">
                            <textarea class="chat-input" id="chat-input" placeholder="Type your message here..." rows="1" aria-label="Message input"></textarea>
                        </div>
                        
                        <div class="tooltip">
                            <button class="button send-button" id="send-button" aria-label="Send message">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                            <span class="tooltiptext">Send</span>
                        </div>
                        
                        <div class="status-indicator" id="voice-status">Listening...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script>
    document.addEventListener('DOMContentLoaded', () => {
        // Get DOM elements
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-button');
        const mikeButton = document.getElementById('mike-button');
        const chatbox = document.getElementById('chatbox');
        const voiceStatus = document.getElementById('voice-status');
        const micTooltip = document.getElementById('mic-tooltip');
        const themeToggle = document.getElementById('theme-toggle');
        const typingIndicator = document.getElementById('typing-indicator');
        const suggestions = document.querySelectorAll('.suggestion-chip');
        
        // Speech synthesis configuration
        const synth = window.speechSynthesis;
        let speaking = false;
        
        // Check if browser supports speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;
        let isRecording = false;
        
        // Initialize speech recognition if supported
        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;
            
            // Speech recognition event handlers
            recognition.onstart = function() {
                isRecording = true;
                if (mikeButton) {
                    mikeButton.classList.add('recording');
                    if (voiceStatus) voiceStatus.textContent = 'Listening...';
                    if (voiceStatus) voiceStatus.classList.add('visible');
                    if (micTooltip) micTooltip.textContent = 'Stop Voice Input';
                }
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                if (chatInput) {
                    chatInput.value = transcript;
                    if (voiceStatus) voiceStatus.textContent = 'Processing...';
                    
                    // Auto-adjust textarea height
                    chatInput.style.height = 'auto';
                    chatInput.style.height = (chatInput.scrollHeight) + 'px';
                }
            };
            
            recognition.onend = function() {
                isRecording = false;
                if (mikeButton) mikeButton.classList.remove('recording');
                if (voiceStatus) voiceStatus.classList.remove('visible');
                if (micTooltip) micTooltip.textContent = 'Start Voice Input';
                
                // Auto-send if we have text
                if (chatInput && chatInput.value.trim()) {
                    sendMessage();
                }
            };
            
            recognition.onerror = function(event) {
                if (voiceStatus) {
                    voiceStatus.textContent = 'Error: ' + event.error;
                    setTimeout(() => {
                        voiceStatus.classList.remove('visible');
                    }, 3000);
                }
                isRecording = false;
                if (mikeButton) mikeButton.classList.remove('recording');
                if (micTooltip) micTooltip.textContent = 'Start Voice Input';
            };
        } else if (mikeButton) {
            mikeButton.style.display = 'none';
            console.log('Speech recognition not supported');
        }
    
        // Theme toggle functionality
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                document.body.classList.toggle('dark-mode');
                const isDarkMode = document.body.classList.contains('dark-mode');
                themeToggle.innerHTML = isDarkMode ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
                
                // Save preference
                localStorage.setItem('darkMode', isDarkMode);
            });
            
            // Check saved theme preference
            if (localStorage.getItem('darkMode') === 'true') {
                document.body.classList.add('dark-mode');
                themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
            }
        }
    
        // Function to append a message to the chatbox
        function appendMessage(text, sender) {
            if (!chatbox) return null;
            
            const messageElement = document.createElement('div');
            messageElement.classList.add('message', sender, 'slide-in');
            messageElement.textContent = text;
            
            const timeElement = document.createElement('div');
            timeElement.classList.add('message-time');
            timeElement.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            messageElement.appendChild(timeElement);
            
            // Add read button for bot messages
            if (sender === 'message-bot') {
                const actionsDiv = document.createElement('div');
                actionsDiv.classList.add('message-actions');
                
                const readButton = document.createElement('button');
                readButton.classList.add('message-action');
                readButton.dataset.action = 'read';
                readButton.innerHTML = '<i class="fas fa-volume-up"></i><span>Read</span>';
                readButton.addEventListener('click', () => {
                    readText(text);
                });
                
                actionsDiv.appendChild(readButton);
                messageElement.appendChild(actionsDiv);
            }
            
            chatbox.appendChild(messageElement);
            chatbox.scrollTop = chatbox.scrollHeight;
            
            // Animate entry with GSAP if available
            if (typeof gsap !== 'undefined') {
                gsap.from(messageElement, {
                    opacity: 0, 
                    y: 20, 
                    duration: 0.5, 
                    ease: "power2.out"
                });
            }
            
            return messageElement;
        }
    
        // Show typing indicator function
        function showTypingIndicator() {
            if (typingIndicator) {
                typingIndicator.classList.add('visible');
                if (chatbox) chatbox.scrollTop = chatbox.scrollHeight;
            }
        }
    
        // Hide typing indicator function
        function hideTypingIndicator() {
            if (typingIndicator) {
                typingIndicator.classList.remove('visible');
            }
        }
    
        // Function to send a message to the backend
        async function sendMessage() {
            if (!chatInput) return;
            
            const message = chatInput.value.trim();
            if (!message) return;
    
            appendMessage(message, 'message-user');
            chatInput.value = '';
            chatInput.style.height = 'auto'; // Reset height
            
            // Show typing indicator
            showTypingIndicator();
    
            try {
                // Connect to the Flask backend API endpoint
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message})
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                
                const data = await response.json();
                
                // Hide typing indicator
                hideTypingIndicator();
                
                // Extract the response from the data returned by the Flask backend
                appendMessage(data.response, 'message-bot');
                
                // Log additional information if needed
                console.log('Intent detected:', data.intent);
                console.log('Sentiment:', data.sentiment);
                console.log('Entities:', data.entities);
                
            } catch (error) {
                hideTypingIndicator();
                appendMessage('Error communicating with server: ' + error.message, 'message-bot');
                console.error('Error:', error);
            }
        }
    
        // Toggle microphone function
        function toggleMic() {
            if (!recognition) return;
            
            if (isRecording) {
                recognition.stop();
            } else {
                recognition.start();
            }
        }
        
        // Function to read text using speech synthesis
        function readText(text) {
            if (!synth) return;
            
            if (speaking) {
                synth.cancel();
                speaking = false;
                return;
            }
            
            // Create speech synthesis utterance
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            
            // Use a more natural voice if available
            const voices = synth.getVoices();
            const preferredVoice = voices.find(voice => 
                voice.name.includes('Google') || voice.name.includes('Samantha') || 
                voice.name.includes('Karen') || voice.name.includes('Daniel')
            );
            
            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }
            
            // Event handlers
            utterance.onstart = () => {
                speaking = true;
            };
            
            utterance.onend = () => {
                speaking = false;
            };
            
            // Start speaking
            synth.speak(utterance);
        }
    
        // Add event listeners
        if (sendButton) {
            sendButton.addEventListener('click', sendMessage);
        }
        
        if (mikeButton) {
            mikeButton.addEventListener('click', toggleMic);
        }
        
        if (chatInput) {
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
        }
    
        // Add click handlers for suggestion chips
        if (suggestions) {
            suggestions.forEach(chip => {
                chip.addEventListener('click', () => {
                    if (chatInput) chatInput.value = chip.textContent;
                    sendMessage();
                });
            });
        }
        
        // Delegate event listener for read buttons added dynamically
        if (chatbox) {
            chatbox.addEventListener('click', (e) => {
                const target = e.target.closest('.message-action[data-action="read"]');
                if (target) {
                    const messageText = target.closest('.message').textContent
                        .replace(target.closest('.message-actions').textContent, '')
                        .replace(target.closest('.message').querySelector('.message-time').textContent, '');
                    readText(messageText);
                }
            });
        }
        
        // Voice synthesis setup - ensure voices are loaded
        if (synth && synth.onvoiceschanged !== undefined) {
            synth.onvoiceschanged = () => {
                console.log('Voices loaded');
            };
        }
        
        // Animate in the chat container using GSAP if available
        if (typeof gsap !== 'undefined') {
            const chatContainer = document.querySelector('.chat-container');
            if (chatContainer) {
                gsap.from('.chat-container', {
                    opacity: 0,
                    y: 30,
                    duration: 0.8,
                    ease: "power2.out"
                });
            }
        }
        
        // Add an initial welcome message
        setTimeout(() => {
            appendMessage("Hello! I'm your NLP Assistant. How can I help you today?", 'message-bot');
        }, 500);
    });
</script>
</body>
</html>
    ''')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
    
    result = process_input(user_input)
    return jsonify(result)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    sentiment = NLPProcessor.analyze_sentiment(text)
    entities = NLPProcessor.extract_entities_spacy(text)
    
    return jsonify({
        "sentiment": sentiment,
        "entities": entities
    })

@app.route('/api/reminders', methods=['GET'])
def reminders():
    return jsonify(get_reminders())

@app.route('/api/games', methods=['GET'])
def games():
    game_name = request.args.get('game', 'coin_flip')
    return jsonify(play_game(game_name))

if __name__ == '__main__':
    app.run(debug=True)
