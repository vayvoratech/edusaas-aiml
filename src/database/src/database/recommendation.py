import os
import random
from datetime import datetime, timedelta

from dotenv import load_dotenv
from faker import Faker
from sqlalchemy import create_engine, text


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Final Recommendation database
DB_NAME = "eduai_db"

# Final Recommendation schema
SCHEMA = "education"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

fake = Faker()


# ============================================================
# DATA SIZE
# ============================================================

NUM_USERS = 1000
NUM_COURSES = 100
NUM_ENROLLMENTS = 3000
NUM_RATINGS = 2000


# ============================================================
# ROLES
# ============================================================

def create_roles(connection):

    roles = [
        ("student", "Student user"),
        ("educator", "Course educator"),
        ("admin", "System administrator"),
    ]

    role_ids = {}

    for name, description in roles:

        existing = connection.execute(
            text(f"""
                SELECT id
                FROM {SCHEMA}.roles
                WHERE name = :name
                LIMIT 1
            """),
            {
                "name": name
            }
        ).fetchone()

        if existing:
            role_ids[name] = existing.id

        else:
            result = connection.execute(
                text(f"""
                    INSERT INTO {SCHEMA}.roles
                        (name, description)
                    VALUES
                        (:name, :description)
                    RETURNING id
                """),
                {
                    "name": name,
                    "description": description
                }
            )

            role_ids[name] = result.scalar_one()

    print(f"✅ Roles ready: {len(role_ids)}")

    return role_ids


# ============================================================
# DOMAIN ROLES
# ============================================================

def create_domain_roles(connection):

    domain_roles = [
        ("AI Engineer", "Artificial Intelligence"),
        ("Machine Learning Engineer", "Artificial Intelligence"),
        ("Data Scientist", "Data"),
        ("Data Analyst", "Data"),
        ("Data Engineer", "Data"),
        ("Generative AI Engineer", "Artificial Intelligence"),
        ("MLOps Engineer", "Artificial Intelligence"),
        ("Backend Developer", "Software Development"),
        ("Full Stack Developer", "Software Development"),
        ("Frontend Developer", "Software Development"),
        ("Cloud Engineer", "Cloud Computing"),
        ("DevOps Engineer", "Cloud Computing"),
        ("Cybersecurity Analyst", "Cybersecurity"),
        ("Software Development Engineer", "Software Development"),
        ("Mobile Application Developer", "Software Development"),
        ("UI/UX Designer", "Design"),
        ("Business Intelligence Developer", "Data"),
        ("Blockchain Developer", "Blockchain"),
        ("IoT Engineer", "Internet of Things"),
        ("Robotics and Computer Vision Engineer", "Artificial Intelligence"),
        ("Software Test Engineer", "Software Testing"),
    ]

    domain_role_ids = []

    for domain_name, category in domain_roles:

        existing = connection.execute(
            text(f"""
                SELECT domain_role_id
                FROM {SCHEMA}.domain_roles
                WHERE domain_name = :domain_name
                LIMIT 1
            """),
            {
                "domain_name": domain_name
            }
        ).fetchone()

        if existing:

            domain_role_ids.append(
                existing.domain_role_id
            )

        else:

            result = connection.execute(
                text(f"""
                    INSERT INTO {SCHEMA}.domain_roles
                        (
                            domain_name,
                            category
                        )
                    VALUES
                        (
                            :domain_name,
                            :category
                        )
                    RETURNING domain_role_id
                """),
                {
                    "domain_name": domain_name,
                    "category": category
                }
            )

            domain_role_ids.append(
                result.scalar_one()
            )

    print(
        f"✅ Domain roles ready: "
        f"{len(domain_role_ids)}"
    )

    return domain_role_ids


# ============================================================
# SKILLS
# ============================================================

