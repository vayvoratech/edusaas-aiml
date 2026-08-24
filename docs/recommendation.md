
# EduSaaS — Recommendation Engine

## Production-Level Technical Documentation

### 1. Module Overview

**Module:** Course Recommendation Engine
**Purpose:** Generate personalized course recommendations for a learner based on:

* Existing course catalog
* Learner-course ratings
* Learner domain/role
* Course content
* Course difficulty/category
* Course prerequisites
* Previously completed courses

The implementation is a **hybrid recommendation system** combining:

1. **Content-Based Filtering**
2. **Collaborative Filtering using SVD**
3. **Learner Profile Matching**
4. **Prerequisite Validation**
5. **Confidence-based ranking**
6. **Recommendation explanation**

The finalized backend schema extends the existing `education.recommendations` table rather than creating a duplicate recommendation table. 

---

# 2. Production Architecture

```text
                    Client / Frontend
                           │
                           ▼
                    Node.js Backend
                         :3000
                           │
                           │ Fetch learner + course data
                           ▼
                    PostgreSQL
                   education schema
                           │
                           │
                           ▼
              Node Recommendation Service
                           │
                           │ HTTP JSON
                           ▼
                  Python FastAPI
                     :8000
                           │
                           ▼
              Recommendation Engine
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    Content-Based      SVD Model      Profile Matching
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                 Confidence Calculation
                           │
                           ▼
              Prerequisite Validation
                           │
                           ▼
                  Final Ranking
                           │
                           ▼
                  Top 5 Courses
                           │
                           ▼
                     Node.js
                           │
                           ▼
               education.recommendations
```

**Critical architectural rule:** Python does not directly connect to PostgreSQL at runtime. The recommendation implementation explicitly expects the Node.js backend to supply the data. 

---

# 3. Input Data

Node provides the recommendation engine with the following datasets.

### Courses

```text
id
title
description
provider
category
difficulty
status
educator_id
```

These are the required course fields consumed by the recommendation engine. 

### Ratings

```text
user_id
course_id
rating
```

Ratings form the user-item interaction matrix used by the SVD collaborative filtering component. 

### User

The engine consumes learner profile information including:

```text
user_id
domain_name
domain_category
```

The finalized backend identifies `education.users` as the canonical learner identity. 

### Prerequisites

```text
course_id
prerequisite_course_id
```

### Completed Courses

```text
id
title
```

The engine uses these to construct the learner's learning pathway and validate prerequisites.

---

# 4. Content-Based Recommendation

Course information is converted into a textual feature representation:

```text
title
+
description
+
category
+
difficulty
```

The implementation creates:

```python
CountVectorizer(
    stop_words="english"
)
```

and transforms the course features into a vector space. 

### Similarity

Cosine similarity is calculated between course vectors:

```text
Course A ─────┐
              │
              ├── Cosine Similarity
              │
Course B ─────┘
```

The similarity score represents how closely related two courses are based on their textual metadata.



---

# 5. Collaborative Filtering

The system uses:

**Algorithm:** SVD
**Library:** Surprise

The rating range is:

```text
1 – 5
```

The training data consists of:

```text
user_id
course_id
rating
```

The SVD model learns latent user/course preference patterns. 

For each candidate course:

```python
svd_model.predict(
    str(user_id),
    str(course["id"])
).est
```

produces the predicted learner rating. 

---

# 6. Profile Matching

The system also considers the learner's:

```text
domain_name
domain_category
```

against course metadata.

For example:

```text
Learner domain:
Data Science

Course category:
Data Science
```

produces a positive profile match.

This allows the system to incorporate learner career/domain context instead of relying exclusively on historical ratings. 

---

# 7. Hybrid Recommendation

The recommendation engine combines multiple signals:

```text
                    Candidate Course
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
 Content Similarity   SVD Rating       Profile Match
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                  Confidence Calculator
                           │
                           ▼
                    Recommendation
```

The implementation also uses:

```text
ConfidenceCalculator
ExplanationEngine
```

to generate the recommendation confidence and human-readable recommendation reason. 

---

# 8. Candidate Generation

The system first calculates similarity against the input course.

It then selects candidate courses from the most similar courses rather than evaluating the entire catalog indiscriminately. The implementation considers the next candidate courses after the input course in similarity order. 

For each candidate it calculates:

```text
similarity_score
predicted_rating
profile_score
confidence_score
```

---

# 9. Prerequisite Validation

Prerequisites are checked before the recommendation is finalized.

Example:

```text
Recommended:
Advanced Python

Prerequisite:
Python Fundamentals

Learner completed:
Python Fundamentals
```

Result:

```text
prerequisite_completed = true
```

If the prerequisite course is not present in the learner's completed-course set:

```text
prerequisite_completed = false
```

The implementation performs this validation using:

```text
course_prerequisites
+
completed_courses
```

before generating the final recommendation object. 

---

# 10. Recommendation Explanation

Each recommendation receives a generated explanation using:

```text
ExplanationEngine
```

The explanation is based on:

```text
course name
predicted rating
confidence score
prerequisite status
```



Example response conceptually:

```json
{
  "course_name": "Advanced Python",
  "predicted_rating": 4.62,
  "similarity_score": 0.81,
  "confidence_score": 0.87,
  "recommendation_reason": "...",
  "prerequisite_completed": true
}
```

---

# 11. Final Ranking

Recommendations are sorted using:

1. `confidence_score`
2. `predicted_rating`
3. `similarity_score`

in descending order.

Only the **top 5 recommendations** are returned. 

