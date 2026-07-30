from config.db_connection import get_connection


class RecommendationEngine:

    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    # -----------------------------------------------------
    # Get Domain Role from Quiz Session
    # -----------------------------------------------------
    def get_job_role(self, session_id):

        query = """
        SELECT domain_role_id
        FROM education.quiz_sessions
        WHERE session_id = %s
        """

        self.cursor.execute(query, (session_id,))
        result = self.cursor.fetchone()

        if result is None:
            raise Exception("Invalid Session ID")

        return result[0]

    # -----------------------------------------------------
    # Get Required Skills
    # -----------------------------------------------------
    def get_job_required_skills(self, domain_role_id):

        query = """
        SELECT skill_id, required_level
        FROM education.domain_required_skills
        WHERE domain_role_id = %s
        """

        self.cursor.execute(query, (domain_role_id,))
        return self.cursor.fetchall()

    # -----------------------------------------------------
    # Get Student Skill Levels
    # -----------------------------------------------------
    def get_student_skills(self, session_id):

        query = """
        SELECT skill_id, skill_level
        FROM education.student_skill_results
        WHERE session_id = %s
        """

        self.cursor.execute(query, (session_id,))
        return dict(self.cursor.fetchall())

    # -----------------------------------------------------
    # Find Skill Gaps
    # -----------------------------------------------------
    def find_skill_gaps(self, session_id):

        domain_role_id = self.get_job_role(session_id)

        required_skills = self.get_job_required_skills(domain_role_id)
        student_skills = self.get_student_skills(session_id)

        gaps = []

        for skill_id, required_level in required_skills:

            student_level = student_skills.get(skill_id, 0)

            if student_level < required_level:

                gaps.append({
                    "skill_id": skill_id,
                    "gap": required_level - student_level
                })

        return gaps
    
    
    
    def recommend_courses(self, session_id):
        gaps = self.find_skill_gaps(session_id)
        recommended = []
        used_courses = set()
        for gap in gaps:
        
                query = """
                SELECT
                    c.course_id,
                    c.course_name,
                    c.rating,
                    c.difficulty,
                    cs.coverage_level,
                    s.skill_name
                FROM education.course_skills cs
                JOIN education.courses c
                    ON c.course_id = cs.course_id
                JOIN education.skills s
                    ON s.skill_id = cs.skill_id
                WHERE cs.skill_id = %s
                ORDER BY
                    cs.coverage_level DESC,
                    c.rating DESC
                """
        
                self.cursor.execute(query, (gap["skill_id"],))
                rows = self.cursor.fetchall()
        
                selected= None
        
                # Pick the first course that hasn't already been used
                for row in rows:
        
                    if row[0] not in used_courses:
                        selected = row
                        break
        
                if selected is None:
                    continue
        
                used_courses.add(selected[0])
        
                recommended.append({
                    "course_id": selected[0],
                    "course_name": selected[1],
                    "rating": selected[2],
                    "difficulty": selected[3],
                    "coverage": selected[4],
                    "skill": selected[5],
                    "score": gap["gap"] * selected[4] + float(selected[2])
                })
        

        if len(recommended) < 5:
        
                extras = {}
        
                for gap in gaps:
        
                    query = """
                    SELECT
                        c.course_id,
                        c.course_name,
                        c.rating,
                        c.difficulty,
                        cs.coverage_level
                    FROM education.course_skills cs
                    JOIN education.courses c
                        ON c.course_id = cs.course_id
                    WHERE cs.skill_id = %s
                    """
        
                    self.cursor.execute(query, (gap["skill_id"],))
        
                    for row in self.cursor.fetchall():
        
                        if row[0] in used_courses:
                            continue
        
                        score = gap["gap"] * row[4] + float(row[2])
        
                        if row[0] not in extras:
        
                            extras[row[0]] = {
                                "course_id": row[0],
                                "course_name": row[1],
                                "rating": row[2],
                                "difficulty": row[3],
                                "coverage": row[4],
                                "score": 0
                            }
        
                        extras[row[0]]["score"] += score
        
                extras = sorted(
                    extras.values(),
                    key=lambda x: x["score"],
                    reverse=True
                )
        
                for course in extras:
        
                    if len(recommended) == 5:
                        break
                    
                    recommended.append(course)
                    used_courses.add(course["course_id"])

        return recommended
    
    
    
    def display_recommendations(self, session_id):

        recommendations = self.recommend_courses(session_id)

        print("\n")
        print("=" * 70)
        print("              COURSE RECOMMENDATIONS")
        print("=" * 70)

        for i, course in enumerate(recommendations, start=1):

            print(f"\n{i}. {course['course_name']}")
            print(f"   Difficulty : {course['difficulty']}")
            print(f"   Rating     : {course['rating']} ★")
            print(f"   Coverage   : {course['coverage']}/5")
            print(f"   Score      : {round(course['score'], 2)}")

            if "skill" in course:
                print(f"   Recommended For : {course['skill']}")