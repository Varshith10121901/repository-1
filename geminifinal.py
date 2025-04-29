from flask import Flask, request, jsonify, render_template
import google.generativeai as ai
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS if you're serving frontend separately

# Gemini API configuration
API_KEY = 'AIzaSyCvyxvEZcBh2x8VRFUCFDZqeoIMCWjwYzo'  # Replace with your real key
ai.configure(api_key=API_KEY)
model = ai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send():
    try:
        user_msg = request.json.get("message", "")
        if not user_msg:
            return jsonify({"error": "Empty message"}), 400

        history.append(f"User: {user_msg}")
        if user_msg.lower() in ["bye", "exit", "quit"]:
            response_text = "Goodbye! Feel free to come back anytime."
        else:
            response = chat.send_message('\n'.join(history))
            response_text = response.text
            history.append(f"Chatbot: {response_text}")

        return jsonify({"response": response_text})
    except Exception as e:
        logger.exception("Error generating response")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
