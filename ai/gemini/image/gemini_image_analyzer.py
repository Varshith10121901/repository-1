import google.generativeai as genai
from google.generativeai import types
from PIL import Image
from io import BytesIO

genai.configure(api_key="AIzaSyCvyxvEZcBh2x8VRFUCFDZqeoIMCWjwYzo")  # Replace with your actual API key
client = genai.Client()  # Move this line up!

contents = ('Hi, can you create a 3d rendered image of a pig '
            'with wings and a top hat flying over a happy '
            'futuristic scifi city with lots of greenery?')

response = client.models.generate_content(
    model="models/gemini-2.0-flash-exp",
    contents=contents,
    config=types.GenerateContentConfig(response_modalities=['Text', 'Image'])
)

for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        try:
            image = Image.open(BytesIO(part.inline_data.data))
            image.show()
        except Exception as e:
            print(f"Error displaying image: {e}") 