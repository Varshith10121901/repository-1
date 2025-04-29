from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from google import genai

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Gemini API Client
client = genai.Client(api_key="AIzaSyCvyxvEZcBh2x8VRFUCFDZqeoIMCWjwYzo")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    response = client.models.generate_content(model="gemini-2.0-flash", contents=user_message)

    bot_reply = response.text if response else "Sorry, I couldn't process that."

    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True)
