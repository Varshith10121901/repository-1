from flask import Flask, render_template_string, request, jsonify
import nltk
import random
import string
import pyjokes
import requests
import json
import time
import wikipedia
import re
from datetime import datetime
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from bs4 import BeautifulSoup
import feedparser

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

# User agent for web requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
HEADERS = {'User-Agent': USER_AGENT}

# Knowledge Base and Responses
knowledge_base = {
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
    
    "music": ["play music", "song recommendation", "music artist", "album", "playlist", "genres"],
    
    "movies": ["movie recommendation", "film suggestion", "tv show", "actor", "director", "cinema", "what to watch"],
    
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

responses = {
    "greetings": ["Hello!", "Hi there!", "Hey!", "Good day!"],
    "farewells": ["Goodbye!", "See you later!", "Bye!", "Take care!", "Farewell!"],
    "about_me": ["I'm a helpful chatbot designed to assist with your questions.", "I can provide information and have conversations.", "I'm here to help you find answers."],
    "weather": ["Let me check the weather for you."],
    "capital": {
        "france": "Paris", "japan": "Tokyo", "germany": "Berlin", "australia": "Canberra", "canada": "Ottawa", 
        "brazil": "Brasília", "india": "new delhi", "united kingdom": "London", "united states": "Washington, D.C.", 
        "china": "Beijing", "russia": "Moscow", "italy": "Rome", "spain": "Madrid", "south africa": "Pretoria", 
        "argentina": "Buenos Aires", "mexico": "Mexico City", "egypt": "Cairo", "nigeria": "Abuja", 
        "saudi arabia": "Riyadh", "indonesia": "Jakarta", "turkey": "Ankara", "south korea": "Seoul", 
        "netherlands": "Amsterdam", "belgium": "Brussels", "switzerland": "Bern", "sweden": "Stockholm", 
        "norway": "Oslo", "denmark": "Copenhagen", "finland": "Helsinki", "greece": "Athens", 
        "portugal": "Lisbon", "ireland": "Dublin", "austria": "Vienna", "poland": "Warsaw", 
        "hungary": "Budapest", "czech republic": "Prague", "slovakia": "Bratislava", "romania": "Bucharest", 
        "bulgaria": "Sofia", "croatia": "Zagreb", "serbia": "Belgrade", "albania": "Tirana", 
        "ukraine": "Kyiv", "belarus": "Minsk", "kazakhstan": "Nur-Sultan", "uzbekistan": "Tashkent", 
        "iran": "Tehran", "thailand": "Bangkok", "vietnam": "Hanoi", "philippines": "Manila", 
        "malaysia": "Kuala Lumpur", "singapore": "Singapore", "new zealand": "Wellington", 
        "chile": "Santiago", "colombia": "Bogotá", "peru": "Lima", "venezuela": "Caracas", 
        "ecuador": "Quito", "bolivia": "Sucre", "paraguay": "Asunción", "uruguay": "Montevideo", 
        "kenya": "Nairobi", "ethiopia": "Addis Ababa", "morocco": "Rabat", "algeria": "Algiers", 
        "tunisia": "Tunis", "ghana": "Accra", "ivory coast": "Yamoussoukro", "cameroon": "Yaoundé", 
        "democratic republic of the congo": "Kinshasa", "angola": "Luanda", "zambia": "Lusaka", 
        "zimbabwe": "Harare", "uganda": "Kampala", "tanzania": "Dodoma", "sudan": "Khartoum", 
        "afghanistan": "Kabul", "iraq": "Baghdad", "syria": "Damascus", "jordan": "Amman", 
        "israel": "Jerusalem", "lebanon": "Beirut", "oman": "Muscat", "kuwait": "Kuwait City", 
        "qatar": "Doha", "bahrain": "Manama", "united arab emirates": "Abu Dhabi", 
        "yemen": "Sana'a", "nepal": "Kathmandu", "sri lanka": "Sri Jayawardenepura Kotte", 
        "myanmar": "Naypyidaw", "cambodia": "Phnom Penh", "laos": "Vientiane", 
        "bangladesh": "Dhaka", "pakistan": "Islamabad", "mongolia": "Ulaanbaatar"
    },
    "joke": [],  # Jokes will be added dynamically
    "map": ["Opening map..."],
    "default": ["I'm sorry, I don't understand.", "Could you please rephrase that?", "I'm still learning.", "Can you provide more details?", "I don't have that information."],
}

class WebSearchEngine:
    """Handle web-based information retrieval"""
    
    @staticmethod
    def search_wikipedia(query):
        """Search Wikipedia for information on a topic"""
        try:
            # Remove common question words and search related terms
            cleaned_query = re.sub(r'\b(what|who|where|when|why|how|is|are|was|were|tell me about|define|information on)\b', '', query, flags=re.IGNORECASE).strip()
            
            # Search Wikipedia
            search_results = wikipedia.search(cleaned_query, results=1)
            if not search_results:
                return None
                
            # Get the page and summary
            page = wikipedia.page(search_results[0])
            summary = wikipedia.summary(search_results[0], sentences=3)
            
            return {
                'title': page.title,
                'summary': summary,
                'url': page.url
            }
        except Exception as e:
            print(f"Wikipedia error: {e}")
            return None
    
    @staticmethod
    def search_web(query, num_results=3):
        """Search the web for information"""
        try:
            # Note: This is a mock response for this example
            # In production, you would implement a proper search API
            results = [
                f"https://example.com/search-result-1-for-{query.replace(' ', '-')}",
                f"https://example.com/search-result-2-for-{query.replace(' ', '-')}",
                f"https://example.com/search-result-3-for-{query.replace(' ', '-')}"
            ]
            return results[:num_results]
        except Exception as e:
            print(f"Web search error: {e}")
            return []
    
    @staticmethod
    def get_web_content(url):
        """Get content from a webpage"""
        try:
            response = requests.get(url, headers=HEADERS, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading and trailing space
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit to first 1000 characters for summary
            return text[:1000] + "..." if len(text) > 1000 else text
        except Exception as e:
            print(f"Web content error: {e}")
            return None
    
    @staticmethod
    def get_news_headlines(category="general"):
        """Get the latest news headlines"""
        try:
            # Use RSS feeds for different news categories
            rss_urls = {
                "general": "http://rss.cnn.com/rss/edition.rss",
                "technology": "http://rss.cnn.com/rss/edition_technology.rss",
                "sports": "http://rss.cnn.com/rss/edition_sport.rss",
                "entertainment": "http://rss.cnn.com/rss/edition_entertainment.rss",
                "health": "http://rss.cnn.com/rss/edition_health.rss",
            }
            
            url = rss_urls.get(category.lower(), rss_urls["general"])
            news_feed = feedparser.parse(url)
            
            headlines = []
            for entry in news_feed.entries[:5]:  # Get top 5 headlines
                headlines.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if 'published' in entry else 'Unknown date'
                })
                
            return headlines
        except Exception as e:
            print(f"News error: {e}")
            return []
    
    @staticmethod
    def get_stock_price(symbol):
        """Get current stock price information"""
        try:
            url = f"https://finance.yahoo.com/quote/{symbol}"
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get the stock price
            price_element = soup.find('fin-streamer', {'data-symbol': symbol, 'data-field': 'regularMarketPrice'})
            if price_element:
                price = price_element.text
                
                # Get additional info (change, percent)
                change_element = soup.find('fin-streamer', {'data-symbol': symbol, 'data-field': 'regularMarketChange'})
                percent_element = soup.find('fin-streamer', {'data-symbol': symbol, 'data-field': 'regularMarketChangePercent'})
                
                change = change_element.text if change_element else "N/A"
                percent = percent_element.text if percent_element else "N/A"
                
                return f"${price} ({change} / {percent})"
            return "Could not retrieve stock price."
        except Exception as e:
            print(f"Stock error: {e}")
            return "Could not retrieve stock price."
    
    @staticmethod
    def get_currency_exchange(from_currency, to_currency):
        """Get currency exchange rate"""
        try:
            url = f"https://www.xe.com/currencyconverter/convert/?Amount=1&From={from_currency}&To={to_currency}"
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract the exchange rate
            rate_element = soup.find('p', {'class': 'result__BigRate-sc-1bsijpp-1'})
            if rate_element:
                return rate_element.text
            return "Could not retrieve exchange rate."
        except Exception as e:
            print(f"Currency error: {e}")
            return "Could not retrieve exchange rate."

