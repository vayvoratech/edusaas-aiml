# EduSaaS – AI-Powered Adaptive Skill Assessment Platform

## Overview

EduSaaS is an AI-powered adaptive skill assessment platform developed by **Vayvora Technologies Pvt. Ltd.** It evaluates a student's technical skills based on their selected job role using an adaptive assessment algorithm.

The platform combines **Node.js**, **Python (Flask)**, and **PostgreSQL** to deliver scalable, intelligent assessments. Node.js manages the business logic, API orchestration, and database operations, while Python acts as a stateless AI engine responsible for adaptive question selection, difficulty adjustment, score calculation, and skill gap analysis.

---

# Features

- User Registration
- Job Role Selection
- AI-Powered Adaptive Quiz
- Dynamic Difficulty Adjustment
- Skill-wise Assessment
- Skill Gap Analysis
- Readiness Score Calculation
- Missing Skills Identification
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
- Dynamic Question Selection
- Skill Score Calculation
- Skill Gap Analysis
- Readiness Score Calculation

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
     PostgreSQL Database      Python Flask APIs
                                      │
                     ┌────────────────┴──────────────┐
                     ▼                               ▼
            Adaptive Quiz Engine          Skill Gap Engine
```

### Node.js Responsibilities

- Business Logic
- API Orchestration
- Database Operations
- Quiz Session Management
- Quiz State Management
- Skill Result Storage

### Python Responsibilities

- Adaptive Question Selection
- Difficulty Adjustment
- Skill Score Calculation
- Skill Gap Analysis
- Readiness Score Calculation

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
│   ├── quiz.py
│   └── skill_gap.py
│
├── services/
│   ├── adaptive_engine.py
│   └── skill_gap_engine.py
│
├── backend/
│   ├── app.js
│   ├── server.js
│   ├── package.json
│   ├── package-lock.json
│   ├── .env
│   │
│   ├── config/
│   │   └── db.js
│   │
│   ├── controllers/
│   │   ├── quizController.js
│   │   └── skillGapController.js
│   │
│   ├── routes/
│   │   ├── quiz.js
│   │   └── skillGap.js
│   │
│   └── services/
│       ├── pythonService.js
│       └── skillGapPythonService.js
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
- Roles
- Domain Roles
- Skills
- Domain Required Skills
- Difficulty Levels
- Questions
- Quiz Sessions
- Quiz State
- Student Answers
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
Python Creates Quiz State
    │
    ▼
Questions Start at Easy Difficulty
    │
    ▼
Student Submits Answer
    │
    ▼
Adaptive Engine Evaluates Answer
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
Store Student Skill Result
    │
    ▼
Next Skill
    │
    ▼
Assessment Completed
```

---

# Skill Gap Analysis Workflow

```
Assessment Completed
            │
            ▼
Load Student Skill Results
            │
            ▼
Load Required Skills
            │
            ▼
Python Skill Gap Engine
            │
            ▼
Compare Required vs Student Skill Levels
            │
            ▼
Calculate Skill Gap
            │
            ▼
Calculate Readiness Score
            │
            ▼
Identify Missing Skills
            │
            ▼
Generate Skill Gap Report
```

---

# Difficulty Adaptation Logic

- Assessment always starts at **Easy** difficulty.
- Two consecutive correct answers increase the difficulty.
- Two consecutive incorrect answers decrease the difficulty.
- Maximum of **10 questions per skill**.
- Marks are awarded according to question difficulty.

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

# Readiness Score

The readiness score measures how closely a student's current skills match the required skills for the selected job role.

```
Readiness Score =
(Total Student Skill Levels ÷ Total Required Skill Levels) × 100
```

### Example

```
Student Levels

Python             3
SQL                2
Machine Learning   3
Deep Learning      2
Git                3

Total Student Levels = 13

Required Levels

Python             5
SQL                3
Machine Learning   5
Deep Learning      5
Git                3

Total Required Levels = 21

Readiness Score

(13 ÷ 21) × 100

= 61.9%
```

---

# Installation

## Clone Repository

```bash
git clone --branch KiranAiml --single-branch https://github.com/vayvoratech/edusaas-aiml.git
```

Move into the project

```bash
cd edusaas-aiml
```

---

# Python Setup

Create Virtual Environment

```bash
python -m venv venv
```

Activate Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install Dependencies

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

```env
PORT=3000

DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=postgres
DB_PASSWORD=your_password

PYTHON_SERVICE=http://127.0.0.1:5000/api/quiz
SKILL_GAP_SERVICE=http://127.0.0.1:5000/api/skill-gap
```

---

# Run the Project

## Start Flask AI Engine

```bash
python app.py
```

Runs on

```
http://127.0.0.1:5000
```

---

## Start Node.js Backend

```bash
cd backend

npm start
```

Runs on

```
http://localhost:3000
```

---

# API Endpoints

## Adaptive Quiz

### Start Assessment

```
POST /api/quiz/start
```

### Submit Answer

```
POST /api/quiz/submit-answer
```

### Finish Assessment

```
POST /api/quiz/finish
```

---

## Skill Gap Analysis

### Analyze Skill Gap

```
POST /api/skill-gap/analyze
```

---

# Assessment Flow

```
Student
    │
    ▼
Start Assessment
    │
    ▼
Adaptive Quiz
    │
    ▼
Question Selection
    │
    ▼
Difficulty Adaptation
    │
    ▼
Skill Score Calculation
    │
    ▼
Store Student Skill Results
    │
    ▼
Assessment Completed
    │
    ▼
Skill Gap Analysis
    │
    ▼
Readiness Score
    │
    ▼
Missing Skills
    │
    ▼
Skill Gap Report
```

---

# Future Enhancements

- JWT Authentication
- Student Dashboard
- Admin Dashboard
- AI Course Recommendation Engine
- Personalized Learning Paths
- Performance Prediction
- Assignment Evaluation
- Certificate Generation
- Certificate Verification
- Industry Readiness Analytics
- AI Interview Assessment

---

# Developed By

**Vayvora Technologies Pvt. Ltd.**

AI • Enterprise SaaS • EdTech