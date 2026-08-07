# EduAI Recommendation System - Project Documentation

## Project
AI-Based Education Recommendation System

---

# Day 1 - Project Setup

## Tasks Completed
- Created project structure
- Created GitHub repository
- Configured Git
- Created virtual environment
- Installed required Python libraries

## Status
Completed

---

# Day 2 - PostgreSQL Database Setup & Synthetic Data

## Tasks Completed

### Database
- Installed PostgreSQL
- Created database: eduai_db
- Created tables:
  - students
  - courses
  - enrollments

### Database Connection
- Connected Python application to PostgreSQL using SQLAlchemy
- Verified successful connection

### Synthetic Data Generation
- Generated 1000 student records
- Generated 50 course records
- Generated 5000 enrollment records

### Technologies Used
- Python
- PostgreSQL
- SQLAlchemy
- Pandas
- Faker

### Database Status

| Table | Records |
|--------|---------|
| students | 1000 |
| courses | 50 |
| enrollments | 5000 |

## Outcome
Database setup is complete, and synthetic data has been populated successfully.

---

# Day 3 (Planned)

## Tasks
- Exploratory Data Analysis (EDA)
- Data preprocessing
- Feature engineering
- Recommendation model developmentm.

# Day 3 - Data Cleaning & Feature Engineering

## Objective
Prepare the recommendation system dataset for machine learning by cleaning the data and engineering relevant features.

---

## Data Cleaning

### Tasks Performed

- Loaded data from PostgreSQL database.
- Removed duplicate records from:
  - students
  - courses
  - enrollments
- Removed rows containing missing values.
- Standardized text columns by removing extra spaces and formatting values consistently.
- Validated student age and retained records within the valid age range.
- Verified dataset integrity after cleaning.

### Output

Clean datasets ready for feature engineering and model training.

---

## Feature Engineering

### Tasks Performed

- Loaded cleaned data from PostgreSQL.
- Merged the following tables:
  - students
  - enrollments
  - courses
- Created a unified dataset for recommendation model training.
- Encoded categorical features using Label Encoding:
  - gender
  - skill_level
  - interest_area
  - category
  - difficulty_level
- Prepared numerical features for machine learning.
- Saved the processed dataset for model development.

### Features Used

#### Student Features
- student_id
- age
- gender
- skill_level
- interest_area

#### Course Features
- course_id
- category
- difficulty_level
- duration_hours

#### Enrollment Features
- completion_percentage
- watch_time_minutes
- quiz_score
- rating

---

## Output Dataset

Processed dataset created for recommendation model training.

Location:

data/processed_recommendation_data.csv

---

## Technologies Used

- Python
- Pandas
- SQLAlchemy
- Scikit-learn
- PostgreSQL

---

## Outcome

Successfully prepared a machine learning-ready dataset by cleaning, merging, and transforming data from multiple PostgreSQL tables. The processed dataset is ready for recommendation model implementation.

---

## Next Task

- Implement Content-Based Recommendation
- Implement Collaborative Filtering
- Develop Hybrid Recommendation 


## 📌 Content-Based Recommendation Model

### Objective

Develop a recommendation system that suggests similar courses based on course attributes rather than user behavior.

---

## Approach

A Content-Based Recommendation System recommends courses by comparing the characteristics of each course. Instead of using other students' preferences, it analyzes the content (features) of the courses.

For this implementation, the following course attributes were used:

- Course Category
- Difficulty Level

These features were combined into a single text feature and converted into numerical vectors for similarity computation.

---

## Workflow

```
Load Courses from PostgreSQL
            │
            ▼
Combine Category + Difficulty
            │
            ▼
Convert Text to Numerical Vectors
(CountVectorizer)
            │
            ▼
Calculate Course Similarity
(Cosine Similarity)
            │
            ▼
Recommend Top Similar Courses
```

---

## Technologies Used

- Python
- Pandas
- PostgreSQL
- SQLAlchemy
- Scikit-learn

---

## Machine Learning Techniques

### CountVectorizer

Converts textual course information into numerical feature vectors.

Example:

Before:

```
Python Beginner
```

After:

```
[1,1,0,0]
```

This allows machine learning algorithms to compare courses mathematically.

---

### Cosine Similarity

Calculates the similarity between every pair of courses.

Similarity Score Range:

- 1.0 → Exactly Similar
- 0.0 → Completely Different

The model recommends courses with the highest similarity scores.

---

## Features Used

### Course Features

- course_name
- category
- difficulty_level

---

## Output

Input:

```
Python Course 1
```

Example Output:

```
Python Course 8
Machine Learning Course 15
SQL Course 22
Data Science Course 30
Deep Learning Course 41
```

