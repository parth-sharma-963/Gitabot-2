# BhagavadGPT – Semantic Search Chatbot for Bhagavad Gita Wisdom

> An AI-powered retrieval system that matches your life questions with relevant verses from the Bhagavad Gita using advanced NLP and semantic embeddings.

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Architecture & ML Stack](#architecture--ml-stack)
4. [How It Works](#how-it-works)
5. [Installation](#installation)
6. [Usage](#usage)
7. [API Documentation](#api-documentation)
8. [Deployment](#deployment)
9. [Project Structure](#project-structure)
10. [Future Enhancements](#future-enhancements)
11. [Contributing](#contributing)

---

## 🎯 Project Overview

BhagavadGPT is a **Semantic Search + Retrieval-Augmented (RAG-like) system** that retrieves relevant verses from the Bhagavad Gita based on user queries. Unlike traditional chatbots that generate responses, it intelligently searches through a curated knowledge base of 100+ philosophical verses and returns the most contextually relevant shlokas with explanations.

**What This Is:**
- ✅ Semantic search engine for philosophical guidance
- ✅ NLP-powered retrieval system
- ✅ Interactive web-based chatbot interface
- ✅ Lightweight, privacy-focused (runs locally)

**What This Is NOT:**
- ❌ A large language model (LLM)
- ❌ A generative AI system
- ❌ An intelligent agent
- ❌ Cloud-dependent

---

## ✨ Features

### Core Capabilities
- **Semantic Understanding**: Uses transformer-based embeddings to understand contextual meaning, not just keywords
- **Hybrid Retrieval**: Combines keyword matching + semantic similarity for accuracy
- **Theme-Based Matching**: Verses tagged with themes (karma yoga, devotion, detachment, etc.) for precise retrieval
- **Rich Metadata**: Each verse includes Sanskrit original, translation, context, and related teachings
- **Interactive Chat Interface**: User-friendly web interface for natural conversation
- **Fast Response**: Sub-second retrieval due to pre-computed embeddings
- **Transparent Results**: Clear visibility into why verses are recommended

### Technical Highlights
- 100+ curated Bhagavad Gita verses with rich metadata
- Pre-embedded with `sentence-transformers` for instant retrieval
- Hybrid scoring: 70% semantic + 30% keyword-based
- Lightweight model (22M parameters) runs on CPU
- Flask backend with REST API
- Vanilla JavaScript frontend (no heavy dependencies)

---

## 🏗️ Architecture & ML Stack

### System Architecture
```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
    ┌────▼──────────────────────┐
    │  Preprocessing & Keywords  │
    │  - Tokenization            │
    │  - Stopword removal        │
    │  - Keyword extraction      │
    └────┬──────────────────────┘
         │
    ┌────▼──────────────────────────┐
    │  Semantic Embedding            │
    │  (SentenceTransformer)         │
    │  - all-MiniLM-L6-v2 model     │
    │  - 384-dim vectors            │
    └────┬──────────────────────────┘
         │
    ┌────▼──────────────────────────┐
    │  Similarity Calculation        │
    │  - Cosine similarity (semantic)│
    │  - Keyword matching score     │
    └────┬──────────────────────────┘
         │
    ┌────▼──────────────────────────┐
    │  Score Fusion & Ranking        │
    │  Final = 0.7×Semantic +       │
    │          0.3×Keyword          │
    └────┬──────────────────────────┘
         │
    ┌────▼──────────────────────────┐
    │  Top-K Retrieval (Top 3)       │
    │  Return best matching verses   │
    └────┬──────────────────────────┘
         │
    ┌────▼──────────────┐
    │  Format Response   │
    │  Return to user    │
    └────────────────────┘
```

### ML Technologies Used
| Technology | Purpose | Details |
|-----------|---------|---------|
| **Sentence-Transformers** | Text Embeddings | `all-MiniLM-L6-v2` (22M params) generates 384-dimensional dense vectors |
| **Cosine Similarity** | Semantic Matching | Measures angle between embedding vectors (0-1 score) |
| **Keyword Extraction** | Lexical Matching | Regex + stopword filtering for exact phrase matching |
| **Hybrid Scoring** | Relevance Ranking | Combines semantic + keyword scores with weighted fusion |
| **Flask** | Backend API | RESTful web service for chat endpoint |
| **SciPy/NumPy** | Vector Operations | Efficient similarity computation across corpus |

### Classification
- **Retrieval Type**: Dense vector search (semantic) + sparse keyword search (lexical)
- **System Type**: Hybrid RAG (Retrieval-Augmented Generation) without generation component
- **ML Paradigm**: Unsupervised similarity matching (no training required)
- **Model**: Frozen pre-trained transformer (no fine-tuning)

---

## 🔧 How It Works

### Step 1: Data Preparation
Each Bhagavad Gita verse is structured with:
```json
{
  "chapter": 2,
  "verse": 47,
  "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
  "translation": "You have a right to perform your prescribed duties...",
  "themes": ["karma yoga", "detachment", "duty"],
  "keywords": ["action", "duty", "detachment", "karma"],
  "context": "Krishna explains the philosophy of selfless action",
  "attributes": {
    "mood": "instructive",
    "teaching_type": "philosophical principle",
    "philosophical_concept": "nishkama karma"
  }
}
```

### Step 2: Embedding Generation
During initialization:
```python
# Load pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create combined search text for each verse
combined_text = f"Theme: {themes}. Keywords: {keywords}. Translation: {translation}"

# Generate 384-dimensional embedding
embedding = model.encode(combined_text)
```

**Why this model?**
- **all-MiniLM-L6-v2** is optimized for semantic similarity tasks
- 22M parameters = runs on CPU
- Trained on millions of sentence pairs for similarity understanding
- Excellent semantic understanding for philosophical texts

### Step 3: Query Processing
When user asks "I feel anxious":

```python
# 1. Extract keywords
keywords = {"feel", "anxious"}

# 2. Create query embedding
query_embedding = model.encode("I feel anxious")

# 3. Calculate similarity scores
semantic_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)

# 4. Calculate keyword scores
keyword_scores = [count_matching_keywords(verse) for verse in dataset]

# 5. Combine scores
final_scores = 0.7 * semantic_scores + 0.3 * keyword_scores

# 6. Get top results
top_verses = dataset[np.argsort(final_scores)[-3:]]
```

### Step 4: Response Formatting
Return matching verse with:
- Sanskrit original (शलोक)
- English translation
- Themes and keywords
- Context explanation
- Chapter and verse reference

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/parth-sharma-963/Gitabot-2.git
cd Gitabot-2
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Generate the dataset (if not present)**
```bash
jupyter notebook code.ipynb
# Run the first two cells to generate bhagavad_gita_dataset_expanded.json
```

5. **Run the Flask server**
```bash
python app.py
```

6. **Access the chatbot**
Open browser and go to: `http://localhost:5000`

---

## 🚀 Usage

### Web Interface
1. Type your question or life situation in the chat input
2. Press Enter or click Send button
3. Receive relevant Bhagavad Gita verses with explanations

### Example Queries
```
"I feel lost and anxious."
→ Returns verses about eternal nature and courage

"How do I balance work and personal life?"
→ Returns verses about karma yoga and duty

"I'm struggling with anger."
→ Returns verses about desire-anger cycle and self-control

"What should I do when facing uncertainty?"
→ Returns verses about faith and detachment

"How can I find peace?"
→ Returns verses about meditation and inner satisfaction
```

### Customization
Edit the retrieval weights in `code.ipynb`:
```python
# Current weights (changeable)
final_score = 0.7 * semantic_similarity + 0.3 * keyword_match

# Increase keyword weight for more literal matching
final_score = 0.5 * semantic_similarity + 0.5 * keyword_match

# Increase semantic weight for more conceptual matching
final_score = 0.9 * semantic_similarity + 0.1 * keyword_match
```

---

## 📡 API Documentation

### Endpoint: POST `/api/chat`

**Request:**
```json
{
  "message": "I feel anxious"
}
```

**Response:**
```json
{
  "reply": "Chapter 2, Verse 2: The soul is eternal and indestructible...",
  "verses": [
    {
      "chapter": 2,
      "verse": 2,
      "translation": "...",
      "themes": ["courage", "eternal nature"],
      "context": "..."
    }
  ],
  "confidence_score": 0.89
}
```

---

## 🌐 Deployment

### Option 1: Vercel (Recommended for Serverless)

Vercel provides serverless deployment with native Python support and zero cold-start times.

**Setup Steps:**

1. **Ensure you have the correct project structure:**
```
Gitabot-2/
├── api/
│   └── index.py          # Serverless function
├── public/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── vercel.json
└── requirements.txt
```

2. **Install Vercel CLI:**
```bash
npm install -g vercel
```

3. **Deploy:**
```bash
vercel
# Follow the prompts to connect GitHub and deploy
```

4. **Access your app:**
```
https://your-project.vercel.app
```

**Environment Variables (if needed):**
Add in Vercel dashboard under Settings → Environment Variables

### Option 2: Heroku (Traditional)
```bash
heroku login
heroku create your-app-name
git push heroku main
heroku logs --tail
```

### Option 3: Railway
Connect GitHub repository directly for auto-deployment.

### Option 4: PythonAnywhere
Simple platform for Python web apps with free tier.

---

## 📁 Project Structure

```
Gitabot-2/
├── README.md                                  # This file
├── requirements.txt                           # Python dependencies
├── vercel.json                                # Vercel configuration
├── app.py                                     # Flask development server
├── code.ipynb                                 # Data generation & training
├── bhagavad_gita_dataset_expanded.json       # Verse database (100+ verses)
│
├── api/
│   └── index.py                              # Vercel serverless function
│
├── public/
│   ├── index.html                            # Web interface
│   ├── style.css                             # Styling
│   └── script.js                             # Frontend logic
│
└── static/                                    # Alternative static files
    ├── script.js
    └── style.css
```

---

## 🔮 Future Enhancements

### Phase 2: Multi-Modal Search
- [ ] Search by emotional state (anger, sadness, confusion)
- [ ] Search by philosophical concept (karma, dharma, bhakti)
- [ ] Multi-language support (Hindi, Sanskrit, Tamil)

### Phase 3: Generative Enhancement
- [ ] Integrate GPT/Claude for personalized explanations
- [ ] Generate guided meditation based on verses
- [ ] Create daily wisdom notifications

### Phase 4: Advanced Features
- [ ] User preferences and conversation memory
- [ ] Verse bookmarking and notes
- [ ] Related verses suggestion network
- [ ] Mood tracking over time

### Phase 5: Quality Improvements
- [ ] Fine-tune embeddings on philosophical text corpus
- [ ] Add RoBERTa-based emotion detection
- [ ] Expand dataset to 500+ verses
- [ ] Add audio narration in Sanskrit/English

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Contribution
- ✅ Adding more verses to the dataset
- ✅ Improving semantic embeddings
- ✅ UI/UX enhancements
- ✅ Bug fixes and optimizations
- ✅ Documentation improvements
- ✅ Translation support

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- **Bhagavad Gita**: Ancient philosophical text
- **Hugging Face**: Sentence-Transformers library
- **Flask**: Web framework
- **Community**: Contributors and users

---

## 📧 Support & Contact

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing discussions

---

## 🔗 Links

- [GitHub Repository](https://github.com/parth-sharma-963/Gitabot-2)
- [Sentence-Transformers Docs](https://www.sbert.net/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Vercel Python Support](https://vercel.com/docs/functions/python)

---

**Last Updated**: November 27, 2025  
**Status**: Active Development  
**Version**: 1.0.0
