from sqlalchemy import create_engine, text

from src.adaptive_quiz.adaptive_engine import (
    get_next_difficulty,
    QUESTIONS_PER_LEVEL
)

from src.adaptive_quiz.scoring import calculate_score


# -----------------------------------------
# PostgreSQL Configuration
# -----------------------------------------

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


# -----------------------------------------
# 1. Start Quiz
# -----------------------------------------

def start_quiz(student_id, role_id):

    with engine.begin() as connection:

        student = connection.execute(
            text("""
                SELECT student_id
                FROM students
                WHERE student_id = :student_id
            """),
            {"student_id": student_id}
        ).scalar()

        if student is None:
            raise ValueError("Student not found")

        role = connection.execute(
            text("""
                SELECT role_id
                FROM job_roles
                WHERE role_id = :role_id
            """),
            {"role_id": role_id}
        ).scalar()

        if role is None:
            raise ValueError("Job role not found")

        attempt_id = connection.execute(
            text("""
                INSERT INTO quiz_attempts (
                    student_id,
                    role_id,
                    current_difficulty,
                    total_score
                )
                VALUES (
                    :student_id,
                    :role_id,
                    'EASY',
                    0
                )
                RETURNING attempt_id
            """),
            {
                "student_id": student_id,
                "role_id": role_id
            }
        ).scalar_one()

    return {
        "attempt_id": attempt_id,
        "student_id": student_id,
        "role_id": role_id,
        "current_difficulty": "EASY",
        "questions_per_level": QUESTIONS_PER_LEVEL
    }


# -----------------------------------------
# 2. Get Next Question
# -----------------------------------------

def get_question(attempt_id):

    with engine.connect() as connection:

        attempt = connection.execute(
            text("""
                SELECT
                    role_id,
                    current_difficulty,
                    completed_at

                FROM quiz_attempts

                WHERE attempt_id = :attempt_id
            """),
            {"attempt_id": attempt_id}
        ).mappings().first()

        if attempt is None:
            raise ValueError("Quiz attempt not found")

        if attempt["completed_at"] is not None:

            return {
                "message": "Quiz already completed"
            }

        difficulty = attempt["current_difficulty"]

        if difficulty == "COMPLETED":

            return {
                "message": "Quiz completed"
            }

        question = connection.execute(
            text("""
                SELECT
                    q.question_id,
                    q.question_text,
                    q.question_type,
                    q.difficulty,

                    q.option_a,
                    q.option_b,
                    q.option_c,
                    q.option_d,

                    q.weight,

                    s.skill_id,
                    s.skill_name

                FROM questions q

                JOIN skills s
                    ON q.skill_id = s.skill_id

                WHERE q.role_id = :role_id

                AND q.difficulty = :difficulty

                AND q.question_id NOT IN (

                    SELECT question_id

                    FROM quiz_responses

                    WHERE attempt_id = :attempt_id
                )

                ORDER BY RANDOM()

                LIMIT 1
            """),
            {
                "role_id": attempt["role_id"],
                "difficulty": difficulty,
                "attempt_id": attempt_id
            }
        ).mappings().first()

        if question is None:

            return {
                "message":
                    "No more unanswered questions available "
                    "for this difficulty."
            }

        return dict(question)


# -----------------------------------------
# 3. Submit Answer
# -----------------------------------------

