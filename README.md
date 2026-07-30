# EduSaaS AI Platform

## Overview

EduSaaS AI Platform is an AI-powered education platform that provides intelligent learning recommendations, dropout prediction, sentiment analysis, and adaptive quizzes.

The project is built using Python, FastAPI, PostgreSQL, Scikit-learn, Hugging Face Transformers, and Machine Learning.

---

# Features

- Course Recommendation System
- Student Dropout Prediction
- Discussion Sentiment Analysis
- Adaptive Quiz System
- PostgreSQL Database
- FastAPI REST APIs
- Swagger Documentation
- Batch Prediction
- Logging
- Unit Testing

---

# Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Scikit-learn
- Hugging Face Transformers
- PyTorch
- Pandas
- NumPy
- Pytest

---

# Project Structure

```text
src/
│
├── api/
├── adaptive_quiz/
├── database/
├── dropout/
├── recommendation/
├── sentiment/
├── logs/
└── models/

tests/
docs/
data/
```

---

# Setup

Clone the repository

```bash
git clone <repository-url>
```

Create virtual environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file

```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=eduai_db

MODEL_VERSION=1.0.0
```

---

# Run API

```bash
uvicorn src.api.main:app --reload
```

Swagger

```
http://127.0.0.1:8000/docs
```

---

# AI Models

## Recommendation System

Hybrid recommendation using:

- Content-Based Filtering
- Collaborative Filtering (SVD)

---

## Dropout Prediction

Random Forest classifier using student engagement features.

---

## Sentiment Analysis

Fine-tuned DistilBERT model for:

- Positive
- Neutral
- Negative

---

## Adaptive Quiz

Adaptive difficulty quiz based on student performance.

---

# Testing

Run all tests

```bash
pytest -v
```

---



# Author

Rohit