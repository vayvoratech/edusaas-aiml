const pool = require("../config/db");

async function getFraudData(userId) {

    const query = `
        SELECT
            u.id AS student_id,

            COALESCE(
                MAX(e.completion_percentage),
                0
            ) AS completion_percentage,

            0 AS watch_time_minutes,

            COALESCE(
                AVG(p.quiz_score),
                0
            ) AS quiz_score,

            COALESCE(
                AVG(cr.rating),
                0
            ) AS rating,

            COALESCE(
                MAX(a.sessions_last_30_days),
                0
            ) AS sessions_last_30_days,

            COALESCE(
                MAX(a.avg_session_minutes),
                0
            ) AS avg_session_minutes,

            COALESCE(
                MAX(a.videos_watched),
                0
            ) AS videos_watched,

            COALESCE(
                MAX(a.assignments_attempted),
                0
            ) AS assignments_attempted,

            COALESCE(
                MAX(a.discussion_interactions),
                0
            ) AS discussion_interactions,

            COALESCE(
                MAX(a.login_count),
                0
            ) AS login_count,

            COALESCE(
                MAX(a.device_count),
                0
            ) AS device_count,

            COALESCE(
                MAX(a.ip_changes),
                0
            ) AS ip_changes,

            COALESCE(
                MAX(a.suspicious_activity_score),
                0
            ) AS suspicious_activity_score

        FROM education.users u

        LEFT JOIN education.enrollments e
            ON e.user_id = u.id

        LEFT JOIN education.progress p
            ON p.user_id = u.id
            AND p.course_id = e.course_id

        LEFT JOIN education.course_ratings cr
            ON cr.user_id = u.id
            AND cr.course_id = e.course_id

        LEFT JOIN education.activity_logs a
            ON a.user_id = u.id

        WHERE u.id = $1

        GROUP BY u.id
    `;

    const result = await pool.query(
        query,
        [userId]
    );

    if (result.rows.length === 0) {
        throw new Error(
            "No fraud data found for this student."
        );
    }

    return result.rows[0];
}

module.exports = {
    getFraudData
};