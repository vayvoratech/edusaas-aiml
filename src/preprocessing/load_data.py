import pandas as pd
from sqlalchemy import create_engine

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

students = pd.read_sql("SELECT * FROM students", engine)
courses = pd.read_sql("SELECT * FROM courses", engine)
enrollments = pd.read_sql("SELECT * FROM enrollments", engine)

#----------------------------------------------------  

print(students.head())
print(courses.head())
print(enrollments.head())

print("\n========== STUDENTS ==========")
print(students.info())
print(students.describe(include="all"))

print("\n========== COURSES ==========")
print(courses.info())
print(courses.describe(include="all"))

print("\n========== ENROLLMENTS ==========")
print(enrollments.info())
print(enrollments.describe(include="all"))

#__________________________________________________________________________________

print("\nMissing Values")

print(students.isnull().sum())

print(courses.isnull().sum())

print(enrollments.isnull().sum())

#+________________________________________________________________
# CHECKING DUPLICATES 


print("\nDuplicate Students:", students.duplicated().sum())

print("Duplicate Courses:", courses.duplicated().sum())

print("Duplicate Enrollments:", enrollments.duplicated().sum())




#At this point we will know:
#Dataset size
#Data types
#Missing values
#Duplicate rows
#Basic statistics
