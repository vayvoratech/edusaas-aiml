from flask import Blueprint, render_template, request, redirect, url_for
from config.db_connection import get_connection
from adaptive_engine import start_quiz, start_skill

home_bp = Blueprint("home", __name__)


# -------------------------------------------------
# Home Page
# -------------------------------------------------
@home_bp.route("/")
def home():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            domain_role_id,
            domain_name
        FROM education.domain_roles
        ORDER BY domain_name
    """)

    domain_roles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "index.html",
        domain_roles=domain_roles
    )

# -------------------------------------------------
# Start Assessment
# -------------------------------------------------
@home_bp.route("/start", methods=["POST"])
def start():

    name = request.form["full_name"]
    email = request.form["email"]
    domain_role_id = request.form["domain_role_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO education.users
    (
        name,
        email,
        role_id
    )
    VALUES (%s,%s,%s)
    RETURNING user_id
    """, (
    name,
    email,
    domain_role_id
))

    user_id = cursor.fetchone()[0]

    conn.commit()

    cursor.close()
    conn.close()
    session_id = start_quiz(
        user_id,
        domain_role_id
    )

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # Get all required skills for selected job role
        cursor.execute("""
            SELECT
                s.skill_id,
                s.skill_name,
                drs.required_level
            FROM education.domain_required_skills drs
            JOIN education.skills s
                ON s.skill_id = drs.skill_id
            WHERE drs.domain_role_id = %s
            ORDER BY s.skill_name
        """, (domain_role_id,))

        skills = cursor.fetchall()

    finally:

        cursor.close()
        conn.close()

    if len(skills) == 0:
        return "No skills mapped to this domain role."

    # Create quiz_state for every skill
    for skill in skills:

        start_skill(
        session_id,
            skill[0]
        )

    # Redirect to first question
    return redirect(
        url_for(
            "quiz.quiz",
            session_id=session_id
        )
    )