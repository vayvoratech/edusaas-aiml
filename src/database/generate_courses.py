from sqlalchemy import text

# ---------------------------------------
# Generate Course Prerequisites
# ---------------------------------------

with engine.begin() as connection:

    # Get inserted course ids
    course_ids = connection.execute(
        text(
            """
            SELECT course_id
            FROM courses
            ORDER BY course_id
            """
        )
    ).fetchall()

    # Skip first course (no prerequisite)
    for i in range(1, len(course_ids)):

        connection.execute(
            text(
                """
                INSERT INTO course_prerequisites
                (
                    course_id,
                    prerequisite_course_id
                )
                VALUES
                (
                    :course_id,
                    :prerequisite_course_id
                )
                """
            ),
            {
                "course_id": course_ids[i].course_id,
                "prerequisite_course_id": course_ids[i - 1].course_id
            }
        )

print("✅ Course prerequisites generated successfully!")