def submit_answer(
    attempt_id,
    question_id,
    student_answer,
    response_time_seconds
):

    if response_time_seconds < 0:

        raise ValueError(
            "Response time cannot be negative"
        )

    with engine.begin() as connection:

        # Get attempt
        attempt = connection.execute(
            text("""
                SELECT
                    role_id,
                    current_difficulty,
                    completed_at

                FROM quiz_attempts

                WHERE attempt_id = :attempt_id
            """),
            {"attempt_id": attempt_id}
        ).mappings().first()

        if attempt is None:
            raise ValueError("Quiz attempt not found")

        if attempt["completed_at"] is not None:
            raise ValueError("Quiz already completed")

        current_difficulty = (
            attempt["current_difficulty"]
        )

        # Get question
        question = connection.execute(
            text("""
                SELECT
                    question_id,
                    role_id,
                    correct_answer,
                    difficulty

                FROM questions

                WHERE question_id = :question_id
            """),
            {"question_id": question_id}
        ).mappings().first()

        if question is None:
            raise ValueError("Question not found")

        # Validate question belongs to selected role
        if question["role_id"] != attempt["role_id"]:

            raise ValueError(
                "Question does not belong "
                "to the selected role"
            )

        # Validate difficulty
        if question["difficulty"] != current_difficulty:

            raise ValueError(
                "Question difficulty does not match "
                "the current quiz difficulty"
            )

        # Prevent answering same question twice
        existing = connection.execute(
            text("""
                SELECT response_id

                FROM quiz_responses

                WHERE attempt_id = :attempt_id

                AND question_id = :question_id
            """),
            {
                "attempt_id": attempt_id,
                "question_id": question_id
            }
        ).scalar()

        if existing is not None:

            raise ValueError(
                "This question has already been answered"
            )

        # -----------------------------------------
        # Check Answer
        # -----------------------------------------

        is_correct = (
            student_answer.strip().lower()
            ==
            question["correct_answer"].strip().lower()
        )

        # -----------------------------------------
        # Calculate Score
        # -----------------------------------------

        score = calculate_score(
            current_difficulty,
            is_correct,
            response_time_seconds
        )

        # -----------------------------------------
        # Save Response
        # -----------------------------------------

        connection.execute(
            text("""
                INSERT INTO quiz_responses (

                    attempt_id,
                    question_id,
                    student_answer,
                    is_correct,
                    response_time_seconds,
                    score

                )

                VALUES (

                    :attempt_id,
                    :question_id,
                    :student_answer,
                    :is_correct,
                    :response_time_seconds,
                    :score

                )
            """),
            {
                "attempt_id": attempt_id,
                "question_id": question_id,
                "student_answer": student_answer,
                "is_correct": is_correct,
                "response_time_seconds":
                    response_time_seconds,
                "score": score
            }
        )

        # Add score to total
        connection.execute(
            text("""
                UPDATE quiz_attempts

                SET total_score =
                    total_score + :score

                WHERE attempt_id =
                    :attempt_id
            """),
            {
                "score": score,
                "attempt_id": attempt_id
            }
        )

        # -----------------------------------------
        # Count Questions at Current Level
        # -----------------------------------------

        level_stats = connection.execute(
            text("""
                SELECT

                    COUNT(*) AS total_questions,

                    COUNT(*) FILTER (
                        WHERE qr.is_correct = TRUE
                    ) AS correct_answers

                FROM quiz_responses qr

                JOIN questions q
                    ON qr.question_id =
                       q.question_id

                WHERE qr.attempt_id =
                    :attempt_id

                AND q.difficulty =
                    :difficulty
            """),
            {
                "attempt_id": attempt_id,
                "difficulty":
                    current_difficulty
            }
        ).mappings().first()

        questions_answered = int(
            level_stats["total_questions"]
        )

        correct_answers = int(
            level_stats["correct_answers"]
        )

        next_difficulty = (
            current_difficulty
        )

        level_completed = False
        quiz_completed = False

        # -----------------------------------------
        # Evaluate only after 4 questions
        # -----------------------------------------

        if questions_answered >= QUESTIONS_PER_LEVEL:

            level_completed = True

            next_difficulty = get_next_difficulty(

                current_difficulty,

                correct_answers,

                questions_answered
            )

            # Highest level successfully completed
            if next_difficulty == "COMPLETED":

                quiz_completed = True

                connection.execute(
                    text("""
                        UPDATE quiz_attempts

                        SET
                            current_difficulty =
                                'COMPLETED',

                            completed_at =
                                CURRENT_TIMESTAMP

                        WHERE attempt_id =
                            :attempt_id
                    """),
                    {
                        "attempt_id":
                            attempt_id
                    }
                )

            else:

                connection.execute(
                    text("""
                        UPDATE quiz_attempts

                        SET current_difficulty =
                            :next_difficulty

                        WHERE attempt_id =
                            :attempt_id
                    """),
                    {
                        "next_difficulty":
                            next_difficulty,

                        "attempt_id":
                            attempt_id
                    }
                )

    return {

        "attempt_id":
            attempt_id,

        "question_id":
            question_id,

        "is_correct":
            is_correct,

        "score":
            score,

        "current_level":
            current_difficulty,

        "questions_answered_at_level":
            questions_answered,

        "correct_answers_at_level":
            correct_answers,

        "questions_required":
            QUESTIONS_PER_LEVEL,

        "level_completed":
            level_completed,

        "next_difficulty":
            next_difficulty,

        "quiz_completed":
            quiz_completed
    }

# -----------------------------------------
# 4. Get Quiz Results
# Output for Skill Gap Analysis
# -----------------------------------------

