import os
from google import genai
from google.genai import types
import PIL.Image

image_path = r'C:\Users\Dell\Pictures\Screenshots\Screenshot 2025-03-10 192751.png'

try:
    image = PIL.Image.open(image_path)
    client = genai.Client(api_key="YOUR_GEMINI_API_KEY") #Replace with your api key
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=["What is this image?", image])
    print(response.text)
except FileNotFoundError:
    print(f"Error: Image not found at {image_path}")
except Exception as e:
    print(f"An error occurred: {e}")

