const pool = require("../config/db");

class RecommendationDataService {

    async getRecommendationData(userId) {

        // 1. Active courses
        const coursesResult = await pool.query(`
            SELECT
                id,
                title,
                description,
                provider,
                category,
                difficulty,
                status,
                educator_id
            FROM education.courses
            WHERE status = 'active'
        `);


        // 2. Course ratings
        const ratingsResult = await pool.query(`
            SELECT
                user_id,
                course_id,
                rating
            FROM education.course_ratings
            WHERE rating IS NOT NULL
        `);


        // 3. User + domain role
        const userResult = await pool.query(`
            SELECT
                u.id,
                u.name,
                u.role_id,
                u.domain_role_id,
                dr.domain_name,
                dr.category AS domain_category
            FROM education.users u
            LEFT JOIN education.domain_roles dr
                ON u.domain_role_id = dr.domain_role_id
            WHERE u.id = $1
        `, [userId]);


        if (userResult.rows.length === 0) {
            throw new Error("User not found.");
        }


        // 4. Course prerequisites
        const prerequisitesResult = await pool.query(`
            SELECT
                course_id,
                prerequisite_course_id
            FROM education.course_prerequisites
        `);


        // 5. Completed courses
        const completedCoursesResult = await pool.query(`
            SELECT
                c.id,
                c.title
            FROM education.enrollments e
            JOIN education.courses c
                ON e.course_id = c.id
            WHERE e.user_id = $1
              AND e.completion_percentage >= 80
            ORDER BY e.enrolled_at
        `, [userId]);


        return {
            courses: coursesResult.rows,
            ratings: ratingsResult.rows,
            user: userResult.rows[0],
            prerequisites: prerequisitesResult.rows,
            completed_courses: completedCoursesResult.rows
        };
    }
}


module.exports = new RecommendationDataService();