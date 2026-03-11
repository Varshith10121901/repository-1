from flask import Flask, request, jsonify, render_template_string
import os
import logging
import nltk
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
    'password': '1234',  # Replace with your MySQL password
    'database': 'tommy'
}

# Initialize NLTK data
def initialize_nltk():
    """Download required NLTK data if not already present."""
    resources = ['punkt', 'wordnet', 'vader_lexicon', 'omw-1.4']
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
            logger.info(f"{resource} is already downloaded.")
        except LookupError:
            logger.info(f"Downloading {resource}...")
            nltk.download(resource, quiet=True)

# Initialize database
def initialize_database():
    """Initialize the MySQL database and ensure the correct schema."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Drop the table if it exists to ensure a fresh schema (for development)
        # Comment out in production to preserve data
        # cursor.execute("DROP TABLE IF EXISTS cluadnltk")

        # Create table with the correct schema
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

        # Verify the schema by checking column names
        cursor.execute("SHOW COLUMNS FROM cluadnltk")
        columns = [col[0] for col in cursor.fetchall()]
        required_columns = ['id', 'user_message', 'bot_response', 'timestamp', 'sentiment', 'intent']
        if not all(col in columns for col in required_columns):
            logger.error("Table schema is incorrect. Required columns: %s, Found: %s", required_columns, columns)
            raise Exception("Table schema is incorrect")

        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Function to store chat messages
def store_chat(user_message, bot_response, sentiment=0.0, intent="unknown"):
    """Store chat messages in the database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO cluadnltk (user_message, bot_response, timestamp, sentiment, intent) VALUES (%s, %s, %s, %s, %s)",
            (user_message, bot_response, datetime.now(), sentiment, intent)
        )

        conn.commit()
        logger.info("Chat stored in database")
    except Exception as e:
        logger.error(f"Database storage error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Initialize NLTK and spaCy
initialize_nltk()
lemmatizer = WordNetLemmatizer()
sentiment_analyzer = SentimentIntensityAnalyzer()

try:
    nlp = spacy.load('en_core_web_sm')
except Exception:
    logger.info("Downloading spaCy model en_core_web_sm...")
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
            "wiki": ["wiki", "tell me about", "tell about", "explain", "define"],
            "music": ["play music", "start a song", "play a song", "music please", "music"],
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
            "music": ["Blinding Lights by The Weeknd", "Bohemian Rhapsody by Queen", "Shape of You by Ed Sheeran",
                      "Levitating by Dua Lipa", "Smells Like Teen Spirit by Nirvana", "Bad Guy by Billie Eilish",
                      "Hotel California by Eagles", "Rolling in the Deep by Adele", "Uptown Funk by Bruno Mars",
                      "Hey Jude by The Beatles"],
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

        # Comprehensive capital data
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
            'aries': ["You're feeling particularly energetic today. Channel that energy into productive pursuits.",
                      "Your assertiveness will serve you well in negotiations today.",
                      "Take time to cool down before making important decisions."],
            'taurus': ["Your persistence is paying off. Keep pushing toward your goals.",
                       "Financial opportunities may present themselves today.",
                       "Take time to appreciate the beautiful things in life."],
            'gemini': ["Your communication skills are sharp today. Use them to resolve misunderstandings.",
                       "Learning something new will satisfy your curiosity.",
                       "Be mindful not to spread yourself too thin across multiple tasks."],
            'cancer': ["Your intuition is particularly strong today. Trust your gut feelings.",
                       "Focus on self-care and emotional well-being.",
                       "Home improvements or family matters may require your attention."],
            'leo': ["Your natural leadership qualities shine today. Others will look to you for guidance.",
                    "Creative pursuits will bring you joy and fulfillment.",
                    "Be mindful of the fine line between confidence and arrogance."],
            'virgo': ["Your analytical skills will help solve a complex problem.",
                      "Pay attention to details, but don't get lost in them.",
                      "Your help will be appreciated by someone in need."],
            'libra': ["Focus on finding balance in your relationships today.",
                      "Artistic endeavors will bring you satisfaction.",
                      "Don't avoid difficult decisions just to keep the peace."],
            'scorpio': ["Your intensity and focus will help you overcome obstacles.",
                        "Trust issues may arise, but open communication will help.",
                        "Your intuition about others' motives is spot on."],
            'sagittarius': ["Adventure calls! Try something new that expands your horizons.",
                            "Your optimism will inspire those around you.",
                            "Be careful not to promise more than you can deliver."],
            'capricorn': ["Your discipline and hard work are noticed by those in positions of power.",
                          "Consider the long-term impact of your current decisions.",
                          "Don't neglect your personal life while pursuing professional goals."],
            'aquarius': ["Your innovative ideas will be well-received today.",
                         "Connect with friends or groups that share your ideals.",
                         "Remember that change requires patience and persistence."],
            'pisces': ["Your compassion and empathy make you a valuable friend today.",
                       "Artistic inspiration flows freely; capture your creative ideas.",
                       "Set boundaries to protect your emotional energy."]
        }

class WebSearchEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def search_wikipedia(self, query):
        try:
            cleaned_query = re.sub(r'\b(what|who|where|is|what|who|where|when|why|which|whose|whom|how)\b', '',
                                   query, flags=re.IGNORECASE).strip()
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
        if 'intent_classifier' in globals() and intent_classifier:
            try:
                intent = intent_classifier.predict([user_input.lower()])[0]
                return intent
            except Exception as e:
                logger.error(f"Intent classifier error: {e}")

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
        scores = sentiment_analyzer.polarity_scores(text)
        blob = TextBlob(text)
        textblob_sentiment = blob.sentiment
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
        try:
            doc = nlp(text)
            return [{
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            } for ent in doc.ents]
        except Exception as e:
            logger.error(f"spaCy entity extraction error: {e}")
            return []

    @staticmethod
    def extract_noun_phrases(text):
        try:
            doc = nlp(text)
            return [chunk.text for chunk in doc.noun_chunks]
        except Exception as e:
            logger.error(f"spaCy noun phrase extraction error: {e}")
            return []

# Train intent classifier
def train_intent_classifier():
    try:
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
        intent_classifier = Pipeline([
            ('vectorizer', CountVectorizer()),
            ('classifier', MultinomialNB())
        ])
        intent_classifier.fit(X, y)
        return intent_classifier
    except Exception as e:
        logger.error(f"Error training intent classifier: {e}")
        return None

intent_classifier = train_intent_classifier()

