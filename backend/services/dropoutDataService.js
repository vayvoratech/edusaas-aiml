const pool = require("../config/db");


class DropoutDataService {

    async getDropoutData(studentId) {

        const query = `
            SELECT

                a.user_id AS student_id,

                a.sessions_last_30_days,
                a.avg_session_minutes,
                a.videos_watched,
                a.assignments_attempted,
                a.discussion_interactions,

                COALESCE(l.logins_last_30_days, 0)
                    AS logins_last_30_days,

                COALESCE(l.days_since_last_login, 0)
                    AS days_since_last_login,

                COALESCE(e.completion_percentage, 0)
                    AS completion_percentage,

                COALESCE(p.quiz_score, 0)
                    AS quiz_average,

                CASE
                    WHEN p.assignment_status = 'completed'
                        THEN 100
                    WHEN p.assignment_status = 'in_progress'
                        THEN 50
                    ELSE 0
                END AS assignment_completion_rate

            FROM education.activity_logs a

            LEFT JOIN education.login_history l
                ON a.user_id = l.user_id

            LEFT JOIN education.enrollments e
                ON a.user_id = e.user_id

            LEFT JOIN education.progress p
                ON a.user_id = p.user_id

            WHERE a.user_id = $1

            ORDER BY
                e.enrolled_at DESC NULLS LAST,
                p.created_at DESC NULLS LAST,
                a.created_at DESC

            LIMIT 1
        `;

        const result = await pool.query(
            query,
            [studentId]
        );

        if (result.rows.length === 0) {

            throw new Error(
                "No dropout data found for this student."
            );
        }

        const row = result.rows[0];

        return {

            student_id: row.student_id,

            sessions_last_30_days:
                Number(row.sessions_last_30_days || 0),

            avg_session_minutes:
                Number(row.avg_session_minutes || 0),

            videos_watched:
                Number(row.videos_watched || 0),

            assignments_attempted:
                Number(row.assignments_attempted || 0),

            discussion_interactions:
                Number(row.discussion_interactions || 0),

            logins_last_30_days:
                Number(row.logins_last_30_days || 0),

            days_since_last_login:
                Number(row.days_since_last_login || 0),

            completion_percentage:
                Number(row.completion_percentage || 0),

            quiz_average:
                Number(row.quiz_average || 0),

            assignment_completion_rate:
                Number(row.assignment_completion_rate || 0)
        };
    }
}


module.exports = new DropoutDataService();