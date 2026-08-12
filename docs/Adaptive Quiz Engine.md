# Adaptive Quiz Engine - Production Level Documentation

# 1. Module Overview

The Adaptive Quiz Engine is an AI-powered assessment module designed to personalize quiz difficulty based on each learner's knowledge, engagement, and historical performance. Instead of presenting identical assessments to every learner, the engine dynamically selects an appropriate difficulty level to maximize learning outcomes and accurately measure skill progression.

The module integrates with the EduSaaS platform through the backend API and continuously updates learner readiness after every assessment.

---

# 2. Objectives

* Personalize quizzes for every learner.
* Prevent learners from receiving questions that are too easy or too difficult.
* Improve knowledge retention through adaptive assessments.
* Measure learner readiness for certification.
* Continuously update learner skill profiles.
* Provide reliable performance analytics for educators.

---

# 3. System Architecture

```text
Frontend
      │
      ▼
Backend API
      │
      ▼
Learner Performance Repository
      │
      ▼
Adaptive Quiz Service
      │
      ▼
Feature Engineering
      │
      ▼
Difficulty Prediction Engine
      │
      ▼
Question Selection Engine
      │
      ▼
Quiz Generation
      │
      ▼
Student Attempts Quiz
      │
      ▼
Automatic Evaluation
      │
      ▼
Readiness Score Update
      │
      ▼
Database Storage
```

---

# 4. Data Flow

### Step 1 – Data Collection

The backend retrieves learner information from PostgreSQL.

Example data includes:

* Quiz Scores
* Assignment Scores
* Lesson Completion
* Learning Progress
* Course Completion
* Time Spent Learning
* Previous Difficulty Level
* Previous Quiz Attempts
* Readiness Score

---

### Step 2 – Data Preprocessing

The service validates and prepares learner information.

Operations include:

* Missing value handling
* Invalid record removal
* Data normalization
* Type conversion
* Duplicate removal

---

### Step 3 – Feature Engineering

Raw learner activity is transformed into meaningful AI features.

Generated features include:

* Average Quiz Score
* Assignment Accuracy
* Course Completion %
* Learning Progress
* Average Response Time
* Practice Frequency
* Consecutive Correct Answers
* Previous Difficulty Level
* Readiness Score
* Engagement Score

---

# 5. Difficulty Prediction Engine

The engine determines the learner's current competency level.

Example classification:

| Score    | Difficulty   |
| -------- | ------------ |
| 0 – 40   | Beginner     |
| 41 – 70  | Intermediate |
| 71 – 100 | Advanced     |

The predicted difficulty determines which question bank will be used.

---

# 6. Question Selection Engine

Questions are selected from the appropriate repository based on:

* Difficulty Level
* Subject
* Topic
* Learning Path
* Previous Questions
* Question Availability

Duplicate questions are automatically avoided.

---

# 7. Quiz Generation

The engine dynamically creates a personalized assessment.

Example:

```text
Student

↓

Intermediate Level

↓

SQL Topic

↓

10 Questions

↓

Medium Difficulty

↓

Return Quiz
```

---

# 8. Quiz Evaluation

After submission, the engine evaluates:

* Correct Answers
* Wrong Answers
* Accuracy
* Completion Time
* Score Percentage
* Topic-wise Performance

---

# 9. Readiness Score Calculation

Learner readiness is recalculated using:

* Current Quiz Performance
* Historical Performance
* Learning Progress
* Assignment Performance
* Course Completion

The updated readiness score is stored for future recommendations.

---

# 10. Database Integration

## Input Tables

* students
* courses
* enrollments
* learning_progress
* quiz_results
* assignments
* user_activity

---

## Output Tables

* adaptive_quiz_attempts
* adaptive_quiz_results
* readiness_scores
* learner_progress
* ai_recommendations

---

# 11. Backend Workflow

```text
Frontend

↓

Backend API

↓

Fetch Learner Data

↓

Adaptive Quiz Service

↓

Feature Engineering

↓

Difficulty Prediction

↓

Question Repository

↓

Generate Quiz

↓

Return Quiz to Frontend

↓

Student Attempts Quiz

↓

Evaluate Answers

↓

Update Readiness Score

↓

Store Results
```

---

# 12. Production Folder Structure

```text
src/

adaptive_quiz/
│
├── __init__.py
├── adaptive_quiz_service.py
├── adaptive_quiz_repository.py
├── feature_engineering.py
├── difficulty_engine.py
├── question_selector.py
├── readiness_score.py
├── quiz_evaluator.py
├── predict_quiz.py
└── schemas.py

api/
└── adaptive_quiz.py

models/
└── adaptive_quiz/

tests/
└── test_adaptive_quiz.py
```

---

# 13. Error Handling

The module handles:

* Invalid learner ID
* Missing learner data
* Empty question bank
* Database failures
* API validation errors
* Unexpected exceptions

All errors are logged through the centralized logging system.

---

# 14. Logging

The module records:

* Quiz generation requests
* Difficulty prediction
* Quiz submission
* Readiness score updates
* Database operations
* Errors and exceptions
* Response time

---

# 15. Testing

Unit tests validate:

* Difficulty prediction
* Feature engineering
* Question selection
* Readiness calculation
* Repository methods
* API endpoints
* Exception handling

Integration tests verify:

* Backend ↔ Database
* Backend ↔ AI Service
* Frontend ↔ Backend API

---

# 16. API Endpoints

### Generate Adaptive Quiz

```http
POST /adaptive-quiz/generate
```

**Input**

```json
{
  "student_id": 101,
  "course_id": 5
}
```

**Response**

```json
{
  "difficulty": "Intermediate",
  "questions": [
    ...
  ]
}
```

---

### Submit Quiz

```http
POST /adaptive-quiz/submit
```

**Input**

```json
{
  "student_id": 101,
  "quiz_id": 5001,
  "answers": [...]
}
```

**Response**

```json
{
  "score": 82,
  "readiness_score": 78,
  "next_difficulty": "Advanced"
}
```

---

# 17. Future Enhancements

* AI-generated question creation using LLMs.
* Reinforcement learning to adapt difficulty dynamically.
* Personalized hints for incorrect answers.
* Topic-level weakness analysis.
* Difficulty calibration using Item Response Theory (IRT).
* Multilingual quiz generation.
* Real-time analytics dashboard.
* Educator approval workflow for generated assessments.

---

## Technology Stack

* **Language:** Python
* **Framework:** FastAPI
* **Database:** PostgreSQL
* **ORM/Database Layer:** SQLAlchemy
* **Testing:** Pytest
* **Logging:** Centralized Python Logging
* **API Validation:** Pydantic
* **Version Control:** Git/GitHub