def create_skills(connection):

    skills = [
        ("Python", "Programming"),
        ("SQL", "Database"),
        ("Machine Learning", "Artificial Intelligence"),
        ("Deep Learning", "Artificial Intelligence"),
        ("Natural Language Processing", "Artificial Intelligence"),
        ("Computer Vision", "Artificial Intelligence"),
        ("Generative AI", "Artificial Intelligence"),
        ("LLMs", "Generative AI"),
        ("RAG", "Generative AI"),
        ("Prompt Engineering", "Generative AI"),
        ("LangChain", "Generative AI"),
        ("LangGraph", "Generative AI"),
        ("TensorFlow", "Deep Learning"),
        ("PyTorch", "Deep Learning"),
        ("Scikit-learn", "Machine Learning"),
        ("Pandas", "Data Science"),
        ("NumPy", "Data Science"),
        ("Power BI", "Data Analytics"),
        ("Apache Spark", "Data Engineering"),
        ("ETL", "Data Engineering"),
        ("AWS", "Cloud"),
        ("Azure", "Cloud"),
        ("GCP", "Cloud"),
        ("Docker", "DevOps"),
        ("Kubernetes", "DevOps"),
        ("FastAPI", "Backend"),
        ("Flask", "Backend"),
        ("PostgreSQL", "Database"),
        ("Databricks", "Data Engineering"),
        ("Snowflake", "Data Engineering"),
    ]

    skill_ids = []

    for skill_name, category in skills:

        existing = connection.execute(
            text(f"""
                SELECT skill_id
                FROM {SCHEMA}.skills
                WHERE skill_name = :skill_name
                LIMIT 1
            """),
            {
                "skill_name": skill_name
            }
        ).fetchone()

        if existing:

            skill_ids.append(
                existing.skill_id
            )

        else:

            result = connection.execute(
                text(f"""
                    INSERT INTO {SCHEMA}.skills
                        (
                            skill_name,
                            category,
                            description
                        )
                    VALUES
                        (
                            :skill_name,
                            :category,
                            :description
                        )
                    RETURNING skill_id
                """),
                {
                    "skill_name": skill_name,
                    "category": category,
                    "description": (
                        f"{skill_name} skill used for "
                        "learning and career development."
                    )
                }
            )

            skill_ids.append(
                result.scalar_one()
            )

    print(
        f"✅ Skills ready: "
        f"{len(skill_ids)}"
    )

    return skill_ids


# ============================================================
# USERS
# ============================================================

def create_users(
    connection,
    role_ids,
    domain_role_ids
):

    student_role_id = role_ids["student"]

    user_ids = []

    for _ in range(NUM_USERS):

        first_name = fake.first_name()
        last_name = fake.last_name()

        email = fake.unique.email()

        result = connection.execute(
            text(f"""
                INSERT INTO {SCHEMA}.users
                    (
                        name,
                        email,
                        role_id,
                        password_hash,
                        status,
                        last_login,
                        domain_role_id
                    )
                VALUES
                    (
                        :name,
                        :email,
                        :role_id,
                        :password_hash,
                        :status,
                        :last_login,
                        :domain_role_id
                    )
                RETURNING id
            """),
            {
                "name": (
                    f"{first_name} "
                    f"{last_name}"
                ),
                "email": email,
                "role_id": student_role_id,
                "password_hash": (
                    "faker-test-password-hash"
                ),
                "status": "active",
                "last_login": (
                    datetime.now()
                    - timedelta(
                        days=random.randint(
                            0,
                            30
                        )
                    )
                ),
                "domain_role_id": random.choice(
                    domain_role_ids
                )
            }
        )

        user_ids.append(
            result.scalar_one()
        )

    print(
        f"✅ Users created: "
        f"{len(user_ids)}"
    )

    return user_ids


# ============================================================
# COURSES
# ============================================================

