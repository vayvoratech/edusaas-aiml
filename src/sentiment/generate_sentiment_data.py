import random

from faker import Faker
from sqlalchemy import create_engine, text


fake = Faker()


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------
# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

DB_USER = "postgres"
DB_PASSWORD = "Chinnu123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "eduai_db"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)


# --------------------------------------------------
# SENTIMENT EXAMPLES
# --------------------------------------------------

positive_posts = [
    "This course is very helpful.",
    "I really enjoyed this lesson.",
    "The explanation was clear and easy to understand.",
    "This assignment helped me understand the concept.",
    "The instructor explained the topic very well.",
    "I learned a lot from this module.",
    "The examples made the concept easy to understand.",
    "This was an excellent learning experience.",
    "The practical exercise was very useful.",
    "I finally understand this topic clearly."
]


negative_posts = [
    "This lesson was very confusing.",
    "I could not understand this topic.",
    "The explanation was difficult to follow.",
    "This assignment was frustrating.",
    "The examples did not help me understand the concept.",
    "I am struggling with this module.",
    "The instructions were unclear.",
    "This topic is extremely difficult for me.",
    "I did not understand the instructor's explanation.",
    "The exercise was confusing and difficult."
]


neutral_posts = [
    "The assignment is due tomorrow.",
    "The next class starts at 10 AM.",
    "I completed chapter three today.",
    "The quiz contains twenty questions.",
    "The instructor uploaded a new document.",
    "The next module covers SQL.",
    "I submitted the assignment yesterday.",
    "The course contains ten modules.",
    "The class duration is one hour.",
    "The project submission date is next week."
]


# --------------------------------------------------
# GENERATE DISCUSSION POSTS
# --------------------------------------------------

def generate_posts(number_of_posts=1000):

    records = []

    sentiment_data = {
        "POSITIVE": positive_posts,
        "NEGATIVE": negative_posts,
        "NEUTRAL": neutral_posts
    }

    labels = list(sentiment_data.keys())

    for _ in range(number_of_posts):

        sentiment = random.choice(labels)

        base_text = random.choice(
            sentiment_data[sentiment]
        )

        # Add a small amount of variation
        post_text = base_text

        if random.random() < 0.30:
            post_text = (
                f"{base_text} "
                f"{fake.sentence(nb_words=5)}"
            )

        record = {
            "student_id": random.randint(1, 1000),
            "course_id": random.randint(1, 50),
            "post_text": post_text,
            "sentiment": sentiment
        }

        records.append(record)

    return records


# --------------------------------------------------
# INSERT INTO POSTGRESQL
# --------------------------------------------------

def insert_posts(records):

    query = text("""
        INSERT INTO discussion_posts
        (
            student_id,
            course_id,
            post_text,
            sentiment
        )
        VALUES
        (
            :student_id,
            :course_id,
            :post_text,
            :sentiment
        )
    """)

    with engine.begin() as connection:

        connection.execute(
            query,
            records
        )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    posts = generate_posts(1000)

    insert_posts(posts)

    print(
        f"✅ {len(posts)} discussion posts "
        f"inserted successfully!"
    )