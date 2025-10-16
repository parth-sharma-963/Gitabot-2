import os
import random
import json
import pickle
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS

import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

# --- NLTK Setup ---
# Download necessary NLTK data. Vercel will cache this for faster builds.
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)

# --- Flask App Initialization ---
app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing

# --- Chatbot Initialization ---
lemmatizer = WordNetLemmatizer()

# Correctly locate data files within the Vercel serverless function environment
base_dir = os.path.dirname(os.path.abspath(__file__))
intents_path = os.path.join(base_dir, 'intents.json')
words_path = os.path.join(base_dir, 'words.pkl')
classes_path = os.path.join(base_dir, 'classes.pkl')
model_path = os.path.join(base_dir, 'chatbot_model.h5')

# Load all necessary files
try:
    intents = json.loads(open(intents_path).read())
    words = pickle.load(open(words_path, 'rb'))
    classes = pickle.load(open(classes_path, 'rb'))
    model = load_model(model_path)
except FileNotFoundError as e:
    # Handle error if a file is missing, which is useful for debugging
    print(f"Error loading files: {e}")
    # You might want to handle this more gracefully in a production app
    intents, words, classes, model = None, None, None, None


# --- Chatbot Processing Functions (from your notebook) ---
def clean_up_sentence(sentence):
    """Tokenizes and lemmatizes the input sentence."""
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence):
    """Converts a sentence into a bag-of-words model."""
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    """Predicts the intent class for a given sentence."""
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

def get_response(intents_list, intents_json):
    """Generates a response based on the predicted intent."""
    if not intents_list:
        return "I'm sorry, I don't understand. Could you please rephrase?"
    
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            return result
            
    return "I'm not sure how to respond to that."

# --- API Endpoints ---
@app.route('/')
def home():
    """A simple endpoint to confirm the API is running."""
    return "GitaBot API is running."

@app.route('/api/chat', methods=['POST'])
def chat():
    """The main chat endpoint that receives user messages and returns the bot's reply."""
    if model is None:
        return jsonify({'error': 'Chatbot model is not loaded'}), 500

    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Get the chatbot's response
    ints = predict_class(user_message)
    bot_reply = get_response(ints, intents)

    # Return the response as JSON
    return jsonify({'reply': bot_reply})