def create_courses(
    connection,
    user_ids
):

    course_data = [
        (
            "Python for Beginners",
            "Programming"
        ),
        (
            "Advanced Python",
            "Programming"
        ),
        (
            "SQL for Data Science",
            "Data Science"
        ),
        (
            "Machine Learning Fundamentals",
            "Artificial Intelligence"
        ),
        (
            "Deep Learning with PyTorch",
            "Artificial Intelligence"
        ),
        (
            "Natural Language Processing",
            "Artificial Intelligence"
        ),
        (
            "Generative AI Fundamentals",
            "Generative AI"
        ),
        (
            "RAG Application Development",
            "Generative AI"
        ),
        (
            "Data Science with Python",
            "Data Science"
        ),
        (
            "Power BI Analytics",
            "Data Analytics"
        ),
        (
            "Data Engineering with Spark",
            "Data Engineering"
        ),
        (
            "Cloud Computing Fundamentals",
            "Cloud"
        ),
        (
            "AWS for Beginners",
            "Cloud"
        ),
        (
            "Azure Data Engineering",
            "Cloud"
        ),
        (
            "Docker and Kubernetes",
            "DevOps"
        ),
        (
            "FastAPI Development",
            "Backend"
        ),
        (
            "Computer Vision",
            "Artificial Intelligence"
        ),
        (
            "Transformers and LLMs",
            "Generative AI"
        ),
        (
            "MLOps Fundamentals",
            "MLOps"
        ),
        (
            "Advanced SQL",
            "Database"
        ),
    ]

    course_ids = []

    # Select educators from existing users
    educator_ids = random.sample(
        user_ids,
        min(20, len(user_ids))
    )

    # Change selected users to educator
    for educator_id in educator_ids:

        connection.execute(
            text(f"""
                UPDATE {SCHEMA}.users
                SET role_id = (
                    SELECT id
                    FROM {SCHEMA}.roles
                    WHERE name = 'educator'
                    LIMIT 1
                )
                WHERE id = :user_id
            """),
            {
                "user_id": educator_id
            }
        )

    for i in range(NUM_COURSES):

        if i < len(course_data):

            title, category = course_data[i]

        else:

            title = (
                f"Technology Course "
                f"{i + 1}"
            )

            category = random.choice(
                [
                    "Programming",
                    "Data Science",
                    "Artificial Intelligence",
                    "Cloud",
                    "Data Engineering"
                ]
            )

        result = connection.execute(
            text(f"""
                INSERT INTO {SCHEMA}.courses
                    (
                        title,
                        description,
                        provider,
                        category,
                        difficulty,
                        status,
                        educator_id
                    )
                VALUES
                    (
                        :title,
                        :description,
                        :provider,
                        :category,
                        :difficulty,
                        :status,
                        :educator_id
                    )
                RETURNING id
            """),
            {
                "title": title,
                "description": (
                    f"Learn {title} "
                    "through practical lessons."
                ),
                "provider": "EduSaaS",
                "category": category,
                "difficulty": random.choice(
                    [
                        "Beginner",
                        "Intermediate",
                        "Advanced"
                    ]
                ),
                "status": "active",
                "educator_id": random.choice(
                    educator_ids
                )
            }
        )

        course_ids.append(
            result.scalar_one()
        )

    print(
        f"✅ Courses created: "
        f"{len(course_ids)}"
    )

    return course_ids


# ============================================================
# ENROLLMENTS
# ============================================================

def create_enrollments(
    connection,
    user_ids,
    course_ids
):

    enrollment_pairs = set()

    while len(enrollment_pairs) < NUM_ENROLLMENTS:

        enrollment_pairs.add(
            (
                random.choice(user_ids),
                random.choice(course_ids)
            )
        )

    for user_id, course_id in enrollment_pairs:

        connection.execute(
            text(f"""
                INSERT INTO {SCHEMA}.enrollments
                    (
                        user_id,
                        course_id,
                        status,
                        completion_percentage,
                        enrolled_at
                    )
                VALUES
                    (
                        :user_id,
                        :course_id,
                        :status,
                        :completion_percentage,
                        :enrolled_at
                    )
            """),
            {
                "user_id": user_id,
                "course_id": course_id,
                "status": random.choice(
                    [
                        "active",
                        "completed",
                        "dropped"
                    ]
                ),
                "completion_percentage": round(
                    random.uniform(
                        0,
                        100
                    ),
                    2
                ),
                "enrolled_at": (
                    datetime.now()
                    - timedelta(
                        days=random.randint(
                            1,
                            365
                        )
                    )
                )
            }
        )

    print(
        f"✅ Enrollments created: "
        f"{len(enrollment_pairs)}"
    )


# ============================================================
# COURSE SKILLS
# ============================================================

