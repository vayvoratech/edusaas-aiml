from config.db_connection import get_connection


def generate_skill_gap(session_id, job_role_id):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        # -------------------------------------------------
        # Fetch required skills for the selected job role
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                s.skill_id,
                s.skill_name,
                jrs.required_level
            FROM job_required_skills jrs
            JOIN skill s
                ON s.skill_id = jrs.skill_id
            WHERE jrs.job_role_id = %s
            ORDER BY s.skill_name
        """, (job_role_id,))

        required_skills = cursor.fetchall()

        required_total = 0
        student_total = 0

        missing_skills = []

        results = []

        print("\n========================================")
        print("        SKILL GAP ANALYSIS")
        print("========================================\n")

        # -------------------------------------------------
        # Compare student level with required level
        # -------------------------------------------------

        for skill_id, skill_name, required_level in required_skills:

            cursor.execute("""
                SELECT skill_level
                FROM student_skill_results
                WHERE session_id = %s
                AND skill_id = %s
            """, (
                session_id,
                skill_id
            ))

            row = cursor.fetchone()

            if row:
                student_level = row[0]
            else:
                student_level = 0

            gap = max(required_level - student_level, 0)

            required_total += required_level
            student_total += min(student_level, required_level)

            if gap == 0:
                status = "Ready"
            else:
                status = "Needs Improvement"
                missing_skills.append(skill_name)

            results.append({
                "skill": skill_name,
                "required": required_level,
                "student": student_level,
                "gap": gap,
                "status": status
            })

        # -------------------------------------------------
        # Calculate Readiness Score
        # -------------------------------------------------

        if required_total == 0:
            readiness = 0
        else:
            readiness = round(
                (student_total / required_total) * 100,
                2
            )

        # -------------------------------------------------
        # Display Report
        # -------------------------------------------------

        for row in results:

            print(
                f"{row['skill']:<25}"
                f" Required:{row['required']} "
                f" Student:{row['student']} "
                f" Gap:{row['gap']} "
                f"{row['status']}"
            )

        print("\n----------------------------------------")
        print(f"Readiness Score : {readiness}%")

        print("\nMissing Skills")

        if missing_skills:

            for skill in missing_skills:
                print("-", skill)

        else:
            print("None")

        return {

            "session_id": session_id,

            "job_role_id": job_role_id,

            "readiness_score": readiness,

            "missing_skills": missing_skills,

            "results": results
        }

    except Exception as e:

        conn.rollback()

        print("Error:", e)

        return None

    finally:

        cursor.close()

        conn.close()