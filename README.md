# EduSaaS – Adaptive Skill Assessment Platform

## Overview

EduSaaS is an AI-powered adaptive skill assessment platform designed to evaluate a student's technical skills based on their selected job role. The system conducts an adaptive quiz, identifies skill gaps, and recommends personalized learning paths.

The project is built using Flask and PostgreSQL and follows a modular architecture for scalability.

---

## Features

- User Registration
- Job Role Selection
- Adaptive Quiz Engine
- Skill-wise Assessment
- Difficulty Level Adjustment
- Skill Gap Analysis
- Personalized Course Recommendation
- PostgreSQL Database
- REST API using Flask

---

## Technology Stack

### Backend
- Python 3.x
- Flask

### Database
- PostgreSQL

### Frontend
- HTML
- CSS
- Jinja2 Templates

### Version Control
- Git
- GitHub

---

## Project Structure

```
EduSaaS/
│
├── app.py
├── main.py
├── config/
│   ├── db_connection.py
│   └── settings.py
│
├── routes/
│   ├── home.py
│   └── quiz.py
│
├── services/
│   └── adaptive_engine.py
│
├── templates/
│   ├── index.html
│   └── quiz.html
│
├── static/
│   └── css/
│       └── style.css
│
├── question_bank/
│   ├── python_questions.csv
│   ├── sql_questions.csv
│   ├── machine_learning_questions.csv
│   ├── deep_learning_questions.csv
│   └── git_questions.csv
│
├── database/
│   └── schema.sql
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Database Modules

- Users
- Domain Roles
- Skills
- Domain Required Skills
- Questions
- Difficulty Levels
- Quiz Sessions
- Student Answers
- Student Skill Results

---

## Adaptive Quiz Flow

1. Student enters name and email.
2. Student selects a target job role.
3. A quiz session is created.
4. Required skills for the selected role are loaded.
5. Questions begin at Easy difficulty.
6. Difficulty changes dynamically based on performance.
7. Skill scores are calculated.
8. Skill gaps are identified.
9. Learning recommendations are generated.

---

## Installation

### Clone Repository

```bash
git clone https://github.com/<your-username>/edusaas.git
```

### Move into Project

```bash
cd edusaas
```

### Create Virtual Environment

Windows

```bash
python -m venv venv
```

Activate

```bash
venv\Scripts\activate
```

Linux/Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Database

Create a PostgreSQL database and execute your SQL schema.

Update the database configuration in:

```
config/settings.py
```

---

## Run the Application

```bash
python app.py
```

or

```bash
flask run
```

---

## Future Enhancements

- JWT Authentication
- Admin Dashboard
- Student Dashboard
- AI-based Course Recommendation
- Performance Analytics
- Assignment Evaluation
- Certificate Generation

---