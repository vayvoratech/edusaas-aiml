const pool = require("../config/db");
const skillGapPythonService = require("../services/skillGapPythonService");

// -----------------------------------------------------
// Analyze Skill Gap
// -----------------------------------------------------
exports.analyzeSkillGap = async (req, res) => {

    try {

        const { session_id } = req.body;

        if (!session_id) {

            return res.status(400).json({

                success: false,

                message: "session_id is required."

            });

        }

        // ----------------------------------------
        // Get Domain Role
        // ----------------------------------------
        const sessionResult = await pool.query(
            `
            SELECT domain_role_id
            FROM education.quiz_sessions
            WHERE session_id = $1
            `,
            [session_id]
        );

        if (sessionResult.rows.length === 0) {

            return res.status(404).json({

                success: false,

                message: "Quiz session not found."

            });

        }

        const domain_role_id = sessionResult.rows[0].domain_role_id;

        // ----------------------------------------
        // Student Skill Results
        // ----------------------------------------
        const studentSkillsResult = await pool.query(
            `
            SELECT

                ssr.skill_id,

                s.skill_name,

                ssr.skill_level

            FROM education.student_skill_results ssr

            JOIN education.skills s

                ON s.skill_id = ssr.skill_id

            WHERE ssr.session_id = $1

            ORDER BY s.skill_name
            `,
            [session_id]
        );

        // ----------------------------------------
        // Required Skills
        // ----------------------------------------
        const requiredSkillsResult = await pool.query(
            `
            SELECT

                drs.skill_id,

                s.skill_name,

                drs.required_level

            FROM education.domain_required_skills drs

            JOIN education.skills s

                ON s.skill_id = drs.skill_id

            WHERE drs.domain_role_id = $1

            ORDER BY s.skill_name
            `,
            [domain_role_id]
        );

        // ----------------------------------------
        // Call Python
        // ----------------------------------------
        const pythonResponse =
            await skillGapPythonService.analyzeGap({

                student_skills: studentSkillsResult.rows,

                required_skills: requiredSkillsResult.rows

            });

        // ----------------------------------------
        // Return Report
        // ----------------------------------------
        return res.json({

            success: true,

            report: pythonResponse.result

        });

    }
    catch (err) {

        console.error(err);

        return res.status(500).json({

            success: false,

            message: err.message

        });

    }

};