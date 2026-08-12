from sqlalchemy import create_engine, text
import random

# --------------------------------
# PostgreSQL Configuration
# --------------------------------

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


# --------------------------------
# Roles and Skills
# --------------------------------

roles_and_skills = {

    "Data Analyst": [
        "SQL",
        "Python",
        "Excel",
        "Power BI",
        "Statistics"
    ],

    "Data Scientist": [
        "Python",
        "SQL",
        "Statistics",
        "Machine Learning",
        "Data Visualization"
    ],

    "AI ML Engineer": [
        "Python",
        "Machine Learning",
        "Deep Learning",
        "NLP",
        "MLOps"
    ],

    "Data Engineer": [
        "SQL",
        "Python",
        "ETL",
        "Apache Spark",
        "Data Warehousing"
    ],

    "Cloud Engineer": [
        "Cloud Fundamentals",
        "Networking",
        "Docker",
        "Kubernetes",
        "DevOps"
    ]
}


# --------------------------------
# Question Templates
# --------------------------------

question_templates = {

    "EASY": {
        "weight": 1.0,
        "question": "Which option best represents a basic concept of {}?",
        "options": [
            "Basic Concept",
            "Advanced Deployment",
            "System Failure",
            "None of the above"
        ],
        "answer": "Basic Concept"
    },

    "AVERAGE": {
        "weight": 2.0,
        "question": "Which option represents practical application of {}?",
        "options": [
            "Applying concepts to solve a task",
            "Ignoring the problem",
            "Deleting the system",
            "None of the above"
        ],
        "answer": "Applying concepts to solve a task"
    },

    "HARD": {
        "weight": 3.0,
        "question": "What is the best approach when solving a complex {} problem?",
        "options": [
            "Analyze, design and validate the solution",
            "Guess randomly",
            "Ignore requirements",
            "Avoid testing"
        ],
        "answer": "Analyze, design and validate the solution"
    },

    "DIFFICULT": {
        "weight": 4.0,
        "question": "How should a real-world {} case study be approached?",
        "options": [
            "Analyze requirements, implement, evaluate and optimize",
            "Use random answers",
            "Skip analysis",
            "Avoid validation"
        ],
        "answer": "Analyze requirements, implement, evaluate and optimize"
    }
}


# --------------------------------
# Insert Roles, Skills, Questions
# --------------------------------

with engine.begin() as connection:

    for role_name, skills in roles_and_skills.items():

        # Insert role only if it doesn't exist
        connection.execute(
            text("""
                INSERT INTO job_roles (role_name, description)
                VALUES (:role_name, :description)
                ON CONFLICT (role_name) DO NOTHING
            """),
            {
                "role_name": role_name,
                "description": f"Assessment pathway for {role_name}"
            }
        )

        role_id = connection.execute(
            text("""
                SELECT role_id
                FROM job_roles
                WHERE role_name = :role_name
            """),
            {"role_name": role_name}
        ).scalar_one()

        for skill_name in skills:

            # Check whether this role-skill mapping already exists
            skill_id = connection.execute(
                text("""
                    SELECT skill_id
                    FROM skills
                    WHERE role_id = :role_id
                    AND skill_name = :skill_name
                    LIMIT 1
                """),
                {
                    "role_id": role_id,
                    "skill_name": skill_name
                }
            ).scalar()

            if skill_id is None:

                skill_id = connection.execute(
                    text("""
                        INSERT INTO skills (
                            role_id,
                            skill_name
                        )
                        VALUES (
                            :role_id,
                            :skill_name
                        )
                        RETURNING skill_id
                    """),
                    {
                        "role_id": role_id,
                        "skill_name": skill_name
                    }
                ).scalar_one()

            # Generate questions for each difficulty
            for difficulty, template in question_templates.items():

                question_text = template["question"].format(
                    skill_name
                )

                # Prevent duplicate questions
                existing_question = connection.execute(
                    text("""
                        SELECT question_id
                        FROM questions
                        WHERE role_id = :role_id
                        AND skill_id = :skill_id
                        AND difficulty = :difficulty
                        AND question_text = :question_text
                        LIMIT 1
                    """),
                    {
                        "role_id": role_id,
                        "skill_id": skill_id,
                        "difficulty": difficulty,
                        "question_text": question_text
                    }
                ).scalar()

                if existing_question is None:

                    options = template["options"]

                    connection.execute(
                        text("""
                            INSERT INTO questions (
                                role_id,
                                skill_id,
                                question_text,
                                question_type,
                                difficulty,
                                option_a,
                                option_b,
                                option_c,
                                option_d,
                                correct_answer,
                                weight
                            )
                            VALUES (
                                :role_id,
                                :skill_id,
                                :question_text,
                                'MCQ',
                                :difficulty,
                                :option_a,
                                :option_b,
                                :option_c,
                                :option_d,
                                :correct_answer,
                                :weight
                            )
                        """),
                        {
                            "role_id": role_id,
                            "skill_id": skill_id,
                            "question_text": question_text,
                            "difficulty": difficulty,
                            "option_a": options[0],
                            "option_b": options[1],
                            "option_c": options[2],
                            "option_d": options[3],
                            "correct_answer": template["answer"],
                            "weight": template["weight"]
                        }
                    )


print("✅ Adaptive Quiz base data generated successfully!")


# --------------------------------
# Verify Data
# --------------------------------

with engine.connect() as connection:

    role_count = connection.execute(
        text("SELECT COUNT(*) FROM job_roles")
    ).scalar()

    skill_count = connection.execute(
        text("SELECT COUNT(*) FROM skills")
    ).scalar()

    question_count = connection.execute(
        text("SELECT COUNT(*) FROM questions")
    ).scalar()


print("\nDatabase Summary")
print("-------------------------")
print("Roles:", role_count)
print("Skills:", skill_count)
print("Questions:", question_count)