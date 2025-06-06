import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes

# Initialize recognizer and text-to-speech engine
listener = sr.Recognizer()
engine = pyttsx3.init()

# Set voice property
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def talk(text):
    """Function to make the assistant speak"""
    engine.say(text)
    engine.runAndWait()

def take_command():
    """Function to take voice command from the user"""
    try:
        with sr.Microphone() as source:
            print("Listening...")
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'alexa' in command:
                command = command.replace('alexa', '')
            print(command)
    except:
        pass
    return command

def run_alexa():
    """Function to execute commands based on user input"""
    command = take_command()
    print(command)

    if 'play' in command:
        song = command.replace('play', '')
        talk("Playing " + song)
        pywhatkit.playonyt(song)

    elif 'time' in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        talk("Current time is " + time)

    elif 'who the heck is' in command:
        person = command.replace('who the heck is', '')
        info = wikipedia.summary(person, 1)
        print(info)
        talk(info)

    elif 'date' in command:
        talk("Sorry, I have a headache")

    elif 'are you single' in command:
        talk("I am in a relationship with WiFi")

    elif 'joke' in command:
        talk(pyjokes.get_joke())

    else:
        talk("Please say the command again.")

while True:
    run_alexa()