def preprocess(text):
    """Preprocess text for NLP tasks"""
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
        response.raise_for_status()
        data = response.json()
        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        return f"The temperature in {city} is {temperature}°C with {description}. Humidity is {humidity}%, wind speed is {wind_speed} m/s."
    except requests.exceptions.RequestException as e:
        # Fallback to web scraping
        try:
            city_formatted = city.replace(" ", "+")
            url = f"https://www.weather-forecast.com/locations/{city_formatted}/forecasts/latest"
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, 'html.parser')
            forecast = soup.find('p', {'class': 'b-forecast__table-description-content'})
            if forecast:
                return forecast.text
            return f"Sorry, I couldn't retrieve weather information for {city}."
        except Exception:
            return f"Sorry, I couldn't retrieve weather information for {city}."
    except (KeyError, IndexError):
        return f"Sorry, I couldn't parse the weather data for {city}."

def format_headlines(headlines):
    """Format news headlines for display"""
    if not headlines:
        return "Sorry, I couldn't retrieve any news headlines at the moment."
        
    result = "Here are the latest headlines:\n\n"
    for i, headline in enumerate(headlines, 1):
        result += f"{i}. {headline['title']}\n"
    
    return result

def extract_entity(user_input, intent_keywords):
    """Extract specific entity from user input by removing intent keywords"""
    for keyword in intent_keywords:
        if keyword in user_input.lower():
            # Split the input at the keyword
            parts = user_input.lower().split(keyword, 1)
            if len(parts) > 1:
                return parts[1].strip()
    
    # If no specific format is found, return the input without the intent keywords
    words = user_input.split()
    non_intent_words = [word for word in words if word.lower() not in [w for sublist in intent_keywords for w in w.split()]]
    return " ".join(non_intent_words).strip()

