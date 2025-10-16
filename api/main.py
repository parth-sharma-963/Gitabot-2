from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)
# Enable CORS to allow your frontend to communicate with this API
CORS(app)

# Define the API endpoint for the chatbot
@app.route('/api/chat', methods=['POST'])
def chat():
    # Get the message from the POST request
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # --- Your GitaBot Logic Goes Here ---
    # For now, we'll just echo the message back.
    # Replace this line with your actual bot's logic to generate a response.
    bot_reply = f"You said: {user_message}"
    # ------------------------------------

    # Return the bot's reply as JSON
    return jsonify({'reply': bot_reply})

# This is a good practice for Vercel deployment
@app.route('/')
def home():
    return "API is running."