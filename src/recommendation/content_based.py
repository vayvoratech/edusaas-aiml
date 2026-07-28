import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# PostgreSQL Configuration
DB_USER = "postgres"
DB_PASSWORD = "Chinnu123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "eduai_db"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)

# Load Courses
courses = pd.read_sql("SELECT * FROM courses", engine)

# Combine important features
courses["features"] = (
    courses["category"] + " " +
    courses["difficulty_level"]
)

# Convert text into vectors
cv = CountVectorizer()

feature_matrix = cv.fit_transform(courses["features"])

# Similarity Matrix
similarity = cosine_similarity(feature_matrix)

print("Similarity Matrix Created Successfully")




def recommend(course_name):

    idx = courses[courses["course_name"] == course_name].index[0]

    distances = list(enumerate(similarity[idx]))

    distances = sorted(distances, key=lambda x: x[1], reverse=True)

    print(f"\nRecommended Courses for {course_name}\n")

    for i in distances[1:6]:

        print(courses.iloc[i[0]].course_name)






recommend(courses.iloc[0]["course_name"])