# Reminder functions
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

        cursor.execute("SELECT * FROM reminders WHERE reminder_time > NOW() ORDER BY reminder_time")
        reminders = cursor.fetchall()

        conn.commit()
        return reminders
    except Exception as e:
        logger.error(f"Error fetching reminders: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def set_reminder(message, time_str):
    try:
        reminder_time = datetime.now()
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
            try:
                reminder_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            except:
                try:
                    reminder_time = datetime.strptime(time_str, "%H:%M")
                    reminder_time = datetime.now().replace(hour=reminder_time.hour, minute=reminder_time.minute,
                                                          second=0, microsecond=0)
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
        return f"Reminder set for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}: {message}"
    except Exception as e:
        logger.error(f"Error setting reminder: {e}")
        return f"Failed to set reminder: {str(e)}"
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

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
        return {
            "error": f"Game '{game_name}' not found",
            "available_games": list(games.keys())
        }

# Main processing function
def process_input(user_input):
    try:
        sentiment_result = NLPProcessor.analyze_sentiment(user_input)
        kb = KnowledgeBase()
        web_search = WebSearchEngine()
        intent = NLPProcessor.classify_intent(user_input, kb)
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
            city = NLPProcessor.extract_entity(user_input, ["weather in", "forecast for", "temperature in", "weather",
                                                          "forecast"])
            if city:
                response = f"To provide weather information for {city}, I need a weather API key."
            else:
                response = "Which city would you like the weather for?"
        elif intent == "capital":
            country = NLPProcessor.extract_entity(user_input, ["capital of", "what is the capital of", "capital city of"])
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
            for phrase in ["calculate", "compute", "solve", "what is", "what's", "evaluate"]:
                problem = problem.replace(phrase, "")
            problem = problem.strip()
            try:
                safe_problem = re.sub(r'[^0-9+\-*/() ]', '', problem)
                result = eval(safe_problem)
                response = f"The result is {result}"
            except:
                response = f"I couldn't solve this math problem: {problem}"
        elif intent == "translate":
            response = "To provide translation services, I would need access to translation APIs."
        elif intent == "reminder":
            match = re.search(r'remind me to (.+?) (in|at) (.+)', user_input, re.IGNORECASE)
            if match:
                message = match.group(1)
                time_str = match.group(3)
                response = set_reminder(message, time_str)
            else:
                response = "Please specify what you want me to remind you about and when."
        elif intent == "location":
            response = "To provide location services, I would need access to geolocation APIs."
        elif intent == "sentiment":
            sentiment = sentiment_result
            emotion = "positive" if sentiment['overall'] >= 0.05 else "negative" if sentiment['overall'] <= -0.05 else "neutral"
            response = f"Your message seems {emotion} with a sentiment score of {sentiment['overall']:.2f}."
        elif intent == "stocks":
            match = re.search(r'stock price for (.+?)\b', user_input, re.IGNORECASE) or re.search(r'stock (.+?)\b',
                                                                                                 user_input,
                                                                                                 re.IGNORECASE)
            if match:
                stock_symbol = match.group(1).upper()
                response = f"To provide stock information for {stock_symbol}, I would need access to a financial data API."
            else:
                response = "Which stock would you like to check?"
        elif intent == "crypto":
            match = re.search(r'(bitcoin|ethereum|dogecoin|crypto|cryptocurrency) (.+?)\b', user_input, re.IGNORECASE)
            if match:
                crypto = match.group(1).lower()
                response = f"To provide cryptocurrency information for {crypto}, I would need access to a cryptocurrency data API."
            else:
                response = "Which cryptocurrency would you like to check?"
        elif intent == "currency":
            response = "To provide currency conversion, I would need access to an exchange rate API."
        elif intent == "summarize":
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
            user_input_lower = user_input.lower()
            found_sign = next((sign for sign in kb.zodiac_signs if sign in user_input_lower), None)
            if found_sign:
                date_range = kb.zodiac_signs[found_sign]
                horoscope = random.choice(kb.horoscopes[found_sign])
                response = f"{found_sign.capitalize()} ({date_range}): {horoscope}"
            else:
                response = "Which zodiac sign would you like the horoscope for?"
        elif intent == "quotes":
            response = random.choice(kb.responses["quotes"])
        elif intent == "games":
            game_name = next((game for game in ["number_guess", "rock_paper_scissors", "dice_roll", "coin_flip",
                                                "word_scramble"] if game.replace("_", " ") in user_input.lower()), None)
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
            response = random.choice(kb.responses["default"])

        store_chat(user_input, response, sentiment_result['overall'], intent)
        return {
            "response": response,
            "intent": intent,
            "sentiment": sentiment_result,
            "entities": NLPProcessor.extract_entities_spacy(user_input)
        }
    except Exception as e:
        logger.error(f"Error processing input: {e}")
        return {
            "response": "Sorry, something went wrong.",
            "intent": "error",
            "sentiment": {"overall": 0.0},
            "entities": []
        }

# Routes
@app.route('/')
def index():
    # Initialize database before serving the page
    try:
        initialize_database()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return "Database initialization failed. Please check the server logs.", 500

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Assistant</title>
        <style>
            /* Base Variables */
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
            }

            /* Base Styles */
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background-color: var(--background-color);
                color: var(--text-color);
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                min-height: 100vh;
                transition: all 0.8s cubic-bezier(0.17, 0.84, 0.44, 1);
                overflow-x: hidden;
            }

            header {
                background: linear-gradient(135deg, #6b46c1 0%, #805ad5 100%);
                color: white;
                padding: 1.5rem 1rem;
                box-shadow: 0 4px 20px rgba(107, 70, 193, 0.4);
                z-index: 10;
                position: relative;
                transition: all 0.8s cubic-bezier(0.17, 0.84, 0.44, 1);
            }

            .header-content {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                position: relative;
            }

            .logo-section {
                display: flex;
                align-items: center;
                gap: 1rem;
            }

            .logo-icon {
                width: 40px;
                height: 40px;
                border-radius: 12px;
                background: rgba(255, 255, 255, 0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }

            .logo-text {
                font-size: 1.75rem;
                font-weight: 700;
                background: linear-gradient(to right, #ffffff, #e2e8f0);
                -webkit-background-clip: text;
                background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }

            .header-decorations {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                overflow: hidden;
                pointer-events: none;
            }

            .decoration-circle {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.1);
            }

            .decoration-1 {
                width: 150px;
                height: 150px;
                top: -50px;
                right: 10%;
            }

            .decoration-2 {
                width: 80px;
                height: 80px;
                bottom: -20px;
                left: 20%;
            }

            .decoration-3 {
                width: 120px;
                height: 120px;
                top: 40%;
                left: 5%;
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 1rem;
                display: flex;
                flex-direction: column;
                flex-grow: 1;
                position: relative;
            }

            .chat-container {
                background-color: var(--chat-bg);
                border-radius: 16px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                display: flex;
                flex-direction: column;
                flex-grow: 1;
                overflow: hidden;
                margin-bottom: 1rem;
                margin-top: 1rem;
                transition: all 0.6s cubic-bezier(0.17, 0.84, 0.44, 1);
                border: 1px solid rgba(107, 70, 193, 0.1);
                width: 165%; /* Increased by 65% from original 100% */
                max-width: 1980px; /* Ensure it doesn't exceed reasonable bounds */
            }

            .chat-header {
                padding: 1rem;
                background-color: white;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                align-items: center;
                justify-content: space-between;
                transition: all 0.6s ease;
            }

            .ai-avatar {
                width: 50px;
                height: 50px;
                border-radius: 16px;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 0.75rem;
                transition: all 0.6s ease;
                box-shadow: 0 4px 8px rgba(107, 70, 193, 0.3);
            }

            .ai-avatar svg {
                width: 28px;
                height: 28px;
                fill: white;
                transition: all 0.6s ease;
            }

            .ai-status {
                display: flex;
                flex-direction: column;
            }

            .ai-info {
                display: flex;
                align-items: center;
            }

            .ai-name {
                font-weight: 700;
                font-size: 1.25rem;
                transition: all 0.3s ease;
            }

            .ai-status-indicator {
                font-size: 0.875rem;
                color: var(--light-text);
                display: flex;
                align-items: center;
                margin-top: 4px;
            }

            .status-dot {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                background-color: #48bb78;
                margin-right: 0.5rem;
                transition: all 0.5s ease;
                position: relative;
            }
            
            .status-dot::after {
                content: '';
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                border-radius: 50%;
                background: transparent;
                border: 2px solid #48bb78;
                opacity: 0.7;
                animation: pulse 2s infinite;
            }

            .status-dot.aura-active {
                background-color: var(--aura-mode-color);
                box-shadow: 0 0 10px var(--aura-mode-color);
            }
            
            .status-dot.aura-active::after {
                border-color: var(--aura-mode-color);
            }

            .chat-messages {
                padding: 1.5rem;
                flex-grow: 1;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 1.25rem;
                max-height: 500px;
                overflow-y: auto;
                overflow-x: hidden;
                transition: background-color 0.6s ease;
                scroll-behavior: smooth;
            }

            .message {
                max-width: 80%;
                padding: 1rem 1.25rem;
                border-radius: 1.5rem;
                position: relative;
                animation: fadeIn 0.3s ease-out;
                transition: transform 0.4s ease, background-color 0.6s ease, color 0.6s ease, box-shadow 0.6s ease;
                line-height: 1.5;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .message-user {
                align-self: flex-end;
                background-color: var(--message-user);
                border-bottom-right-radius: 0.25rem;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            }

            .message-bot {
                align-self: flex-start;
                background-color: var(--message-bot);
                border-bottom-left-radius: 0.25rem;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            }

            .message-time {
                font-size: 0.7rem;
                color: var(--light-text);
                text-align: right;
                margin-top: 0.5rem;
                transition: color 0.6s ease;
            }

            .message-typing {
                display: flex;
                gap: 0.25rem;
                padding: 0.5rem;
            }

            .typing-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background-color: var(--light-text);
                animation: typingAnimation 1.5s infinite ease-in-out;
            }

            .typing-dot:nth-child(2) {
                animation-delay: 0.5s;
            }

            .typing-dot:nth-child(3) {
                animation-delay: 1s;
            }

            @keyframes typingAnimation {
                0% { transform: translateY(0); }
                50% { transform: translateY(-5px); }
                100% { transform: translateY(0); }
            }

            .input-container {
                display: flex;
                gap: 0.75rem;
                padding: 1.25rem;
                background-color: white;
                border-top: 1px solid #e2e8f0;
                transition: all 0.6s ease;
                position: relative;
            }

            .input-container::before {
                content: '';
                position: absolute;
                top: -2px;
                left: 10%;
                right: 10%;
                height: 1px;
                background: linear-gradient(to right, transparent, rgba(107, 70, 193, 0.2), transparent);
            }

            .chat-input {
                flex-grow: 1;
                border: 1px solid #e2e8f0;
                border-radius: 24px;
                padding: 0.9rem 1.25rem;
                font-size: 0.95rem;
                transition: all 0.4s ease;
                outline: none;
                resize: none;
                max-height: 120px;
                min-height: 52px;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
            }

            .chat-input:focus {
                border-color: var(--primary-color);
                box-shadow: 0 0 0 3px rgba(107, 70, 193, 0.2);
            }

            .send-button, .mic-button {
                width: 52px;
                height: 52px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                border: none;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.4s ease;
                box-shadow: 0 4px 10px rgba(107, 70, 193, 0.3);
            }

            .send-button:hover, .mic-button:hover {
                background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
                transform: translateY(-3px);
                box-shadow: 0 6px 12px rgba(107, 70, 193, 0.4);
            }

            .aura-mode-button {
                position: relative;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                border: none;
                border-radius: 30px;
                padding: 0.6rem 1.5rem;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.5s cubic-bezier(0.17, 0.84, 0.44, 1);
                display: flex;
                align-items: center;
                gap: 0.5rem;
                overflow: hidden;
                box-shadow: 0 4px 10px rgba(107, 70, 193, 0.4);
                z-index: 2;
            }

            .aura-mode-button:before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, 
                    rgba(255, 255, 255, 0) 0%, 
                    rgba(255, 255, 255, 0.1) 50%, 
                    rgba(255, 255, 255, 0) 100%);
                z-index: -1;
                transform: translateX(-100%);
                transition: transform 0.6s ease;
            }

            .aura-mode-button:hover:before {
                transform: translateX(100%);
            }

            .aura-mode-button:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 15px rgba(107, 70, 193, 0.5);
            }

            .aura-mode-button.active {
                background: linear-gradient(135deg, #f6e05e, #d69e2e);
                box-shadow: 0 0 20px rgba(214, 158, 46, 0.5);
            }

            .aura-icon {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                transition: all 0.5s ease;
            }
            
            .mic-button.active {
                background: linear-gradient(135deg, #e53e3e, #c53030);
                box-shadow: 0 4px 10px rgba(229, 62, 62, 0.5);
            }
            
            .mic-button.disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }

            .spacer {
                height: 20px;
            }

            .connection-status {
                font-size: 0.8rem;
                padding: 0.35rem 0.75rem;
                border-radius: 20px;
                display: none;
                align-items: center;
                gap: 0.35rem;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                margin-top: 1rem;
            }

            .connection-status.connected {
                display: flex;
                background-color: rgba(72, 187, 120, 0.15);
                color: #2f855a;
                border: 1px solid rgba(72, 187, 120, 0.3);
            }

            .connection-status.connecting {
                display: flex;
                background-color: rgba(237, 137, 54, 0.15);
                color: #c05621;
                border: 1px solid rgba(237, 137, 54, 0.3);
            }

            .connection-status.error {
                display: flex;
                background-color: rgba(229, 62, 62, 0.15);
                color: #c53030;
                border: 1px solid rgba(229, 62, 62, 0.3);
            }

            /* Enhanced AURA MODE transition */
            .aura-transition-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: transparent;
                z-index: 9999;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            .normal-transition-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: rgba(255, 255, 255, 0.5);
                z-index: 9999;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
            }

            @keyframes dramatic-flash {
                0% { 
                    opacity: 0; 
                    background: radial-gradient(circle at center, rgba(45, 212, 191, 0), rgba(0, 0, 0, 0));
                }
                10% { 
                    opacity: 1; 
                    background: radial-gradient(circle at center, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.8));
                }
                25% { 
                    opacity: 1; 
                    background: radial-gradient(circle at center, rgba(45, 212, 191, 0.8), rgba(45, 212, 191, 0.4));
                    transform: scale(1.05);
                }
                40% { 
                    opacity: 0.9; 
                    background: radial-gradient(circle at center, rgba(35, 35, 75, 0.8), rgba(35, 35, 75, 0.5));
                    transform: scale(1.1);
                }
                70% { 
                    opacity: 0.7; 
                    background: radial-gradient(circle at center, rgba(25, 25, 40, 0.7), rgba(25, 25, 40, 0.3));
                    transform: scale(1.1);
                }
                100% { 
                    opacity: 0; 
                    background: radial-gradient(circle at center, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0));
                    transform: scale(1);
                }
            }

            .aura-transition-overlay.flash {
                animation: dramatic-flash 1.8s forwards cubic-bezier(0.17, 0.84, 0.44, 1);
            }

            /* Floating particles for AURA mode */
            .particles-container {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 1;
                opacity: 0;
                transition: opacity 1s ease;
            }

            .particles-container.active {
                opacity: 1;
            }

            .particle {
                position: absolute;
                background: rgba(45, 212, 191, 0.6);
                border-radius: 50%;
                pointer-events: none;
                opacity: 0;
            }

            @keyframes float-up {
                0% {
                    transform: translateY(0) rotate(0deg);
                    opacity: 0;
                }
                10% {
                    opacity: 0.8;
                }
                90% {
                    opacity: 0.2;
                }
                100% {
                    transform: translateY(-100vh) rotate(360deg);
                    opacity: 0;
                }
            }

            /* Ripple effect for buttons */
            .ripple {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.7);
                transform: scale(0);
                animation: ripple 0.8s linear;
                pointer-events: none;
            }

            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }

            /* Enhanced animations for AURA Mode */
            .aura-reveal {
                animation: reveal-message 1s cubic-bezier(0.17, 0.84, 0.44, 1) forwards;
                animation-delay: var(--delay, 0s);
            }

            @keyframes reveal-message {
                0% { 
                    opacity: 0; 
                    transform: scale(0.7) translateY(30px);
                    filter: brightness(0.5) blur(5px);
                }
                30% {
                    opacity: 0.5;
                    filter: brightness(0.8) blur(2px);
                }
                70% { 
                    opacity: 1; 
                    transform: scale(1.05) translateY(-5px);
                    filter: brightness(1.2) blur(0);
                }
                100% { 
                    opacity: 1; 
                    transform: scale(1) translateY(0);
                    filter: brightness(1) blur(0);
                }
            }

            .pulse-effect {
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.05); opacity: 0.8; }
                100% { transform: scale(1); opacity: 1; }
            }

            .ai-avatar.aura-active {
                animation: avatar-pulse 4s infinite alternate;
            }

            @keyframes avatar-pulse {
                0% { 
                    transform: scale(1); 
                    box-shadow: 0 0 10px var(--aura-mode-color);
                }
                50% { 
                    transform: scale(1.1);
                    box-shadow: 0 0 20px var(--aura-mode-color), 0 0 35px var(--aura-mode-color);
                }
                100% { 
                    transform: scale(1); 
                    box-shadow: 0 0 10px var(--aura-mode-color);
                }
            }

            /* AURA MODE enhanced styles */
            body.aura-active {
                background-color: #0c1222;
            }

            body.aura-active header {
                background: linear-gradient(135deg, #1a1a3a 0%, #2d3748 100%);
                box-shadow: 0 0 25px rgba(45, 212, 191, 0.3);
            }

            body.aura-active .decoration-circle {
                background: rgba(45, 212, 191, 0.1);
            }

            body.aura-active .chat-container {
                background-color: #1a202c;
                box-shadow: 0 0 35px rgba(45, 212, 191, 0.3);
                border: 1px solid rgba(45, 212, 191, 0.5);
                transform: translateY(-5px);
            }

            body.aura-active .chat-header,
            body.aura-active .input-container {
                background-color: #1e2533;
                border-color: #2d3748;
            }
            
            body.aura-active .input-container::before {
                background: linear-gradient(to right, transparent, rgba(45, 212, 191, 0.3), transparent);
            }

            body.aura-active .ai-name {
                color: var(--aura-mode-color);
                text-shadow: 0 0 8px rgba(45, 212, 191, 0.7);
            }

            body.aura-active .message-bot {
                background-color: #2d3748;
                color: white;
                box-shadow: 0 2px 15px rgba(0, 0, 0, 0.3);
            }

            body.aura-active .message-user {
                background-color: var(--aura-mode-color);
                color: #0c1222;
                box-shadow: 0 2px 15px rgba(45, 212, 191, 0.3);
            }

            body.aura-active .chat-input {
                background-color: #2d3748;
                border-color: #4a5568;
                color: white;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
            }

            body.aura-active .chat-input::placeholder {
                color: #a0aec0;
            }

            body.aura-active .send-button, 
            body.aura-active .mic-button {
                background: linear-gradient(135deg, var(--aura-mode-color), #1a9e8f);
                box-shadow: 0 0 15px rgba(45, 212, 191, 0.5);
            }

            body.aura-active .send-button:hover, 
            body.aura-active .mic-button:hover {
                transform: translateY(-3px);
                box-shadow: 0 5px 20px rgba(45, 212, 191, 0.7);
                background: linear-gradient(135deg, #3abeae, var(--aura-mode-color));
            }

            /* Radial pulse behind button */
            .aura-mode-button .button-glow {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 100%;
                height: 100%;
                background: radial-gradient(circle, rgba(45, 212, 191, 0.8) 0%, rgba(45, 212, 191, 0) 70%);
                border-radius: 30px;
                opacity: 0;
                transition: opacity 0.5s ease;
                z-index: -1;
            }

            .aura-mode-button.active .button-glow {
                animation: glow-pulse 2s infinite alternate;
            }

            @keyframes glow-pulse {
                0% {
                    opacity: 0.3;
                    transform: translate(-50%, -50%) scale(1);
                }
                100% {
                    opacity: 0.6;
                    transform: translate(-50%, -50%) scale(1.3);
                }
            }

            @media (max-width: 768px) {
                .container {
                    padding: 0.5rem;
                }

                .chat-messages {
                    max-height: 400px;
                    padding: 1rem;
                }

                .message {
                    max-width: 90%;
                    padding: 0.8rem 1rem;
                }
                
                .header-content {
                    flex-direction: column;
                    gap: 1rem;
                    align-items: center;
                    text-align: center;
                }
                
                .logo-section {
                    margin-bottom: 0.5rem;
                }

                .chat-container {
                    width: 100%; /* Override for mobile to prevent overflow */
                }
            }
        </style>
    </head>
    <body>
        <!-- Transition overlays -->
        <div class="aura-transition-overlay" id="auraOverlay"></div>
        <div class="normal-transition-overlay" id="normalOverlay"></div>
        
        <!-- Floating particles container for AURA mode -->
        <div class="particles-container" id="particlesContainer"></div>

        <header>
            <div class="header-content">
                <div class="logo-section">
                    <div class="logo-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="white">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-5-8a5 5 0 1 1 10 0 5 5 0 0 1-10 0z"/>
                        </svg>
                    </div>
                    <h1 class="logo-text">AI Assistant</h1>
                </div>
                <button id="auraModeBtn" class="aura-mode-button">
                    <div class="button-glow"></div>
                    <span class="aura-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="5"></circle>
                            <line x1="12" y1="1" x2="12" y2="3"></line>
                            <line x1="12" y1="21" x2="12" y2="23"></line>
                            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                            <line x1="1" y1="12" x2="3" y2="12"></line>
                            <line x1="21" y1="12" x2="23 Wallpapers and Backgrounds for Your Screen
            </div>
        </header>

        <div class="container">
            <div id="connectionStatus" class="connection-status">
                <span id="connectionDot" class="status-dot"></span>
                <span id="connectionText">Not connected</span>
            </div>

            <div class="spacer"></div>

            <div class="chat-container">
                <div class="chat-header">
                    <div class="ai-info">
                        <div class="ai-avatar">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-14c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z"/>
                            </svg>
                        </div>
                        <div class="ai-status">
                            <div class="ai-name">AI Assistant</div>
                            <div class="ai-status-indicator">
                                <div id="statusDot" class="status-dot"></div>
                                <span id="statusText">Online</span>
                            </div>
                        </div>
                    </div>
                    <div id="auraModeStatus" style="font-size: 0.75rem; color: var(--light-text);">Standard Mode</div>
                </div>

                <div class="chat-messages chatbox">
                    <div class="message message-bot">
                        Hello! I'm your AI assistant. How can I help you today?
                        <div class="message-time">10:05 AM</div>
                    </div>
                    <div class="welcome-message" style="display: none;"></div>
                </div>

                <div class="input-container">
                    <textarea class="chat-input" placeholder="Type your message here..." rows="1"></textarea>
                    <button class="mic-button">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                            <line x1="12" y1="19" x2="12" y2="23"></line>
                            <line x1="8" y1="23" x2="16" y2="23"></line>
                        </svg>
                    </button>
                    <button class="send-button">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                </div>
            </div>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function () {
        // DOM Elements
        const chatInput = document.querySelector('.chat-input');
        const sendButton = document.querySelector('.send-button');
        const micButton = document.querySelector('.mic-button');
        const chatbox = document.querySelector('.chatbox');
        const welcomeMessage = document.querySelector('.welcome-message');
        const auraModeBtn = document.querySelector('#auraModeBtn');

        // Check if elements exist before using them
        if (!chatInput || !sendButton || !chatbox) {
            console.error('Critical chat elements not found. Check your HTML structure.');
            return; // Stop execution if critical elements are missing
        }

        let auraMode = false;
        let isBotResponding = false; // Flag to track if the bot is currently responding

        // Speech Recognition Setup
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition;
        let isListening = false;

        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
        } else {
            console.error("Your browser doesn't support speech recognition. Try Chrome or Edge.");
            if (micButton) micButton.classList.add("disabled");
        }

        // Function to safely append messages to the chatbox
        function appendMessage(text, sender) {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message', sender);
            
            // Create text content
            messageElement.textContent = text;
            
            // Add time element
            const timeElement = document.createElement('div');
            timeElement.classList.add('message-time');
            const now = new Date();
            timeElement.textContent = now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            messageElement.appendChild(timeElement);
            
            chatbox.appendChild(messageElement);
            requestAnimationFrame(() => {
                chatbox.scrollTop = chatbox.scrollHeight;
            });
            if (welcomeMessage) {
                welcomeMessage.style.display = 'none';
            }
        }

        // Function to handle user input
        function handleUserInput() {
            if (isBotResponding) return;
            const userText = chatInput.value.trim();
            if (!userText) return;
            appendMessage(userText, 'message-user');
            chatInput.value = '';
            isBotResponding = true;
            
            // Send the message to the server
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({message: userText}),
            })
            .then(response => response.json())
            .then(data => {
                appendMessage(data.response, 'message-bot');
                isBotResponding = false;
                chatInput.focus();
            })
            .catch((error) => {
                console.error('Error:', error);
                appendMessage('Sorry, there was an error processing your request.', 'message-bot');
                isBotResponding = false;
            });
        }

        // Event listeners
        sendButton.addEventListener('click', function (e) {
            e.preventDefault();
            handleUserInput();
        });

        chatInput.addEventListener('keypress', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                handleUserInput();
            }
        });

        // Voice recognition events
        if (recognition && micButton) {
            micButton.addEventListener('click', function (e) {
                e.preventDefault();
                if (isListening) {
                    recognition.stop();
                } else {
                    recognition.start();
                }
            });

            recognition.onstart = function () {
                if (micButton) micButton.classList.add("active");
                isListening = true;
            };

            recognition.onresult = function (event) {
                let transcript = event.results[0][0].transcript;
                chatInput.value = transcript;
                handleUserInput();
            };

            recognition.onend = function () {
                if (micButton) micButton.classList.remove("active");
                isListening = false;
            };

            recognition.onerror = function (event) {
                console.error('Speech recognition error:', event.error);
                if (micButton) micButton.classList.remove("active");
                isListening = false;
            };
        }

        // AURA Mode toggle
        if (auraModeBtn) {
            auraModeBtn.addEventListener('click', function (e) {
                e.preventDefault();
                toggleAuraMode();
            });
        }

        // Function to toggle AURA Mode
        function toggleAuraMode() {
            auraMode = !auraMode;
            const body = document.body;
            const auraOverlay = document.getElementById('auraOverlay');
            const normalOverlay = document.getElementById('normalOverlay');
            const particlesContainer = document.getElementById('particlesContainer');
            const auraModeStatus = document.getElementById('auraModeStatus');
            const statusDot = document.getElementById('statusDot');

            if (auraMode) {
                // Activate AURA Mode
                body.classList.add('aura-active');
                auraModeBtn.classList.add('active');
                auraModeBtn.textContent = 'Standard Mode';
                auraModeStatus.textContent = 'AURA Mode';
                statusDot.classList.add('aura-active');
                auraOverlay.classList.add('flash');

                // Create floating particles
                createParticles();

                // Remove flash effect after animation
                setTimeout(() => {
                    auraOverlay.classList.remove('flash');
                }, 1800);
            } else {
                // Deactivate AURA Mode
                body.classList.remove('aura-active');
                auraModeBtn.classList.remove('active');
                auraModeBtn.innerHTML = `
                    <div class="button-glow"></div>
                    <span class="aura-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="5"></circle>
                            <line x1="12" y1="1" x2="12" y2="3"></line>
                            <line x1="12" y1="21" x2="12" y2="23"></line>
                            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                            <line x1="1" y1="12" x2="3" y2="12"></line>
                            <line x1="21" y1="12" x2="23" y2="12"></line>
                            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                        </svg>
                    </span>
                    AURA Mode
                `;
                auraModeStatus.textContent = 'Standard Mode';
                statusDot.classList.remove('aura-active');
                normalOverlay.style.opacity = '1';

                // Remove particles
                particlesContainer.innerHTML = '';
                particlesContainer.classList.remove('active');

                // Fade out normal overlay
                setTimeout(() => {
                    normalOverlay.style.opacity = '0';
                }, 300);
            }

            // Apply reveal animation to existing messages
            const messages = document.querySelectorAll('.message');
            messages.forEach((msg, index) => {
                msg.style.setProperty('--delay', `${index * 0.1}s`);
                msg.classList.add('aura-reveal');
                setTimeout(() => {
                    msg.classList.remove('aura-reveal');
                }, 1000 + index * 100);
            });
        }

        // Function to create floating particles
        function createParticles() {
            const particlesContainer = document.getElementById('particlesContainer');
            particlesContainer.classList.add('active');
            const particleCount = 20;

            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.classList.add('particle');
                const size = Math.random() * 10 + 5;
                particle.style.width = `${size}px`;
                particle.style.height = `${size}px`;
                particle.style.left = `${Math.random() * 100}%`;
                particle.style.animation = `float-up ${Math.random() * 5 + 3}s infinite`;
                particle.style.animationDelay = `${Math.random() * 5}s`;
                particlesContainer.appendChild(particle);
            }
        }

        // Ripple effect for buttons
        function createRipple(event, button) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            button.appendChild(ripple);

            const diameter = Math.max(button.clientWidth, button.clientHeight);
            const radius = diameter / 2;

            ripple.style.width = ripple.style.height = `${diameter}px`;
            ripple.style.left = `${event.clientX - button.getBoundingClientRect().left - radius}px`;
            ripple.style.top = `${event.clientY - button.getBoundingClientRect().top - radius}px`;

            setTimeout(() => {
                ripple.remove();
            }, 800);
        }

        // Add ripple effect to buttons
        [sendButton, micButton, auraModeBtn].forEach(button => {
            if (button) {
                button.addEventListener('click', (e) => {
                    createRipple(e, button);
                });
            }
        });

        // Auto-resize textarea
        chatInput.addEventListener('input', function () {
            this.style.height = 'auto';
            this.style.height = `${this.scrollHeight}px`;
        });

        // Initialize connection status
        const connectionStatus = document.getElementById('connectionStatus');
        const connectionDot = document.getElementById('connectionDot');
        const connectionText = document.getElementById('connectionText');

        function updateConnectionStatus(status) {
            connectionStatus.classList.remove('connected', 'connecting', 'error');
            connectionDot.classList.remove('aura-active');

            if (status === 'connected') {
                connectionStatus.classList.add('connected');
                connectionText.textContent = 'Connected';
                connectionDot.style.backgroundColor = '#48bb78';
                if (auraMode) connectionDot.classList.add('aura-active');
            } else if (status === 'connecting') {
                connectionStatus.classList.add('connecting');
                connectionText.textContent = 'Connecting...';
                connectionDot.style.backgroundColor = '#ed8936';
            } else {
                connectionStatus.classList.add('error');
                connectionText.textContent = 'Connection Error';
                connectionDot.style.backgroundColor = '#e53e3e';
            }
        }

        // Simulate connection status
        updateConnectionStatus('connecting');
        setTimeout(() => {
            updateConnectionStatus('connected');
        }, 1000);

        // Focus input on page load
        chatInput.focus();
    });
        </script>
    </body>
    </html>
    ''')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400

        user_message = data['message']
        result = process_input(user_message)
        return jsonify(result)
    except Exception as e:
        logger.error(f"API chat error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
   initialize_database()
   app.run(debug=True, host='0.0.0.0', port=5000)
