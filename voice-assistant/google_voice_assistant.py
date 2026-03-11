import datetime
import webbrowser
import os
import random
import wikipedia
import pyjokes
import time
import requests
import json
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class Chatbot:
    def __init__(self, name="ChatBot", gemini_api_key=None):
        self.name = name
        self.gemini_api_key = gemini_api_key
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        
        # Set speech rate and volume
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 1.0)
        
        # Get available voices and set a female voice if available
        voices = self.engine.getProperty('voices')
        if len(voices) > 1:  # Usually index 1 is a female voice
            self.engine.setProperty('voice', voices[1].id)
            
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Setup Gemini if API key is provided
        if self.gemini_api_key:
            self.setup_gemini()
        
        # Greeting phrases
        self.greetings = [
            f"Hello, I'm {self.name}. How can I help you?",
            f"Hi there! {self.name} at your service.",
            f"Hey! {self.name} is ready to assist you."
        ]
    
    def setup_gemini(self):
        """Setup Gemini AI model"""
        genai.configure(api_key=self.gemini_api_key)
        
        # Set up the model
        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        self.gemini_model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Initialize chat session
        self.chat = self.gemini_model.start_chat(history=[])
        print(f"{self.name}: Gemini AI integration is active!")
    
    def respond(self, text):
        """Print the chatbot's response"""
        print(f"{self.name}: {text}")
        return text
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"{self.name}: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        """Listen for voice commands"""
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.pause_threshold = 1
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = self.recognizer.listen(source)
        
        try:
            print("Recognizing...")
            command = self.recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            self.speak("Sorry, I didn't understand that.")
            return ""
        except sr.RequestError:
            self.speak("I'm having trouble accessing the speech recognition service.")
            return ""
    
    def get_weather(self, city):
        """Get weather for a specific city"""
        # You need to sign up for an API key at openweathermap.org
        api_key = "YOUR_OPENWEATHERMAP_API_KEY"
        base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        
        try:
            response = requests.get(base_url)
            data = response.json()
            
            if data["cod"] != "404":
                main_data = data["main"]
                weather_data = data["weather"][0]
                
                temperature = main_data["temp"]
                humidity = main_data["humidity"]
                description = weather_data["description"]
                
                weather_info = f"The weather in {city} is {description}. "
                weather_info += f"The temperature is {temperature} degrees Celsius. "
                weather_info += f"The humidity is {humidity} percent."
                
                return weather_info
            else:
                return f"Sorry, I couldn't find weather information for {city}."
        
        except Exception as e:
            return "Sorry, I couldn't get the weather information right now."
    
    def get_time(self):
        """Get current time"""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}."
    
    def get_date(self):
        """Get current date"""
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return f"Today is {current_date}."
    
    def search_wikipedia(self, query):
        """Search information on Wikipedia"""
        try:
            result = wikipedia.summary(query, sentences=2)
            return f"According to Wikipedia: {result}"
        except Exception as e:
            return "Sorry, I couldn't find that information on Wikipedia."
    
    def tell_joke(self):
        """Tell a joke"""
        return pyjokes.get_joke()
    
    def ask_gemini(self, query):
        """Get a response from Gemini AI"""
        if not self.gemini_api_key:
            return "Gemini AI is not configured. Please provide an API key."
        
        try:
            response = self.chat.send_message(query)
            return response.text
        except Exception as e:
            return f"Sorry, there was an error with the Gemini AI service: {str(e)}"
    
    def process_command(self, command, use_voice_response=False):
        """Process text commands"""
        if not command:
            return True
            
        command = command.lower()
        
        # Function to handle the response based on voice or text preference
        def handle_response(response_text):
            if use_voice_response:
                self.speak(response_text)
            else:
                self.respond(response_text)
            return response_text
            
        # Greeting commands
        if any(word in command for word in ["hello", "hi", "hey"]):
            return handle_response(random.choice(self.greetings))
        
        # Voice message command
        elif "voice message" in command or "voice mode" in command:
            handle_response("Voice message mode activated. Please speak your message.")
            voice_message = self.listen()
            if voice_message:
                return self.process_command(voice_message, use_voice_response=True)
            return handle_response("I didn't catch that.")
        
        # Time and date commands
        elif "time" in command:
            return handle_response(self.get_time())
        
        elif "date" in command:
            return handle_response(self.get_date())
        
        # Web search commands
        elif "search" in command and "wikipedia" not in command:
            search_term = command.replace("search", "").strip()
            if not search_term:
                return handle_response("What would you like me to search for?")
            
            url = f"https://www.google.com/search?q={search_term}"
            webbrowser.open(url)
            return handle_response(f"I've opened a search for '{search_term}' in your browser.")
        
        # Wikipedia search
        elif "wikipedia" in command:
            search_term = command.replace("wikipedia", "").strip()
            if not search_term:
                return handle_response("What would you like to know about?")
            
            result = self.search_wikipedia(search_term)
            return handle_response(result)
        
        # Weather command
        elif "weather" in command:
            # Try to extract city name after "weather in" or "weather for"
            if "weather in" in command:
                city = command.split("weather in")[1].strip()
            elif "weather for" in command:
                city = command.split("weather for")[1].strip()
            else:
                return handle_response("Which city would you like to know the weather for?")
            
            if city:
                weather_info = self.get_weather(city)
                return handle_response(weather_info)
        
        # Joke command
        elif "joke" in command:
            joke = self.tell_joke()
            return handle_response(joke)
        
        # Open application commands
        elif "open" in command:
            if "notepad" in command:
                os.system("notepad")
                return handle_response("Opening Notepad")
            elif "calculator" in command:
                os.system("calc")
                return handle_response("Opening Calculator")
            elif "browser" in command or "chrome" in command:
                webbrowser.open("https://www.google.com")
                return handle_response("Opening web browser")
            else:
                return handle_response("I'm not sure which application to open. Please specify the application name.")
        
        # About assistant command
        elif "who are you" in command or "about you" in command:
            about_text = f"I'm {self.name}, your personal chatbot built with Python. "
            about_text += "I can help you with various tasks like telling the time, "
            about_text += "searching the web, checking the weather, and more."
            if self.gemini_api_key:
                about_text += " I'm also powered by Google's Gemini AI for advanced conversations."
            return handle_response(about_text)
        
        # Gemini AI (if configured)
        elif self.gemini_api_key:
            gemini_response = self.ask_gemini(command)
            return handle_response(gemini_response)
        
        # Exit commands
        elif any(word in command for word in ["exit", "stop", "quit", "goodbye", "bye"]):
            return handle_response("Goodbye! Have a nice day!")
        
        # Default response
        else:
            return handle_response("I'm not sure how to help with that yet.")

    def run(self):
        """Main method to run the chatbot"""
        print("\n" + "="*50)
        print(f"  Welcome to {self.name} - Your Python Chatbot")
        print("  Type 'exit' to end the conversation")
        print("  Type 'voice message' to use speech input")
        if self.gemini_api_key:
            print("  Gemini AI integration is active!")
        print("="*50 + "\n")
        
        self.respond(random.choice(self.greetings))
        
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                self.respond("Goodbye! Have a nice day!")
                break
            
            self.process_command(user_input)


if __name__ == "__main__":
    # Create and run chatbot with your Gemini API key
    bot = Chatbot(name="PyChat", gemini_api_key="AIzaSyCvyxvEZcBh2x8VRFUCFDZqeoIMCWjwYzo")
    bot.run()