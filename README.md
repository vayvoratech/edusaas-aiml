# EduSaaS – AI-Powered Adaptive Skill Assessment Platform

## Overview

EduSaaS is an AI-powered adaptive skill assessment platform developed by **Vayvora Technologies Pvt. Ltd.** It evaluates a student's technical skills based on their selected job role using an adaptive assessment algorithm.

The platform combines **Node.js**, **Python (Flask)**, and **PostgreSQL** to deliver scalable, intelligent assessments. Node.js manages the business logic and database operations, while Python serves as a stateless AI engine responsible for adaptive question selection and difficulty adjustment.

---

# Features

- User Registration
- Job Role Selection
- AI-Powered Adaptive Quiz
- Dynamic Difficulty Adjustment
- Skill-wise Assessment
- Skill Gap Analysis
- Personalized Learning Recommendations
- RESTful APIs
- PostgreSQL Database
- Modular Microservice Architecture

---

# Technology Stack

## Backend

- Node.js
- Express.js
- Python 3.x
- Flask

## Database

- PostgreSQL

## AI Engine

- Adaptive Difficulty Algorithm
- Skill Score Calculation
- Dynamic Question Selection

## Version Control

- Git
- GitHub

---

# System Architecture

```
                Frontend
                    │
                    ▼
          Node.js (Express API)
                    │
        ┌───────────┴────────────┐
        │                        │
        ▼                        ▼
 PostgreSQL Database      Python Flask API
                                │
                                ▼
                      Adaptive Quiz Engine
```

Node.js is responsible for:

- Business Logic
- Database Operations
- Quiz Session Management
- API Endpoints

Python is responsible for:

- Adaptive Question Selection
- Difficulty Adjustment
- Skill Score Calculation
- Adaptive Quiz Engine

---

# Project Structure

```
Adaptive_Quiz/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── routes/
│   └── quiz.py
│
├── services/
│   └── adaptive_engine.py
│
├── backend/
│   ├── server.js
│   ├── package.json
│   ├── config/
│   │   └── db.js
│   ├── controllers/
│   │   └── quizController.js
│   ├── routes/
│   │   └── quiz.js
│   ├── services/
│   │   └── pythonService.js
│   └── .env
│
├── uploads/
└── question_bank/
```

---

# Complete Call Chain

```text
Student
   │
   ▼
server.js
   │
   ▼
routes/quiz.js
   │
   ▼
quizController.js
   │
   ├──────────────► db.js
   │                   │
   │                   ▼
   │              PostgreSQL
   │
   └──────────────► pythonService.js
                        │
                        ▼
                  HTTP Request
                        │
                        ▼
                    app.py
                        │
                        ▼
                 routes/quiz.py
                        │
                        ▼
              adaptive_engine.py
                        │
                        ▼
                 Adaptive Logic
                        │
                        ▼
                 routes/quiz.py
                        │
                        ▼
                pythonService.js
                        │
                        ▼
                quizController.js
                        │
                        ▼
                  PostgreSQL
                        │
                        ▼
                    Frontend
---

# Database Modules

- Users
- Domain Roles
- Skills
- Domain Required Skills
- Difficulty Levels
- Questions
- Quiz Sessions
- Quiz State
- Student Skill Results

---

# Adaptive Quiz Workflow

```
Student
    │
    ▼
Select Job Role
    │
    ▼
Create Quiz Session
    │
    ▼
Load Required Skills
    │
    ▼
Python Creates Adaptive State
    │
    ▼
Question Starts at Easy Level
    │
    ▼
Student Answers Question
    │
    ▼
Difficulty Updated
    │
    ▼
Next Question Selected
    │
    ▼
Skill Completed
    │
    ▼
Skill Score Calculated
    │
    ▼
Next Skill
    │
    ▼
Assessment Completed
```

---

# Difficulty Adaptation Logic

- Assessment starts at **Easy** difficulty.
- Two consecutive correct answers increase the difficulty.
- Two consecutive incorrect answers decrease the difficulty.
- Maximum of **10 questions per skill**.
- Marks are awarded based on question difficulty.

| Difficulty | Marks |
|------------|------:|
| Easy | 1 |
| Medium | 2 |
| Hard | 3 |

---

# Skill Level Calculation

| Percentage | Skill Level |
|------------|------------:|
| 90–100 | 5 |
| 70–89 | 4 |
| 50–69 | 3 |
| 25–49 | 2 |
| 0–24 | 1 |

---

# Installation

## Clone Repository

```bash
git clone --branch KiranAiml --single-branch https://github.com/vayvoratech/edusaas-aiml.git
```

```
cd edusaas-aiml
```

---

# Python Setup

Create Virtual Environment

```bash
python -m venv venv
```

Activate

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

# Node.js Setup

Move into backend

```bash
cd backend
```

Install dependencies

```bash
npm install
```

---

# Configure Environment

Create a `.env` file inside the `backend` directory.

Example:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=postgres
DB_PASSWORD=your_password

PYTHON_API=http://127.0.0.1:5000/api/quiz
PORT=3000
```

---

# Run the Project

### Start Python AI Engine

```bash
python app.py
```

Runs on:

```
http://127.0.0.1:5000
```

---

### Start Node.js Backend

```bash
cd backend
npm start
```

Runs on:

```
http://localhost:3000
```

---

# API Endpoints

## Start Assessment

```
POST /api/quiz/start
```

---

## Submit Answer

```
POST /api/quiz/submit-answer
```

---

## Finish Assessment

```
POST /api/quiz/finish
```

---

# Future Enhancements

- JWT Authentication
- Student Dashboard
- Admin Dashboard
- AI Course Recommendation
- Skill Gap Analytics
- Performance Prediction
- Assignment Evaluation
- Certificate Generation
- Learning Path Recommendation

---

# Developed By

**Vayvora Technologies Pvt. Ltd.**

AI • Enterprise SaaS • EdTech