def classify_intent(user_input):
    """Determine the intent of the user's input"""
    user_tokens = preprocess(user_input)
    
    # Direct keyword matching
    for intent, keywords in knowledge_base.items():
        for keyword in keywords:
            keyword_tokens = preprocess(keyword)
            if all(token in user_tokens for token in keyword_tokens):
                return intent
    
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
        return "unknown"
    else:
        for intent, keywords in knowledge_base.items():
            if all_texts_flat[index] in keywords:
                return intent
                
    return "unknown"

def get_response(user_input):
    """Generate a response based on the user's input"""
    start_time = time.time()
    intent = classify_intent(user_input)
    web_search = WebSearchEngine()
    
    # Handle specific intents
    if intent == "capital":
        for country in responses["capital"]:
            if country in user_input.lower():
                response = f"The capital of {country.title()} is {responses['capital'][country]}."
                break
        else:
            response = "Please specify which country's capital you want."

    elif intent == "weather":
        city = extract_entity(user_input, knowledge_base["weather"])
        response = get_weather(city)

    elif intent == "joke":
        response = pyjokes.get_joke()

    elif intent == "map":
        location = extract_entity(user_input, knowledge_base["map"])
        response = f"I would show you a map of {location}, but I can't open a browser here. Try searching for it online!"
        
    elif intent == "time":
        current_time = datetime.now().strftime("%H:%M:%S")
        response = f"The current time is {current_time}."
        
    elif intent == "date":
        current_date = datetime.now().strftime("%A, %B %d, %Y")
        response = f"Today is {current_date}."
        
    elif intent == "news":
        category = "general"
        for cat in ["technology", "sports", "entertainment", "health"]:
            if cat in user_input.lower():
                category = cat
        headlines = web_search.get_news_headlines(category)
        response = format_headlines(headlines)
        
    elif intent == "search":
        query = extract_entity(user_input, knowledge_base["search"])
        results = web_search.search_web(query)
        if results:
            response = f"Here are some results for '{query}':\n\n"
            for i, url in enumerate(results, 1):
                response += f"{i}. {url}\n"
        else:
            response = f"I couldn't find any results for '{query}'."
        
    elif intent == "wiki" or intent == "definition":
        query = extract_entity(user_input, knowledge_base["wiki"] + knowledge_base["definition"])
        wiki_result = web_search.search_wikipedia(query)
        if wiki_result:
            response = f"{wiki_result['title']}: {wiki_result['summary']}\n\nSource: {wiki_result['url']}"
        else:
            # Fallback to web search
            results = web_search.search_web(query, num_results=1)
            if results:
                content = web_search.get_web_content(results[0])
                if content:
                    response = f"Information about '{query}':\n\n{content[:500]}...\n\nSource: {results[0]}"
                else:
                    response = f"I couldn't find detailed information about '{query}'."
            else:
                response = f"I couldn't find information about '{query}'."
        
    elif intent == "stock":
        symbol = extract_entity(user_input, knowledge_base["stock"])
        # Clean up symbol
        symbol = symbol.upper().strip()
        response = f"The current price for {symbol} is {web_search.get_stock_price(symbol)}"
        
    elif intent == "currency":
        # Try to extract currency codes from the query
        query = user_input.lower()
        from_currency = None
        to_currency = None
        
        # Look for common currency codes
        currency_codes = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR"]
        for code in currency_codes:
            if code.lower() in query:
                if from_currency is None:
                    from_currency = code
                else:
                    to_currency = code
                    break
                    
        if from_currency and to_currency:
            response = f"The exchange rate from {from_currency} to {to_currency} is {web_search.get_currency_exchange(from_currency, to_currency)}"
        else:
            response = "Please specify the currencies you want to convert (e.g., USD to EUR)."
        
    elif intent in responses:
        response = random.choice(responses[intent]) 
    
    else:
        # For unknown intents, try to find information online
        wiki_result = web_search.search_wikipedia(user_input)
        if wiki_result:
            response = f"{wiki_result['title']}: {wiki_result['summary']}\n\nSource: {wiki_result['url']}"
        else:  
            # If nothing else works, search the web
            results = web_search.search_web(user_input, num_results=1)
            if results:
                content = web_search.get_web_content(results[0])
                if content:
                    response = f"I found this online:\n\n{content[:500]}...\n\nSource: {results[0]}"
                else:
                    response = random.choice(responses["default"])
            else:
                response = random.choice(responses["default"])
    
    end_time = time.time()
    response_time = end_time - start_time
    
    return {"response": response, "time": response_time}

