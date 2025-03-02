import google.generativeai as genai

# Set up API key
genai.configure(api_key="YOUR_API_KEY") 

# Initialize the model
model = genai.GenerativeModel("gemini-2.0-flash")

# Generate response
response = model.generate_content("Explain how AI works")

# Print output
print(response.text)