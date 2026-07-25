import psycopg2
from config.db_connection import get_connection

def start_quiz(student_id, job_role_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO quiz_sessions(
                student_id,
                job_role_id,
                start_time,
                status,
                total_questions,
                questions_answered
            )
            VALUES(
                %s,
                %s,
                CURRENT_TIMESTAMP,
                'In Progress',
                50,
                0
            )
            RETURNING session_id;
        """, (student_id, job_role_id))

        session_id = cursor.fetchone()[0]

        conn.commit()

        return session_id

    finally:
        cursor.close()
        conn.close()
        
        
def start_skill(session_id, skill_id):

    return {
        "session_id": session_id,
        "skill_id": skill_id,
        "current_difficulty": 1,
        "correct_streak": 0,
        "wrong_streak": 0,
        "questions_answered": 0,
        "obtained_score": 0,
        "maximum_score": 0
    }
       
def get_next_question(session_id, skill_id, difficulty_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT question_id
            FROM student_answers
            WHERE session_id = %s
            AND skill_id = %s
        """, (session_id, skill_id))

        asked_questions = [row[0] for row in cursor.fetchall()]

        params = [skill_id, difficulty_id]

        query = """
            SELECT
                question_id,
                question_text,
                option_a,
                option_b,
                option_c,
                option_d,
                difficulty_id
            FROM questions
            WHERE skill_id = %s
            AND difficulty_id = %s
        """

        if asked_questions:
            placeholders = ",".join(["%s"] * len(asked_questions))
            query += f" AND question_id NOT IN ({placeholders})"
            params.extend(asked_questions)

        query += " ORDER BY RANDOM() LIMIT 1"

        cursor.execute(query, params)

        row = cursor.fetchone()

        # Fallback: any remaining question in this skill
        if row is None:

            params = [skill_id]

            query = """
                SELECT
                    question_id,
                    question_text,
                    option_a,
                    option_b,
                    option_c,
                    option_d,
                    difficulty_id
                FROM questions
                WHERE skill_id = %s
            """

            if asked_questions:
                placeholders = ",".join(["%s"] * len(asked_questions))
                query += f" AND question_id NOT IN ({placeholders})"
                params.extend(asked_questions)

            query += " ORDER BY RANDOM() LIMIT 1"

            cursor.execute(query, params)

            row = cursor.fetchone()

        if row is None:
            return None

        return {
            "question_id": row[0],
            "question_text": row[1],
            "option_a": row[2],
            "option_b": row[3],
            "option_c": row[4],
            "option_d": row[5],
            "difficulty_id": row[6]
        }

    finally:
        cursor.close()
        conn.close()