# HTML template as a string
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NLP Chatbot</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        
        .chat-container {
            width: 90%;
            max-width: 800px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            height: 80vh;
        }
        
        .chat-header {
            background-color: #4285f4;
            color: white;
            padding: 15px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }
        
        .chat-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 20px;
            max-width: 70%;
            word-wrap: break-word;
        }
        
        .user-message {
            background-color: #e6f2ff;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }
        
        .bot-message {
            background-color: #f0f0f0;
            margin-right: auto;
            border-bottom-left-radius: 5px;
        }
        
        .chat-input {
            display: flex;
            padding: 15px;
            border-top: 1px solid #e0e0e0;
        }
        
        #user-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
        }
        
        #send-button {
            background-color: #4285f4;
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            margin-left: 10px;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        #send-button:hover {
            background-color: #3367d6;
        }
        
        .response-time {
            font-size: 12px;
            color: #666;
            text-align: right;
            margin-top: 5px;
        }
        
        .typing-indicator {
            display: none;
            padding: 10px 15px;
            background-color: #f0f0f0;
            border-radius: 20px;
            margin-bottom: 15px;
            width: fit-content;
            border-bottom-left-radius: 5px;
        }
        
        .dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #888;
            margin-right: 3px;
            animation: wave 1.3s linear infinite;
        }
        
        .dot:nth-child(2) {
            animation-delay: -1.1s;
        }
        
        .dot:nth-child(3) {
            animation-delay: -0.9s;
        }
        
        @keyframes wave {
            0%, 60%, 100% { transform: initial; }
            30% { transform: translateY(-10px); }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>NLP Chatbot</h1>
        </div>
        <div class="chat-messages" id="chat-messages">
            <div class="message bot-message">
                Hello! I'm your NLP chatbot. How can I help you today?
            </div>
            <div class="typing-indicator" id="typing-indicator">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
            </div>
        </div>
        <div class="chat-input">
            <input type="text" id="user-input" placeholder="Type your message here...">
            <button id="send-button">➤</button>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const chatMessages = document.getElementById('chat-messages');
            const userInput = document.getElementById('user-input');
            const sendButton = document.getElementById('send-button');
            const typingIndicator = document.getElementById('typing-indicator');
            
            function sendMessage() {
                const message = userInput.value.trim();
                if (message === '') return;
                
                // Add user message to chat
                addMessage(message, 'user');
                userInput.value = '';
                
                // Show typing indicator
                typingIndicator.style.display = 'block';
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // Send message to server
                fetch('/get_response', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message }),
                })
                .then(response => response.json())
                .then(data => {
                    // Hide typing indicator
                    typingIndicator.style.display = 'none';
                    
                    // Add bot response to chat
                    addMessage(data.response, 'bot', data.time);
                })
                .catch(error => {
                    console.error('Error:', error);
                    typingIndicator.style.display = 'none';
                    addMessage('Sorry, there was an error processing your request.', 'bot');
                });
            }
            
            function addMessage(content, sender, responseTime) {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message');
                messageDiv.classList.add(sender + '-message');
                
                // Process potential line breaks in the message content
                const formattedContent = content.replace(/\n/g, '<br>');
                messageDiv.innerHTML = formattedContent;
                
                chatMessages.appendChild(messageDiv);
                
                // Add response time for bot messages
                if (sender === 'bot' && responseTime) {
                    const timeDiv = document.createElement('div');
                    timeDiv.classList.add('response-time');
                    timeDiv.textContent = `Response time: ${responseTime.toFixed(2)}s`;
                    messageDiv.appendChild(timeDiv);
                }
                
                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Event listeners
            sendButton.addEventListener('click', sendMessage);
            
            userInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Focus input on page load
            userInput.focus();
        });
    </script>
</body>
</html>
'''

# Flask app routes
app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_message = request.json.get('message', '')
    result = get_response(user_message)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)