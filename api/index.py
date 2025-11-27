"""
BhagavadGPT - Vercel Serverless Function
Semantic search engine for Bhagavad Gita verses
"""

import json
import re
import os
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

# Import libraries for embeddings
from sentence_transformers import SentenceTransformer, util
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# ==================== Configuration ====================

STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
    "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
    "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
    "while", "of", "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"
}

MODEL_NAME = 'all-MiniLM-L6-v2'

# ==================== Global Variables ====================

model = None
corpus_embeddings = None
dataset = None

# ==================== Helper Functions ====================

def get_dataset_path():
    """Get the path to the dataset JSON file."""
    # Try multiple possible paths
    paths = [
        Path(__file__).parent.parent / 'bhagavad_gita_dataset_expanded.json',
        Path('/tmp/bhagavad_gita_dataset_expanded.json'),
        Path('bhagavad_gita_dataset_expanded.json'),
    ]
    
    for p in paths:
        if p.exists():
            return str(p)
    
    # If file doesn't exist, raise error
    raise FileNotFoundError(
        "Dataset not found. Please ensure 'bhagavad_gita_dataset_expanded.json' exists."
    )

def load_gita_dataset(file_path: str) -> List[Dict[str, Any]]:
    """Load the Bhagavad Gita dataset from JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            print(f"✓ Loaded dataset with {len(data)} verses")
            return data
    except FileNotFoundError:
        print(f"Error: Dataset file '{file_path}' not found")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{file_path}'")
        return []

def preprocess_and_embed_dataset(dataset: List[Dict[str, Any]]):
    """Generate embeddings for all verses in the dataset."""
    global model, corpus_embeddings
    
    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    
    # Create combined search text for each verse
    for item in dataset:
        themes_str = ", ".join(item.get("themes", []))
        keywords_str = ", ".join(item.get("keywords", []))
        item['combined_search_text'] = (
            f"Theme: {themes_str}. Keywords: {keywords_str}. "
            f"Context: {item.get('context', '')}. "
            f"Translation: {item.get('translation', '')}"
        )
    
    # Generate embeddings for all verses
    corpus_embeddings = model.encode(
        [item['combined_search_text'] for item in dataset],
        convert_to_tensor=True,
        show_progress_bar=False
    )
    
    print("✓ Embeddings generated successfully")
    return model, corpus_embeddings

def extract_keywords(text: str) -> set:
    """Extract meaningful keywords from text."""
    words = re.findall(r"\b\w+\b", text.lower())
    return {word for word in words if word not in STOPWORDS}

def search_verses_hybrid(
    dataset: List[Dict[str, Any]],
    user_query: str,
    model: SentenceTransformer,
    corpus_embeddings
) -> List[Dict[str, Any]]:
    """
    Hybrid search combining semantic similarity and keyword matching.
    """
    user_keywords = extract_keywords(user_query)
    
    # Calculate keyword scores
    keyword_scores = []
    for item in dataset:
        score = 0
        verse_content = " ".join(
            item.get("keywords", []) + 
            item.get("themes", []) + 
            [item.get("translation", "")]
        ).lower()
        for keyword in user_keywords:
            if keyword in verse_content:
                score += 1
        keyword_scores.append(score)
    
    # Normalize keyword scores (0-1)
    max_keyword_score = max(keyword_scores) if max(keyword_scores) > 0 else 1
    keyword_scores = [score / max_keyword_score for score in keyword_scores]
    
    # Calculate semantic scores using embeddings
    query_embedding = model.encode(user_query, convert_to_tensor=True)
    semantic_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
    semantic_scores = semantic_scores.cpu().numpy()
    
    # Combine scores (70% semantic, 30% keyword)
    combined_scores = 0.7 * semantic_scores + 0.3 * np.array(keyword_scores)
    
    # Get top 3 results
    top_indices = np.argsort(combined_scores)[-3:][::-1]
    
    results = []
    for idx in top_indices:
        if combined_scores[idx] > 0.1:  # Minimum threshold
            results.append({
                'verse_data': dataset[idx],
                'score': float(combined_scores[idx])
            })
    
    return results

def format_response(results: List[Dict[str, Any]]) -> str:
    """Format search results into a readable response."""
    if not results:
        return "I couldn't find a matching verse. Please try rephrasing your question."
    
    response_parts = []
    
    for i, result in enumerate(results, 1):
        verse = result['verse_data']
        score = result['score']
        
        chapter = verse.get('chapter', 'N/A')
        verse_num = verse.get('verse', 'N/A')
        translation = verse.get('translation', '')
        themes = ", ".join(verse.get('themes', []))
        context = verse.get('context', '')
        
        part = (
            f"\n{'='*60}\n"
            f"📖 Chapter {chapter}, Verse {verse_num}\n"
            f"{'='*60}\n"
            f"\n{translation}\n"
            f"\n📌 Themes: {themes}"
            f"\n\n💭 Context: {context}"
            f"\n(Confidence: {score*100:.1f}%)"
        )
        response_parts.append(part)
    
    return "\n".join(response_parts)

# ==================== Initialize on Startup ====================

def initialize():
    """Initialize model and embeddings on first request."""
    global model, corpus_embeddings, dataset
    
    if model is None:
        try:
            dataset_path = get_dataset_path()
            dataset = load_gita_dataset(dataset_path)
            
            if dataset:
                preprocess_and_embed_dataset(dataset)
            else:
                print("Warning: Dataset is empty or failed to load")
        except Exception as e:
            print(f"Error during initialization: {e}")

# ==================== API Endpoints ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'BhagavadGPT',
        'version': '1.0.0'
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint for verse retrieval."""
    try:
        # Initialize on first request
        if model is None:
            initialize()
        
        # Get user message
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        if not dataset or model is None:
            return jsonify({
                'error': 'Service not ready. Dataset failed to load.'
            }), 503
        
        # Search for relevant verses
        results = search_verses_hybrid(
            dataset,
            user_message,
            model,
            corpus_embeddings
        )
        
        # Format response
        reply = format_response(results)
        
        # Prepare structured response
        verses_data = [
            {
                'chapter': r['verse_data'].get('chapter'),
                'verse': r['verse_data'].get('verse'),
                'translation': r['verse_data'].get('translation'),
                'themes': r['verse_data'].get('themes', []),
                'context': r['verse_data'].get('context'),
                'score': r['score']
            }
            for r in results
        ]
        
        return jsonify({
            'reply': reply,
            'verses': verses_data,
            'confidence_score': max([r['score'] for r in results]) if results else 0
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/api/verses/count', methods=['GET'])
def verse_count():
    """Get total number of verses in dataset."""
    if dataset is None:
        initialize()
    
    return jsonify({
        'total_verses': len(dataset) if dataset else 0
    })

# ==================== Static File Serving ====================

@app.route('/')
def serve_index():
    """Serve index.html from public directory."""
    public_path = Path(__file__).parent.parent / 'public'
    if (public_path / 'index.html').exists():
        return send_from_directory(public_path, 'index.html')
    else:
        return jsonify({'error': 'Frontend not found'}), 404

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from public directory."""
    public_path = Path(__file__).parent.parent / 'public'
    file_path = public_path / path
    
    if file_path.exists() and file_path.is_file():
        return send_from_directory(public_path, path)
    
    # Try to serve from root
    root_path = Path(__file__).parent.parent / path
    if root_path.exists() and root_path.is_file():
        return send_from_directory(Path(__file__).parent.parent, path)
    
    return jsonify({'error': 'File not found'}), 404

# ==================== Vercel Handler ====================

# For Vercel serverless deployment
handler = app
