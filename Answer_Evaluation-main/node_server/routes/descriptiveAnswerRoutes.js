const express = require("express");
const axios = require("axios");

const router = express.Router();

const pool = require("../config/db");

// Flask XLNet service
const XLNET_URL =
    `${process.env.XLNET_SERVICE_URL}/evaluate`;


router.post("/answer", async (req, res) => {

    const {
        descriptive_question_id,
        user_id,
        student_answer
    } = req.body;

    console.log("\n=================================");
    console.log("Descriptive Answer Request");
    console.log("=================================");

    try {

        // -----------------------------------------
        // 1. Validate request
        // -----------------------------------------

        if (!descriptive_question_id) {
            return res.status(400).json({
                success: false,
                error: "descriptive_question_id is required"
            });
        }

        if (!user_id) {
            return res.status(400).json({
                success: false,
                error: "user_id is required"
            });
        }

        if (!student_answer || !student_answer.trim()) {
            return res.status(400).json({
                success: false,
                error: "student_answer is required"
            });
        }


        // -----------------------------------------
        // 2. Get question + reference answer
        // -----------------------------------------

        console.log(
            "Getting descriptive question:",
            descriptive_question_id
        );

        const questionResult = await pool.query(
            `
            SELECT
                descriptive_question_id,
                question_text,
                reference_answer,
                marks
            FROM education.descriptive_questions
            WHERE descriptive_question_id = $1
              AND is_active = TRUE
            `,
            [descriptive_question_id]
        );


        if (questionResult.rows.length === 0) {

            return res.status(404).json({
                success: false,
                error: "Descriptive question not found"
            });

        }


        const question = questionResult.rows[0];


        console.log(
            "Question:",
            question.question_text
        );


        // -----------------------------------------
        // 3. Store student answer
        // -----------------------------------------

        console.log("Storing student answer...");

        const answerResult = await pool.query(
            `
            INSERT INTO education.descriptive_student_answers
            (
                descriptive_question_id,
                user_id,
                student_answer,
                evaluation_status
            )
            VALUES
            (
                $1,
                $2,
                $3,
                'PENDING'
            )
            RETURNING
                descriptive_answer_id,
                descriptive_question_id,
                user_id,
                student_answer,
                evaluation_status,
                answered_at
            `,
            [
                descriptive_question_id,
                user_id,
                student_answer.trim()
            ]
        );


        const answer = answerResult.rows[0];


        console.log(
            "Answer ID:",
            answer.descriptive_answer_id
        );


        // -----------------------------------------
        // 4. Set status = EVALUATING
        // -----------------------------------------

        await pool.query(
            `
            UPDATE education.descriptive_student_answers
            SET evaluation_status = 'EVALUATING'
            WHERE descriptive_answer_id = $1
            `,
            [answer.descriptive_answer_id]
        );


        // -----------------------------------------
        // 5. Send data to Flask
        // -----------------------------------------

        console.log(
            "Sending data to Flask XLNet service..."
        );


        const xlnetResponse = await axios.post(
            XLNET_URL,
            {
                question_text:
                    question.question_text,

                student_answer_text:
                    answer.student_answer,

                reference_answer_text:
                    question.reference_answer
            },
            {
                timeout: 300000
            }
        );


        console.log(
            "Flask response:",
            xlnetResponse.data
        );


        // -----------------------------------------
        // 6. Validate XLNet response
        // -----------------------------------------

        if (
            !xlnetResponse.data ||
            xlnetResponse.data.success !== true
        ) {

            throw new Error(
                xlnetResponse.data?.error ||
                "XLNet evaluation failed"
            );

        }


        const score =
            Number(xlnetResponse.data.score);


        if (Number.isNaN(score)) {

            throw new Error(
                "Invalid score received from XLNet"
            );

        }


        console.log(
            "Received XLNet score:",
            score
        );


        // -----------------------------------------
        // 7. Store score in PostgreSQL
        // -----------------------------------------

        console.log(
            "Saving score to database..."
        );


        const updateResult = await pool.query(
            `
            UPDATE education.descriptive_student_answers
            SET
                score = $1,
                evaluation_status = 'EVALUATED',
                evaluated_at = CURRENT_TIMESTAMP
            WHERE descriptive_answer_id = $2

            RETURNING
                descriptive_answer_id,
                descriptive_question_id,
                user_id,
                student_answer,
                score,
                evaluation_status,
                answered_at,
                evaluated_at
            `,
            [
                score,
                answer.descriptive_answer_id
            ]
        );


        const evaluatedAnswer =
            updateResult.rows[0];


        // -----------------------------------------
        // 8. Send result to frontend
        // -----------------------------------------

        console.log(
            "Evaluation completed successfully"
        );


        return res.status(200).json({

            success: true,

            message:
                "Descriptive answer evaluated successfully",

            result: {

                descriptive_answer_id:
                    evaluatedAnswer.descriptive_answer_id,

                descriptive_question_id:
                    evaluatedAnswer.descriptive_question_id,

                user_id:
                    evaluatedAnswer.user_id,

                score:
                    Number(evaluatedAnswer.score),

                evaluation_status:
                    evaluatedAnswer.evaluation_status,

                answered_at:
                    evaluatedAnswer.answered_at,

                evaluated_at:
                    evaluatedAnswer.evaluated_at
            }

        });

    } catch (error) {

        console.error(
            "\nDescriptive evaluation error:"
        );

        console.error(error);


        // -----------------------------------------
        // 9. Mark answer as FAILED
        // -----------------------------------------

        try {

            if (
                descriptive_question_id &&
                user_id
            ) {

                await pool.query(
                    `
                    UPDATE education.descriptive_student_answers
                    SET evaluation_status = 'FAILED'
                    WHERE descriptive_question_id = $1
                      AND user_id = $2
                      AND evaluation_status = 'EVALUATING'
                    `,
                    [
                        descriptive_question_id,
                        user_id
                    ]
                );

            }

        } catch (dbError) {

            console.error(
                "Failed to update evaluation status:",
                dbError
            );

        }


        return res.status(500).json({

            success: false,

            error:
                "Descriptive answer evaluation failed",

            details:
                error.message

        });

    }

});


module.exports = router;