def submit_answer(session_id, skill_id, question_id, selected_option):
    conn = get_connection()
    cursor = conn.cursor()

    # Get correct answer and difficulty
    cursor.execute("""
        SELECT correct_option, difficulty_id
        FROM questions
        WHERE question_id = %s
    """, (question_id,))

    row = cursor.fetchone()

    if row is None:
        cursor.close()
        conn.close()
        return None

    correct_option = row[0]
    difficulty_id = row[1]

    # Check correctness
    is_correct = (selected_option.upper() == correct_option)

    # Assign marks
    if is_correct:
        if difficulty_id == 1:
            marks_awarded = 1
        elif difficulty_id == 2:
            marks_awarded = 2
        elif difficulty_id == 3:
            marks_awarded = 3
        else:
            marks_awarded = 0
    else:
        marks_awarded = 0

    # Save student's answer
    cursor.execute("""
        INSERT INTO student_answers(
            session_id,
            skill_id,
            question_id,
            difficulty_id,
            selected_option,
            correct_option,
            is_correct,
            marks_awarded
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """,
    (
        session_id,
        skill_id,
        question_id,
        difficulty_id,
        selected_option.upper(),
        correct_option,
        is_correct,
        marks_awarded
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "is_correct": is_correct,
        "marks_awarded": marks_awarded,
        "difficulty_id": difficulty_id
    }
    
    
from config.db_connection import get_connection


def update_difficulty(state, result):
    """
    Update the adaptive assessment state after each answer
    and synchronize quiz progress with the database.
    """

    # -------------------------
    # Update question count
    # -------------------------
    state["questions_answered"] += 1

    # -------------------------
    # Update scores
    # -------------------------
    state["obtained_score"] += result["marks_awarded"]
    state["maximum_score"] += result["difficulty_id"]

    # -------------------------
    # Correct Answer
    # -------------------------
    if result["is_correct"]:

        state["correct_streak"] += 1
        state["wrong_streak"] = 0

        # Easy -> Medium
        if (
            state["current_difficulty"] == 1 and
            state["correct_streak"] >= 2
        ):
            state["current_difficulty"] = 2
            state["correct_streak"] = 0

        # Medium -> Hard
        elif (
            state["current_difficulty"] == 2 and
            state["correct_streak"] >= 2
        ):
            state["current_difficulty"] = 3
            state["correct_streak"] = 0

    # -------------------------
    # Wrong Answer
    # -------------------------
    else:

        state["wrong_streak"] += 1
        state["correct_streak"] = 0

        # Hard -> Medium
        if (
            state["current_difficulty"] == 3 and
            state["wrong_streak"] >= 2
        ):
            state["current_difficulty"] = 2
            state["wrong_streak"] = 0

        # Medium -> Easy
        elif (
            state["current_difficulty"] == 2 and
            state["wrong_streak"] >= 2
        ):
            state["current_difficulty"] = 1
            state["wrong_streak"] = 0

    # -------------------------
    # Update quiz progress in database
    # -------------------------
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        UPDATE quiz_sessions
        SET questions_answered = questions_answered + 1
        WHERE session_id = %s
        """, (state["session_id"],))

        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Error updating quiz progress:", e)

    finally:
        cursor.close()
        conn.close()

    return state



def calculate_skill_score(session_id, state):
    """
    Calculate the final skill score, save it to the database,
    and mark the quiz session as completed.

    Parameters:
        session_id : Quiz session ID
        state      : Skill assessment state

    Returns:
        Dictionary containing the final results.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:

        obtained_score = state["obtained_score"]
        maximum_score = state["maximum_score"]

        # Calculate percentage
        if maximum_score == 0:
            percentage = 0
        else:
            percentage = round(
                (obtained_score / maximum_score) * 100,
                2
            )

        # Determine skill level
        if percentage >= 90:
            skill_level = 5
        elif percentage >= 70:
            skill_level = 4
        elif percentage >= 50:
            skill_level = 3
        elif percentage >= 25:
            skill_level = 2
        else:
            skill_level = 1

        # Save skill result
        cursor.execute("""
            INSERT INTO student_skill_results (
                session_id,
                skill_id,
                obtained_score,
                maximum_score,
                percentage,
                skill_level
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            session_id,
            state["skill_id"],
            obtained_score,
            maximum_score,
            percentage,
            skill_level
        ))


        # Commit both queries
        conn.commit()

        return {
            "session_id": session_id,
            "skill_id": state["skill_id"],
            "questions_answered": state["questions_answered"],
            "obtained_score": obtained_score,
            "maximum_score": maximum_score,
            "percentage": percentage,
            "skill_level": skill_level,
            "status": "Completed"
        }

    except Exception as e:
        conn.rollback()
        print("Error calculating skill score:", e)
        return None

    finally:
        cursor.close()
        conn.close()


def finish_quiz(session_id):
    """
    Complete the entire adaptive quiz after all skills.
    """

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            UPDATE quiz_sessions
            SET
                status='Completed',
                end_time=CURRENT_TIMESTAMP
            WHERE session_id=%s
        """,(session_id,))

        conn.commit()

        print("Quiz Completed Successfully.")

    except Exception as e:

        conn.rollback()
        print(e)

    finally:

        cursor.close()
        conn.close()