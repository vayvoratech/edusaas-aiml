from flask import Blueprint, render_template

from config.db_connection import get_connection
from skill_gap_analysis import generate_skill_gap
from recommendation_engine import RecommendationEngine

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard/<int:session_id>")
def dashboard(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # ------------------------------------------
        # Student Details
        # ------------------------------------------
        cursor.execute("""
            SELECT
                u.name,
                dr.domain_name,
                qs.domain_role_id
            FROM education.quiz_sessions qs
            JOIN education.users u
                ON qs.user_id = u.user_id
            JOIN education.domain_roles dr
                ON qs.domain_role_id = dr.domain_role_id
            WHERE qs.session_id = %s
        """, (session_id,))

        student = cursor.fetchone()

        if student is None:
            return "Invalid Session ID", 404

        # ------------------------------------------
        # Skill Results
        # ------------------------------------------
        cursor.execute("""
            SELECT
                sk.skill_name,
                ssr.percentage,
                ssr.skill_level
            FROM education.student_skill_results ssr
            JOIN education.skills sk
                ON ssr.skill_id = sk.skill_id
            WHERE ssr.session_id = %s
            ORDER BY sk.skill_name
        """, (session_id,))

        skill_results = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    # ------------------------------------------
    # Skill Gap Analysis
    # ------------------------------------------
    report = generate_skill_gap(
        session_id,
        student[2]
    )

    # ------------------------------------------
    # Course Recommendations
    # ------------------------------------------
    recommender = RecommendationEngine()
    recommendations = recommender.recommend_courses(session_id)

    # ------------------------------------------
    # Readiness Score
    # ------------------------------------------
    if skill_results:
        readiness = round(
            sum(row[1] for row in skill_results) /
            len(skill_results),
            1
        )
    else:
        readiness = 0

    return render_template(
        "dashboard.html",
        student=student,
        readiness=readiness,
        skill_results=skill_results,
        report=report,
        recommendations=recommendations
    )