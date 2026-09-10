const {
    checkMiniProjectPlagiarism
} = require("../services/miniProjectPlagiarismService");


// ============================================================
// POST /api/plagiarism/mini-project/check
// ============================================================

async function checkMiniProjectPlagiarismController(req, res) {

    try {

        const {
            submission,
            comparison_submissions
        } = req.body;


        // ====================================================
        // VALIDATION
        // ====================================================

        if (!submission) {

            return res.status(400).json({
                success: false,
                message: "submission is required"
            });

        }


        if (!submission.submission_id) {

            return res.status(400).json({
                success: false,
                message: "submission.submission_id is required"
            });

        }


        if (!Array.isArray(submission.files)) {

            return res.status(400).json({
                success: false,
                message: "submission.files must be an array"
            });

        }


        if (!Array.isArray(comparison_submissions)) {

            return res.status(400).json({
                success: false,
                message:
                    "comparison_submissions must be an array"
            });

        }


        // ====================================================
        // VALIDATE COMPARISON PROJECTS
        // ====================================================

        for (const comparison of comparison_submissions) {

            if (!comparison.submission_id) {

                return res.status(400).json({
                    success: false,
                    message:
                        "Each comparison submission must have submission_id"
                });

            }


            if (!Array.isArray(comparison.files)) {

                return res.status(400).json({
                    success: false,
                    message:
                        "Each comparison submission must have files array"
                });

            }

        }


        // ====================================================
        // CALL PYTHON AIML SERVICE
        // ====================================================

        const plagiarismResult =
            await checkMiniProjectPlagiarism(
                submission,
                comparison_submissions
            );


        // ====================================================
        // RESPONSE
        // ====================================================

        return res.status(200).json({
            success: true,
            plagiarism: plagiarismResult
        });


    } catch (error) {

        console.error(
            "MINI PROJECT PLAGIARISM ERROR"
        );

        console.error(
            "Message:",
            error.message
        );

        console.error(
            "Stack:",
            error.stack
        );


        return res.status(500).json({
            success: false,
            message: error.message
        });

    }
}


// ============================================================
// HEALTH CHECK
// ============================================================

function miniProjectPlagiarismHealth(req, res) {

    return res.status(200).json({
        success: true,
        service: "Node Mini Project Plagiarism",
        status: "running"
    });

}


module.exports = {
    checkMiniProjectPlagiarismController,
    miniProjectPlagiarismHealth
};