The system returns the Top 5 most similar courses.

---

## Advantages

- Simple and fast recommendation system.
- Does not require user ratings.
- Easy to scale for new courses.
- Useful for cold-start courses where no enrollment history exists.

---

## Current Limitations

This implementation only considers:

- Course Category
- Difficulty Level

It does not yet use learner-specific information such as:

- Student Interests
- Skill Level
- Course Ratings
- Completion Percentage
- Quiz Scores
- Watch Time

---

## Future Improvements

The recommendation engine will be enhanced into a Hybrid Recommendation System by integrating:

- Collaborative Filtering
- Student Learning History
- Course Ratings
- Watch Time
- Quiz Performance
- Skill Gap Analysis

This will generate personalized recommendations based on both course similarity and learner behavior.

---

## Status

✅ Content-Based Recommendation Model Implemented

Next Module:

➡️ Collaborative Filtering Recommendation


## Collaborative Filtering Recommendation

### Objective

Recommend courses based on learner behavior and historical ratings.

---

### Algorithm

Singular Value Decomposition (SVD)

---

### Dataset

The model was trained using:

- student_id
- course_id
- rating

---

### Workflow

PostgreSQL
↓

Load Enrollment Data
↓

Train-Test Split

↓

SVD Model Training

↓

Predict Ratings

↓

Evaluate using RMSE

---

### Evaluation Metric

Root Mean Squared Error (RMSE)

Obtained RMSE:

1.4513

---

### Technologies Used

- Python
- Pandas
- PostgreSQL
- SQLAlchemy
- Scikit-Surprise

---

### Output

The model predicts the rating a student is likely to give a course.

These predicted ratings are used to recommend courses the learner has not yet taken.

---

### Status

✅ Implemented Successfully


## Hybrid Recommendation System

### Objective

Develop a Hybrid Recommendation System by combining Content-Based Recommendation and Collaborative Filtering to provide personalized course recommendations.

---

## Overview

The Hybrid Recommendation System combines:

- **Content-Based Filtering** – Recommends courses based on course attributes such as category and difficulty level.
- **Collaborative Filtering** – Recommends courses based on learner ratings and behavior.

This approach improves recommendation quality by considering both course similarity and student preferences.

---

## Workflow

```
                 PostgreSQL
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
   Courses Table             Enrollments Table
        │                           │
        ▼                           ▼
Content-Based Model       Collaborative Filtering
        │                           │
        └─────────────┬─────────────┘
                      │
                      ▼
          Hybrid Recommendation Engine
                      │
                      ▼
          Top Recommended Courses
```

---

## Technologies Used

- Python
- PostgreSQL
- Pandas
- SQLAlchemy
- Scikit-learn
- Scikit-Surprise

---

## Data Used

### Courses Table

- course_id
- course_name
- category
- difficulty_level

### Enrollments Table

- student_id
- course_id
- rating

---

## Implementation Steps

### Step 1

Load course and enrollment data from PostgreSQL.

### Step 2

Generate course similarity using:

- CountVectorizer
- Cosine Similarity

### Step 3

Train the Collaborative Filtering model using the SVD algorithm.

### Step 4

Retrieve similar courses using the Content-Based model.

### Step 5

Predict each student's expected rating for those courses using Collaborative Filtering.

### Step 6

Rank the recommendations based on predicted ratings.

---

## Model Components

### Content-Based Filtering

Uses:

- Course Category
- Difficulty Level

Purpose:

Find courses similar to the selected course.

---

### Collaborative Filtering

Uses:

- Student ID
- Course ID
- Rating

Purpose:

Predict how much a student is likely to prefer each course.

---

## Recommendation Strategy

The system first identifies courses similar to the selected course and then predicts how much the target student will like each of those courses.

The recommendations are sorted according to the predicted rating and the highest-ranked courses are returned.

---

## Output

Input

```
Student ID : 1

Selected Course :
Python Course 1
```

Example Output

```
Machine Learning Course 12

Predicted Rating : 4.82

------------------------

SQL Course 8

Predicted Rating : 4.71

------------------------

Deep Learning Course 16

Predicted Rating : 4.65
```

---

## Advantages

- Produces more personalized recommendations.
- Combines learner preferences with course similarity.
- Reduces limitations of using only one recommendation approach.
- Easily scalable for large educational datasets.

---

## Current Status

- ✅ Content-Based Recommendation Completed
- ✅ Collaborative Filtering Completed
- ✅ Hybrid Recommendation System Completed

---

## Next Phase

FastAPI Integration

The hybrid recommendation model will be deployed as a REST API to serve recommendations to the EduAI SaaS platform.