def get_quiz_results(attempt_id):

    difficulty_rank = {
        "EASY": 1,
        "AVERAGE": 2,
        "HARD": 3,
        "DIFFICULT": 4
    }

    with engine.connect() as connection:

        # -----------------------------------------
        # Get Quiz Attempt
        # -----------------------------------------

        attempt = connection.execute(
            text("""
                SELECT
                    student_id,
                    role_id,
                    current_difficulty,
                    total_score,
                    completed_at

                FROM quiz_attempts

                WHERE attempt_id = :attempt_id
            """),
            {
                "attempt_id": attempt_id
            }
        ).mappings().first()

        if attempt is None:
            raise ValueError(
                "Quiz attempt not found"
            )

        student_id = int(
            attempt["student_id"]
        )

        job_role_id = int(
            attempt["role_id"]
        )

        # -----------------------------------------
        # Get ALL skills belonging to this role
        #
        # We derive them from the question bank
        # so skills with no responses are included.
        # -----------------------------------------

        role_skills = connection.execute(
            text("""
                SELECT DISTINCT

                    s.skill_id,
                    s.skill_name

                FROM skills s

                JOIN questions q
                    ON q.skill_id = s.skill_id

                WHERE q.role_id = :role_id

                ORDER BY s.skill_id
            """),
            {
                "role_id": job_role_id
            }
        ).mappings().all()

        results = []

        # -----------------------------------------
        # Calculate result for every role skill
        # -----------------------------------------

        for skill in role_skills:

            skill_id = int(
                skill["skill_id"]
            )

            # Get all responses for this skill
            responses = connection.execute(
                text("""
                    SELECT

                        qr.is_correct,
                        qr.score,
                        q.difficulty

                    FROM quiz_responses qr

                    JOIN questions q
                        ON qr.question_id =
                           q.question_id

                    WHERE qr.attempt_id =
                        :attempt_id

                    AND q.skill_id =
                        :skill_id
                """),
                {
                    "attempt_id":
                        attempt_id,

                    "skill_id":
                        skill_id
                }
            ).mappings().all()

            questions_attempted = len(
                responses
            )

            correct_answers = sum(
                1
                for response in responses
                if response["is_correct"]
            )

            weighted_score = sum(
                float(
                    response["score"] or 0
                )
                for response in responses
            )

            # -----------------------------------------
            # No questions attempted for this skill
            # -----------------------------------------

            if questions_attempted == 0:

                results.append({

                    "skill_id":
                        skill_id,

                    "skill_name":
                        skill["skill_name"],

                    "assessment_status":
                        "NOT_ASSESSED",

                    "questions_attempted":
                        0,

                    "correct_answers":
                        0,

                    "accuracy_percentage":
                        0.0,

                    "weighted_score":
                        0.0,

                    "highest_difficulty":
                        None,

                    "current_level":
                        0
                })

                continue

            # -----------------------------------------
            # Accuracy
            # -----------------------------------------

            accuracy_percentage = round(

                (
                    correct_answers
                    /
                    questions_attempted
                ) * 100,

                2
            )

            # -----------------------------------------
            # Highest difficulty answered correctly
            # -----------------------------------------

            highest_rank = 0
            highest_difficulty = None

            for response in responses:

                if not response[
                    "is_correct"
                ]:
                    continue

                difficulty = response[
                    "difficulty"
                ]

                rank = difficulty_rank.get(
                    difficulty,
                    0
                )

                if rank > highest_rank:

                    highest_rank = rank

                    highest_difficulty = (
                        difficulty
                    )

            # -----------------------------------------
            # Convert performance to
            # current proficiency level 0–5
            # -----------------------------------------

            if highest_rank == 0:

                current_level = 0

            elif highest_rank == 1:

                if accuracy_percentage >= 75:
                    current_level = 2
                else:
                    current_level = 1

            elif highest_rank == 2:

                if accuracy_percentage >= 75:
                    current_level = 3
                else:
                    current_level = 2

            elif highest_rank == 3:

                if accuracy_percentage >= 75:
                    current_level = 4
                else:
                    current_level = 3

            elif highest_rank == 4:

                if accuracy_percentage >= 75:
                    current_level = 5
                else:
                    current_level = 4

            else:

                current_level = 0

            results.append({

                "skill_id":
                    skill_id,

                "skill_name":
                    skill["skill_name"],

                "assessment_status":
                    "ASSESSED",

                "questions_attempted":
                    questions_attempted,

                "correct_answers":
                    correct_answers,

                "accuracy_percentage":
                    accuracy_percentage,

                "weighted_score":
                    round(
                        weighted_score,
                        2
                    ),

                "highest_difficulty":
                    highest_difficulty,

                "current_level":
                    current_level
            })

        # -----------------------------------------
        # Quiz Status
        # -----------------------------------------

        if attempt["completed_at"] is not None:

            quiz_status = "COMPLETED"

        else:

            quiz_status = "IN_PROGRESS"

    # -----------------------------------------
    # Final Skill Gap-ready Output
    # -----------------------------------------

    return {

        "attempt_id":
            attempt_id,

        "student_id":
            student_id,

        "job_role_id":
            job_role_id,

        "quiz_status":
            quiz_status,

        "total_score":
            round(
                float(
                    attempt["total_score"] or 0
                ),
                2
            ),

        "skills":
            results
    }