Conceptually:

```text
Confidence
    ↓
Predicted Rating
    ↓
Similarity
    ↓
Final Rank
```

---

# 12. Learning Pathway

The system also produces a learning pathway.

It combines:

```text
Completed Courses
        +
Recommended Courses
```

Completed courses are marked:

```text
COMPLETED
```

Recommended courses are marked:

```text
RECOMMENDED
```



Final response structure:

```json
{
  "user_id": "...",
  "course_name": "...",
  "recommendations": [],
  "learning_pathway": []
}
```



---

# 13. Database Integration

The production database uses:

```text
education.recommendations
```

The table already exists in the backend schema.

AI-specific fields are:

```text
predicted_rating
similarity_score
confidence_score
prerequisite_completed
rank
```

The backend specification explicitly says to **extend the existing table rather than create a duplicate recommendation table**. 

The corresponding AI fields are defined as:

| Column                 | Type             | Purpose                          |
| ---------------------- | ---------------- | -------------------------------- |
| predicted_rating       | DOUBLE PRECISION | SVD predicted learner preference |
| similarity_score       | DOUBLE PRECISION | Content similarity               |
| confidence_score       | DOUBLE PRECISION | Recommendation confidence        |
| prerequisite_completed | BOOLEAN          | Prerequisite validation          |
| rank                   | INTEGER          | Final recommendation order       |



---

# 14. Runtime Data Flow

The production flow is:

```text
1. Frontend requests recommendations
              ↓
2. Node receives user_id + course_name
              ↓
3. Node queries PostgreSQL
              ↓
4. Node collects:
      • courses
      • ratings
      • user profile
      • prerequisites
      • completed courses
              ↓
5. Node sends JSON to Python
              ↓
6. Python creates DataFrames
              ↓
7. Content similarity calculated
              ↓
8. SVD prediction calculated
              ↓
9. Profile matching calculated
              ↓
10. Prerequisites validated
              ↓
11. Confidence calculated
              ↓
12. Recommendations ranked
              ↓
13. Top 5 returned
              ↓
14. Node receives result
              ↓
15. Node persists recommendation data
              ↓
16. API response returned
```

This separation keeps **database ownership in Node** and **ML computation in Python**.

---

# 15. API Contract

### Request

Conceptually:

```http
POST /api/recommendation/recommend
Content-Type: application/json
```

with:

```json
{
  "user_id": "USER_UUID",
  "course_name": "Python for Beginners"
}
```

Node enriches this request with the database data required by Python.

### Python service payload

The Python recommendation engine expects:

```text
user_id
course_name
courses
ratings
user
prerequisites
completed_courses
```

This is explicitly represented in the Node-provided request implementation. 

---

# 16. Error Handling

The recommendation service validates important runtime conditions.

### No courses

```text
No active courses were provided by Node.js.
```

### Course not found

```text
Course '<course_name>' not found.
```

### User not found

```text
User '<user_id>' not found.
```

These validations prevent the model from producing recommendations from incomplete inputs. 

---

# 17. Production Security

### Python

Python should **not** contain:

```text
PostgreSQL credentials
DATABASE_URL
DB password
SQL queries
```

for runtime recommendation inference.

### Node

Node owns:

```text
PostgreSQL connection
DB credentials
data retrieval
prediction persistence
API authentication/authorization
```

### Environment variables

Sensitive configuration should remain in:

```text
.env
```

and `.env` must **not be committed to Git**.

---

# 18. Model/Data Considerations

The current implementation has an important characteristic:

> The current recommendation implementation retrains the SVD/vectorizer from the Node-provided data at runtime rather than depending on persisted model artifacts. 

Therefore the current architecture is:

```text
Node data
   ↓
Python
   ↓
Fit SVD + Vectorizer
   ↓
Generate recommendations
```

rather than:

```text
Pre-trained artifacts
       ↓
Load model
       ↓
Inference
```

This is important to document accurately for your manager.

---

# 19. Production Deployment

Recommended deployment structure:

```text
                    Load Balancer / API Gateway
                              │
                              ▼
                         Node.js API
                            :3000
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
           PostgreSQL                Python ML Service
                                      :8000
                                           │
                                           ▼
                                  Recommendation Engine
```

Python should be independently deployable as an ML microservice.

Node remains the application/backend layer.

---

# 20. Testing Checklist

### Python

```text
☐ Python service starts
☐ Health endpoint works
☐ Valid recommendation request works
☐ Invalid user handled
☐ Invalid course handled
☐ Empty course dataset handled
☐ Recommendation ranking works
☐ Prerequisite validation works
```

### Node

```text
☐ Node service starts
☐ PostgreSQL connection works
☐ Node → Python works
☐ Python response received
☐ Recommendation persistence works
☐ API response returned correctly
```

### Database

```text
☐ education.courses
☐ education.course_ratings
☐ education.users
☐ education.domain_roles
☐ education.course_prerequisites
☐ education.enrollments
☐ education.recommendations
```

---

# 21. Production Acceptance Criteria

The Recommendation module is considered production-ready when:

```text
✅ Python has no runtime DB connection
✅ Node owns PostgreSQL access
✅ Node → Python communication works
✅ SVD prediction works
✅ Content similarity works
✅ Profile matching works
✅ Prerequisite validation works
✅ Confidence calculation works
✅ Top 5 ranking works
✅ Learning pathway generated
✅ Recommendation data persisted
✅ UUID-based backend schema supported
✅ API errors handled
✅ Secrets excluded from Git
```


