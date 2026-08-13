# Sentiment Analysis Engine – Production Level Documentation

# 1. Module Overview

The Sentiment Analysis Engine is an AI-powered Natural Language Processing (NLP) module designed to analyze textual feedback submitted by learners across the EduSaaS platform. It classifies text into **Positive**, **Neutral**, or **Negative** sentiment, enabling institutions to monitor learner satisfaction, identify concerns, and improve educational content.

The module is built using **DistilBERT**, a lightweight transformer model fine-tuned for sentiment classification, and integrates seamlessly with the backend through FastAPI.

---

# 2. Objectives

* Analyze learner feedback automatically.
* Classify sentiments into Positive, Neutral, or Negative.
* Detect dissatisfaction early.
* Improve instructor and course quality insights.
* Generate sentiment analytics dashboards.
* Support data-driven educational decisions.

---

# 3. System Architecture

```text
Frontend
      │
      ▼
Backend API
      │
      ▼
Feedback Repository
      │
      ▼
Sentiment Service
      │
      ▼
Data Preprocessing
      │
      ▼
Feature Engineering
      │
      ▼
DistilBERT Model
      │
      ▼
Sentiment Prediction
      │
      ▼
Store Results
      │
      ▼
Analytics Dashboard
```

---

# 4. Data Flow

### Step 1 – Data Collection

Learner feedback is collected from multiple sources:

* Course Reviews
* Discussion Forums
* Assignment Feedback
* Instructor Reviews
* Survey Responses
* Course Ratings

The backend stores all feedback in PostgreSQL.

---

### Step 2 – Data Preprocessing

Raw text is cleaned before model training and inference.

Operations include:

* Lowercase conversion
* URL removal
* HTML tag removal
* Special character removal
* Extra whitespace removal
* Missing value handling
* Duplicate removal

---

### Step 3 – Feature Engineering

The DistilBERT tokenizer converts text into numerical representations.

Generated features include:

* Input IDs
* Attention Mask
* Token IDs
* Maximum Sequence Length
* Tokenized Input

These features are passed to the transformer model.

---

# 5. Model Training

The module uses **DistilBERT**, a transformer-based NLP model pre-trained on large text corpora and fine-tuned on labeled sentiment datasets.

### Model Configuration

* Architecture: DistilBERT
* Task: Multi-class Text Classification
* Classes:

  * Positive
  * Neutral
  * Negative

Training Process:

1. Load Dataset
2. Preprocess Text
3. Tokenize Text
4. Create PyTorch Dataset
5. Fine-tune DistilBERT
6. Evaluate Model
7. Save Model & Tokenizer

---

# 6. Sentiment Prediction

During inference:

1. User submits feedback.
2. Backend forwards text to the AI engine.
3. Text is tokenized.
4. DistilBERT predicts class probabilities.
5. Highest probability determines the final sentiment.
6. Backend stores the prediction.

---

# 7. Model Evaluation

Performance is evaluated using:

* Accuracy
* Precision
* Recall
* F1-Score
* Validation Loss

These metrics are monitored to ensure consistent model quality.

---

# 8. Database Integration

### Input Tables

* students
* course_feedback
* discussion_posts
* assignment_feedback
* instructor_reviews

### Output Tables

* sentiment_predictions
* feedback_analytics
* sentiment_reports

---

# 9. Backend Workflow

```text
Frontend

↓

Backend API

↓

Fetch Feedback

↓

Sentiment Service

↓

Preprocessing

↓

DistilBERT Tokenizer

↓

DistilBERT Model

↓

Sentiment Prediction

↓

Store Prediction

↓

Return Response
```

---

# 10. Production Folder Structure

```text
src/

sentiment/
│
├── __init__.py
├── preprocessing.py
├── sentiment_dataset.py
├── train_model.py
├── evaluate_model.py
├── model_loader.py
├── sentiment_service.py
├── sentiment_repository.py
├── predict_sentiment.py
└── sentiment_schema.py

api/
└── sentiment.py

models/
└── sentiment/

tests/
└── test_sentiment.py
```

---

# 11. Error Handling

The module handles:

* Empty feedback
* Invalid student ID
* Missing text
* Database failures
* Model loading failures
* Prediction failures
* API validation errors

All exceptions are logged through the centralized logging system.

---

# 12. Logging

The module records:

* Feedback received
* Model inference requests
* Prediction results
* Database operations
* API requests
* Processing time
* Errors and exceptions

---

# 13. Testing

Unit tests cover:

* Text preprocessing
* Tokenization
* Dataset creation
* Model prediction
* Repository methods
* Service layer
* API endpoints

Integration tests validate:

* Backend ↔ AI Engine
* AI Engine ↔ PostgreSQL
* Frontend ↔ Backend API

---

# 14. API Endpoints

### Predict Sentiment

```http
POST /sentiment/predict
```

### Request

```json
{
    "student_id": 101,
    "feedback": "The course content was very informative and well structured."
}
```

### Response

```json
{
    "student_id": 101,
    "feedback": "The course content was very informative and well structured.",
    "sentiment": "Positive",
    "confidence": 97.8
}
```

---

# 15. Technology Stack

* **Programming Language:** Python
* **Framework:** FastAPI
* **Deep Learning Framework:** PyTorch
* **Transformer Library:** Hugging Face Transformers
* **Pre-trained Model:** DistilBERT
* **Database:** PostgreSQL
* **Database Layer:** SQLAlchemy / psycopg2
* **Testing:** Pytest
* **Logging:** Python Logging
* **API Validation:** Pydantic
* **Version Control:** Git & GitHub

---

# 16. Future Enhancements

* Emotion detection (Joy, Anger, Sadness, Fear)
* Aspect-based sentiment analysis
* Multilingual sentiment classification
* Real-time sentiment monitoring
* Explainable AI (attention visualization)
* Trend analysis dashboards
* LLM-assisted feedback summarization
* Automated alerts for highly negative feedback

---

# Workflow Summary

```text
Student Feedback
        │
        ▼
Backend API
        │
        ▼
PostgreSQL
        │
        ▼
Preprocessing
        │
        ▼
DistilBERT Tokenizer
        │
        ▼
DistilBERT Model
        │
        ▼
Positive / Neutral / Negative Prediction
        │
        ▼
Store Prediction
        │
        ▼
Analytics Dashboard
```