def create_course_skills(
    connection,
    course_ids,
    skill_ids
):

    mappings = set()

    for course_id in course_ids:

        selected_skills = random.sample(
            skill_ids,
            random.randint(
                2,
                5
            )
        )

        for skill_id in selected_skills:

            mappings.add(
                (
                    course_id,
                    skill_id
                )
            )

    for course_id, skill_id in mappings:

        connection.execute(
            text(f"""
                INSERT INTO {SCHEMA}.course_skills
                    (
                        course_id,
                        skill_id,
                        skill_level
                    )
                VALUES
                    (
                        :course_id,
                        :skill_id,
                        :skill_level
                    )
                ON CONFLICT DO NOTHING
            """),
            {
                "course_id": course_id,
                "skill_id": skill_id,
                "skill_level": random.randint(
                    1,
                    5
                )
            }
        )

    print(
        f"✅ Course-skill mappings created: "
        f"{len(mappings)}"
    )


# ============================================================
# COURSE PREREQUISITES
# ============================================================

def create_course_prerequisites(
    connection,
    course_ids
):

    mappings = set()

    for i in range(
        1,
        len(course_ids)
    ):

        mappings.add(
            (
                course_ids[i],
                course_ids[i - 1]
            )
        )

    for (
        course_id,
        prerequisite_course_id
    ) in mappings:

        connection.execute(
            text(f"""
                INSERT INTO {SCHEMA}.course_prerequisites
                    (
                        course_id,
                        prerequisite_course_id
                    )
                VALUES
                    (
                        :course_id,
                        :prerequisite_course_id
                    )
                ON CONFLICT DO NOTHING
            """),
            {
                "course_id": course_id,
                "prerequisite_course_id": (
                    prerequisite_course_id
                )
            }
        )

    print(
        f"✅ Course prerequisites created: "
        f"{len(mappings)}"
    )


# ============================================================
# COURSE RATINGS
# ============================================================

def create_course_ratings(
    connection,
    user_ids,
    course_ids
):

    rating_pairs = set()

    while len(rating_pairs) < NUM_RATINGS:

        rating_pairs.add(
            (
                random.choice(user_ids),
                random.choice(course_ids)
            )
        )

    for user_id, course_id in rating_pairs:

        connection.execute(
            text(f"""
                INSERT INTO {SCHEMA}.course_ratings
                    (
                        user_id,
                        course_id,
                        rating
                    )
                VALUES
                    (
                        :user_id,
                        :course_id,
                        :rating
                    )
                ON CONFLICT DO NOTHING
            """),
            {
                "user_id": user_id,
                "course_id": course_id,
                "rating": round(
                    random.uniform(
                        1,
                        5
                    ),
                    1
                )
            }
        )

    print(
        f"✅ Course ratings created: "
        f"{len(rating_pairs)}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("EduSaaS Recommendation Data Generator")
    print("=" * 60)
    print(f"Database : {DB_NAME}")
    print(f"Schema   : {SCHEMA}")
    print("=" * 60)

    try:

        with engine.begin() as connection:

            # 1. Roles
            role_ids = create_roles(
                connection
            )

            # 2. Domain roles
            domain_role_ids = create_domain_roles(
                connection
            )

            # 3. Skills
            skill_ids = create_skills(
                connection
            )

            # 4. Users
            user_ids = create_users(
                connection,
                role_ids,
                domain_role_ids
            )

            # 5. Courses
            course_ids = create_courses(
                connection,
                user_ids
            )

            # 6. Enrollments
            create_enrollments(
                connection,
                user_ids,
                course_ids
            )

            # 7. Course skills
            create_course_skills(
                connection,
                course_ids,
                skill_ids
            )

            # 8. Prerequisites
            create_course_prerequisites(
                connection,
                course_ids
            )

            # 9. Ratings
            create_course_ratings(
                connection,
                user_ids,
                course_ids
            )

        print()
        print("=" * 60)
        print(
            "🎉 Recommendation synthetic data "
            "generated successfully!"
        )
        print("=" * 60)

    except Exception as e:

        print()
        print("=" * 60)
        print("❌ DATA GENERATION FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()