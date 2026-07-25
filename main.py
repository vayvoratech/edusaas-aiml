from config.db_connection import get_connection

from adaptive_engine import (
    start_quiz,
    start_skill,
    get_next_question,
    submit_answer,
    update_difficulty,
    calculate_skill_score,
    finish_quiz
)

from skill_gap_analysis import generate_skill_gap


# -------------------------------------------------
# Display Available Courses (Job Roles)
# -------------------------------------------------

def display_job_roles():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT job_role_id, job_role_name
        FROM job_roles
        ORDER BY job_role_name
    """)

    rows = cursor.fetchall()

    print("\n====================================")
    print("       AVAILABLE COURSES")
    print("====================================")

    for row in rows:
        print(f"{row[0]}. {row[1]}")

    cursor.close()
    conn.close()


# -------------------------------------------------
# Fetch Required Skills
# -------------------------------------------------

def get_required_skills(job_role_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            s.skill_id,
            s.skill_name,
            jrs.required_level
        FROM job_required_skills jrs
        JOIN skill s
            ON s.skill_id = jrs.skill_id
        WHERE jrs.job_role_id=%s
        ORDER BY s.skill_name
    """, (job_role_id,))

    skills = cursor.fetchall()

    cursor.close()
    conn.close()

    return skills


# -------------------------------------------------
# Main Program
# -------------------------------------------------

def main():

    student_id = int(input("Enter Student ID : "))

    display_job_roles()

    job_role_id = int(
        input("\nSelect Course ID : ")
    )

    session_id = start_quiz(
        student_id,
        job_role_id
    )

    print("\nQuiz Session Started.")
    print("Session ID :", session_id)

    required_skills = get_required_skills(
        job_role_id
    )

    if not required_skills:
        print("No skills mapped to this course.")
        return

    # --------------------------------------------
    # Adaptive Quiz
    # --------------------------------------------

    for skill_id, skill_name, required_level in required_skills:

        print("\n========================================")
        print("Skill :", skill_name)
        print("Required Level :", required_level)
        print("========================================")

        state = start_skill(
            session_id,
            skill_id
        )

        while state["questions_answered"] < 10:

            question = get_next_question(
                session_id,
                state["skill_id"],
                state["current_difficulty"]
            )

            if question is None:

                print(
                    "No more questions available."
                )

                break

            print("\n------------------------------------")
            print(
                "Difficulty :",
                question["difficulty_id"]
            )
            print("------------------------------------")

            print(question["question_text"])

            print("A.", question["option_a"])
            print("B.", question["option_b"])
            print("C.", question["option_c"])
            print("D.", question["option_d"])

            while True:

                answer = input(
                    "\nEnter Answer (A/B/C/D): "
                ).upper()

                if answer in ["A", "B", "C", "D"]:
                    break

                print("Invalid Option")

            result = submit_answer(

                session_id,

                state["skill_id"],

                question["question_id"],

                answer

            )

            if result["is_correct"]:
                print("✅ Correct")
            else:
                print("❌ Wrong")

            state = update_difficulty(
                state,
                result
            )

        skill_result = calculate_skill_score(
            session_id,
            state
        )

        print("\n----------- Skill Result -----------")

        print(
            "Percentage :",
            skill_result["percentage"]
        )

        print(
            "Skill Level :",
            skill_result["skill_level"]
        )

        print("------------------------------------")

    # --------------------------------------------
    # Finish Quiz
    # --------------------------------------------

    finish_quiz(session_id)

    # --------------------------------------------
    # Skill Gap Analysis
    # --------------------------------------------

    report = generate_skill_gap(
        session_id,
        job_role_id
    )

    print("\n====================================")
    print("ASSESSMENT COMPLETED")
    print("====================================")

    print(
        "Readiness Score :",
        report["readiness_score"],
        "%"
    )

    if report["missing_skills"]:

        print("\nMissing Skills:")

        for skill in report["missing_skills"]:
            print("-", skill)

    else:

        print("\nCongratulations!")
        print("No Skill Gaps Found.")


if __name__ == "__main__":
    main()