# Toxicity Detection Engine – Production Level Documentation

# 1. Module Overview

The Toxicity Detection Engine is an AI-powered Natural Language Processing (NLP) module designed to identify toxic, abusive, offensive, or harmful text submitted by learners on the EduSaaS platform. The module automatically analyzes discussion posts, comments, and forum messages to maintain a safe and respectful learning environment.

The engine is built using **DistilBERT**, fine-tuned on the **Jigsaw Toxic Comment Classification Dataset**, and integrates with the backend using FastAPI.

---

# 2. Objectives

* Detect toxic content automatically.
* Maintain a safe discussion environment.
* Prevent abusive language in learner interactions.
* Assist moderators by flagging harmful content.
* Improve community engagement and platform quality.
* Store toxicity analytics for reporting and monitoring.

---

# 3. System Architecture

```text
Frontend
      │
      ▼
Backend API
      │
      ▼
Discussion Repository
      │
      ▼
Toxicity Service
      │
      ▼
Text Preprocessing
      │
      ▼
DistilBERT Tokenizer
      │
      ▼
DistilBERT Model
      │
      ▼
Multi-Label Toxicity Prediction
      │
      ▼
Store Prediction
      │
      ▼
Moderation Dashboard
```

---

# 4. Data Flow

## Step 1 – Data Collection

Learner-generated content is collected from:

* Discussion Forums
* Community Posts
* Course Comments
* Assignment Discussions
* Peer Reviews
* Public Chat Messages

The backend stores all discussion data in PostgreSQL.

---

## Step 2 – Data Preprocessing

Before training and inference, text is cleaned using NLP preprocessing techniques.

Operations include:

* Lowercase conversion
* URL removal
* HTML tag removal
* Special character removal
* Extra whitespace removal
* Duplicate removal
* Missing value removal

---

## Step 3 – Feature Engineering

The DistilBERT tokenizer converts cleaned text into transformer-compatible features.

Generated features include:

* Input IDs
* Attention Mask
* Tokenized Sequence
* Maximum Sequence Length

These tensors are provided as input to the DistilBERT model.

---

# 5. Model Training

The Toxicity Detection Engine is built using **DistilBERT**, a transformer-based language model pre-trained on large-scale text corpora and fine-tuned for multi-label toxicity classification.

### Training Workflow

1. Load Jigsaw Toxic Comment Dataset
2. Clean and preprocess comments
3. Tokenize text using DistilBERT Tokenizer
4. Create PyTorch Dataset
5. Fine-tune DistilBERT
6. Evaluate model performance
7. Save trained model and tokenizer

---

# 6. Toxicity Categories

The model predicts one or more of the following labels:

* Toxic
* Severe Toxic
* Obscene
* Threat
* Insult
* Identity Hate

Since this is a **multi-label classification problem**, a single comment may belong to multiple toxicity categories.

Example:

```text
Comment

↓

"You are a stupid idiot."

↓

Predictions

✔ Toxic

✔ Insult
```

---

# 7. Prediction Pipeline

During inference:

1. Learner submits a discussion post.
2. Backend forwards the text to the AI engine.
3. Text is cleaned and tokenized.
4. DistilBERT generates logits.
5. Sigmoid activation converts logits into probabilities.
6. Labels with confidence greater than the configured threshold are selected.
7. Prediction is returned to the backend.
8. Backend stores prediction results in PostgreSQL.

---

# 8. Model Evaluation

Model performance is evaluated using:

* Training Loss
* Validation Loss
* Accuracy
* Precision
* Recall
* F1-Score

These metrics are used to monitor and improve model performance before deployment.

---

# 9. Database Integration

## Input Tables

* students
* discussion_posts
* discussion_comments
* forum_messages

## Output Tables

* toxicity_predictions
* moderation_logs
* flagged_comments

---

# 10. Backend Workflow

```text
Frontend

↓

Backend API

↓

Discussion Repository

↓

Toxicity Service

↓

Text Preprocessing

↓

DistilBERT Tokenizer

↓

DistilBERT Model

↓

Sigmoid Probability Calculation

↓

Toxicity Label Prediction

↓

Store Prediction

↓

Return API Response
```

---

# 11. Production Folder Structure

```text
src/

toxicity/
│
├── __init__.py
├── preprocessing.py
├── toxicity_dataset.py
├── train_model.py
├── evaluate_model.py
├── model_loader.py
├── toxicity_service.py
├── toxicity_repository.py
├── predict_toxicity.py
└── schemas.py

api/
└── toxicity.py

models/
└── toxicity/

tests/
└── test_toxicity.py
```

---

# 12. Error Handling

The module handles:

* Empty discussion posts
* Invalid student IDs
* Missing text input
* Database connection failures
* Model loading failures
* Prediction failures
* API validation errors

All exceptions are recorded through the centralized logging system.

---

# 13. Logging

The module logs:

* Incoming prediction requests
* Student ID
* Discussion ID
* Model inference status
* Prediction results
* Database operations
* Processing time
* Errors and exceptions

---

# 14. Testing

Unit tests cover:

* Text preprocessing
* Dataset creation
* Tokenization
* Model loading
* Prediction service
* Repository methods
* API endpoints

Integration tests validate:

* Backend ↔ AI Engine
* AI Engine ↔ PostgreSQL
* Frontend ↔ Backend API

---

# 15. API Endpoints

## Predict Toxicity

```http
POST /toxicity/predict
```

### Request

```json
{
    "student_id": 101,
    "discussion_id": 5001,
    "post_text": "You are a stupid idiot."
}
```

### Response

```json
{
    "student_id": 101,
    "discussion_id": 5001,
    "post_text": "You are a stupid idiot.",
    "predictions": [
        {
            "label": "TOXIC",
            "confidence": 96.4
        },
        {
            "label": "INSULT",
            "confidence": 94.8
        }
    ]
}
```

---

# 16. Technology Stack

* **Programming Language:** Python
* **Framework:** FastAPI
* **Deep Learning Framework:** PyTorch
* **Transformer Library:** Hugging Face Transformers
* **Pre-trained Model:** DistilBERT
* **Dataset:** Jigsaw Toxic Comment Classification Dataset
* **Database:** PostgreSQL
* **Database Layer:** SQLAlchemy / psycopg2
* **Testing:** Pytest
* **Logging:** Python Logging
* **API Validation:** Pydantic
* **Version Control:** Git & GitHub

---

# 17. Future Enhancements

* Real-time discussion moderation
* Automatic comment blocking based on toxicity threshold
* Severity-based moderation workflow
* Multilingual toxicity detection
* Explainable AI for toxicity predictions
* Custom moderation rules for institutions
* Integration with educator moderation dashboard
* Continuous model retraining using platform data

---

# Workflow Summary

```text
Student Discussion Post
        │
        ▼
Backend API
        │
        ▼
PostgreSQL
        │
        ▼
Text Preprocessing
        │
        ▼
DistilBERT Tokenizer
        │
        ▼
DistilBERT Model
        │
        ▼
Sigmoid Activation
        │
        ▼
Multi-Label Toxicity Prediction
        │
        ▼
Store Prediction
        │
        ▼
Moderation Dashboard
```

