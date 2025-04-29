from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    
    # Simple response logic (replace with AI logic)
    bot_response = f"You said: {user_input}"

    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
