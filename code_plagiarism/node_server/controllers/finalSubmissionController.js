const db = require("../config/db");

const {
    checkPlagiarism
} = require("../services/plagiarismClient");


async function submitFinalCode(req, res) {

    const client = await db.connect();

    try {

        const {
            user_id,
            domain_role_id,
            assignment_id,
            code
        } = req.body;


        // ==========================================
        // VALIDATION
        // ==========================================

        if (
            !user_id ||
            !domain_role_id ||
            !assignment_id ||
            !code
        ) {
            return res.status(400).json({
                success: false,
                message:
                    "user_id, domain_role_id, assignment_id and code are required"
            });
        }


        // ==========================================
        // START TRANSACTION
        // ==========================================

        await client.query("BEGIN");


        // ==========================================
        // 1. STORE NEW SUBMISSION
        // ==========================================

        const submissionResult =
            await client.query(
                `
                INSERT INTO education.final_submissions
                (
                    user_id,
                    domain_role_id,
                    assignment_id,
                    code
                )
                VALUES ($1, $2, $3, $4)
                RETURNING
                    submission_id,
                    user_id,
                    domain_role_id,
                    assignment_id,
                    submitted_at
                `,
                [
                    user_id,
                    domain_role_id,
                    assignment_id,
                    code
                ]
            );


        const submission =
            submissionResult.rows[0];


        // ==========================================
        // 2. FIND SAME ASSIGNMENT +
        //    SAME DOMAIN ROLE
        // ==========================================

        const comparisonResult =
            await client.query(
                `
                SELECT
                    submission_id,
                    user_id,
                    code
                FROM education.final_submissions
                WHERE domain_role_id = $1
                  AND assignment_id = $2
                  AND user_id <> $3
                  AND submission_id <> $4
                ORDER BY submitted_at ASC
                `,
                [
                    domain_role_id,
                    assignment_id,
                    user_id,
                    submission.submission_id
                ]
            );


        const comparisonSubmissions =
            comparisonResult.rows;


        // ==========================================
        // 3. NO PREVIOUS SUBMISSIONS
        // ==========================================

        if (
            comparisonSubmissions.length === 0
        ) {

            const checkResult =
                await client.query(
                    `
                    INSERT INTO education.plagiarism_checks
                    (
                        submission_id,
                        status,
                        highest_similarity,
                        comparison_count
                    )
                    VALUES ($1, $2, $3, $4)
                    RETURNING *
                    `,
                    [
                        submission.submission_id,
                        "NO_COMPARISON",
                        null,
                        0
                    ]
                );


            await client.query("COMMIT");


            return res.status(201).json({

                success: true,

                submission: submission,

                plagiarism: {
                    status: "NO_COMPARISON",

                    highest_similarity: null,

                    comparison_count: 0,

                    check:
                        checkResult.rows[0]
                }
            });
        }


        // ==========================================
        // 4. BUILD JSON FOR PYTHON
        // ==========================================

        const pythonRequest = {

            submission: {
                submission_id:
                    submission.submission_id,

                code: code
            },

            comparison_submissions:
                comparisonSubmissions.map(
                    item => ({
                        submission_id:
                            item.submission_id,

                        code: item.code
                    })
                )
        };


        // ==========================================
        // 5. CALL PYTHON
        // ==========================================

        const plagiarismResult =
            await checkPlagiarism(
                pythonRequest.submission,
                pythonRequest.comparison_submissions
            );


        const matches =
            plagiarismResult.matches || [];


        // ==========================================
        // 6. FIND HIGHEST SIMILARITY
        // ==========================================

        let highestSimilarity = null;

        if (matches.length > 0) {

            highestSimilarity =
                Math.max(
                    ...matches.map(
                        match =>
                            Number(
                                match.final_similarity
                            )
                    )
                );
        }


        // ==========================================
        // 7. STORE PLAGIARISM CHECK
        // ==========================================

        const checkResult =
            await client.query(
                `
                INSERT INTO education.plagiarism_checks
                (
                    submission_id,
                    status,
                    highest_similarity,
                    comparison_count
                )
                VALUES ($1, $2, $3, $4)
                RETURNING *
                `,
                [
                    submission.submission_id,
                    "CHECKED",
                    highestSimilarity,
                    matches.length
                ]
            );


        const plagiarismCheck =
            checkResult.rows[0];


        // ==========================================
        // 8. STORE EACH MATCH
        // ==========================================

        for (const match of matches) {

            await client.query(
                `
                INSERT INTO education.plagiarism_matches
                (
                    plagiarism_check_id,
                    matched_submission_id,
                    original_token_similarity,
                    normalized_token_similarity,
                    weighted_ast_similarity,
                    final_similarity,
                    risk_level
                )
                VALUES
                (
                    $1,
                    $2,
                    $3,
                    $4,
                    $5,
                    $6,
                    $7
                )
                `,
                [
                    plagiarismCheck.plagiarism_check_id,

                    match.submission_id,

                    match.original_token_similarity,

                    match.normalized_token_similarity,

                    match.weighted_ast_similarity,

                    match.final_similarity,

                    match.risk_level
                ]
            );
        }


        // ==========================================
        // 9. COMMIT
        // ==========================================

        await client.query("COMMIT");


        // ==========================================
        // 10. RESPONSE TO FRONTEND
        // ==========================================

        return res.status(201).json({

            success: true,

            submission: submission,

            plagiarism: {

                status: "CHECKED",

                highest_similarity:
                    highestSimilarity,

                comparison_count:
                    matches.length,

                matches: matches
            }
        });


    } catch (error) {
        await client.query("ROLLBACK");
        console.error("====================================");
        console.error("FINAL SUBMISSION ERROR");
        console.error("====================================");
        console.error("Message:", error.message);
        console.error("Code:", error.code);
        console.error("Detail:", error.detail);
        console.error("Hint:", error.hint);
        console.error("Where:", error.where);
        console.error("Stack:", error.stack);

        console.error("====================================");

        return res.status(500).json({
            success: false,
            message: error.message
        });
    } finally {

        client.release();
    }
}


module.exports = {
    submitFinalCode
};