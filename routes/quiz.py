from flask import Blueprint, render_template, request, jsonify, session

from adaptive_engine import (
    get_next_question,
    submit_answer,
    update_difficulty,
    calculate_skill_score,
    finish_quiz,
    start_skill
)

from config.db_connection import get_connection

quiz_bp = Blueprint("quiz", __name__)


# ----------------------------------------------------
# Start Quiz
# ----------------------------------------------------
@quiz_bp.route("/quiz/<int:session_id>")
def quiz(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT drs.skill_id, s.skill_name
            FROM education.domain_required_skills drs
            JOIN education.skills s
                ON drs.skill_id = s.skill_id
            WHERE drs.domain_role_id = (
                SELECT domain_role_id
                FROM education.quiz_sessions
                WHERE session_id=%s
            )
            ORDER BY drs.skill_id
            LIMIT 1
        """, (session_id,))

        row = cursor.fetchone()

        skill_id = row[0]
        skill_name = row[1]

        session["session_id"] = session_id
        session["skill_id"] = skill_id

        start_skill(session_id, skill_id)

        question = get_next_question(session_id, skill_id)

        return render_template(
            "quiz.html",
            question=question,
            skill_name=skill_name,
            question_number=1
        )

    finally:
        cursor.close()
        conn.close()


# ----------------------------------------------------
# Submit Answer
# ----------------------------------------------------
@quiz_bp.route("/submit_answer", methods=["POST"])
def submit():

    data = request.get_json()

    session_id = session["session_id"]
    skill_id = session["skill_id"]

    result = submit_answer(
        session_id,
        skill_id,
        data["question_id"],
        data["answer"]
    )

    state = start_skill(session_id, skill_id)
    state = update_difficulty(state, result)

    # Skill completed
    if state["questions_answered"] >= 10:

        calculate_skill_score(session_id, skill_id)

    return jsonify({
        "completed": state["questions_answered"] >= 10
    })


# ----------------------------------------------------
# Next Question
# ----------------------------------------------------
@quiz_bp.route("/next_question")
def next_question():

    session_id = session["session_id"]
    skill_id = session["skill_id"]

    conn = get_connection()
    cursor = conn.cursor()

    try:

        state = start_skill(session_id, skill_id)

        # --------------------------------------------------
        # Current skill finished?
        # --------------------------------------------------
        if state["questions_answered"] >= 10:

            cursor.execute("""
                SELECT drs.skill_id, s.skill_name
                FROM education.domain_required_skills drs
                JOIN education.skills s
                    ON drs.skill_id = s.skill_id
                WHERE drs.domain_role_id = (
                    SELECT domain_role_id
                    FROM education.quiz_sessions
                    WHERE session_id=%s
                )
                ORDER BY drs.skill_id
            """,(session_id,))

            skills = cursor.fetchall()

            ids = [row[0] for row in skills]

            current = ids.index(skill_id)

            # -------------------------
            # Last Skill
            # -------------------------
            if current == len(ids)-1:

                finish_quiz(session_id)

                return jsonify({

                    "completed": True,

                    "redirect": f"/dashboard/{session_id}"

                })

            # -------------------------
            # Next Skill
            # -------------------------

            next_skill = skills[current+1]

            session["skill_id"] = next_skill[0]

            state = start_skill(
                session_id,
                next_skill[0]
            )

            question = get_next_question(
                session_id,
                next_skill[0]
            )

            return jsonify({

                "completed": False,

                "new_skill": True,

                "skill_name": next_skill[1],

                "question_number": 1,

                "question_id": question["question_id"],

                "question_text": question["question_text"],

                "option_a": question["option_a"],

                "option_b": question["option_b"],

                "option_c": question["option_c"],

                "option_d": question["option_d"]

            })

        # --------------------------------------------------
        # Same Skill
        # --------------------------------------------------

        question = get_next_question(
            session_id,
            skill_id
        )

        return jsonify({

            "completed": False,

            "new_skill": False,

            "question_number": state["questions_answered"] + 1,

            "question_id": question["question_id"],

            "question_text": question["question_text"],

            "option_a": question["option_a"],

            "option_b": question["option_b"],

            "option_c": question["option_c"],

            "option_d": question["option_d"]

        })

    finally:

        cursor.close()
        conn.close()