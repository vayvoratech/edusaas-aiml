const pool = require("../config/db");
const pythonService = require("../services/pythonService");

// -----------------------------------------------------
// Start Assessment
// -----------------------------------------------------
exports.startAssessment = async (req, res) => {
    console.log(req.body);

    try {

        const {
            user_id,
            domain_role_id
        } = req.body;

        // ----------------------------------------
        // Validate Request
        // ----------------------------------------
        if (!user_id || !domain_role_id) {

            return res.status(400).json({

                success: false,

                message: "user_id and domain_role_id are required."

            });

        }

        // ----------------------------------------
        // Create Quiz Session
        // ----------------------------------------
        const sessionResult = await pool.query(
            `
            INSERT INTO education.quiz_sessions
            (
                user_id,
                domain_role_id
            )
            VALUES
            (
                $1,
                $2
            )
            RETURNING session_id
            `,
            [
                user_id,
                domain_role_id
            ]
        );

        const session_id = sessionResult.rows[0].session_id;

        // ----------------------------------------
        // Get First Skill
        // ----------------------------------------
        const skillResult = await pool.query(
            `
            SELECT

                s.skill_id,

                s.skill_name

            FROM education.domain_required_skills drs

            JOIN education.skills s

                ON s.skill_id = drs.skill_id

            WHERE drs.domain_role_id = $1

            ORDER BY drs.domain_required_skill_id

            LIMIT 1
            `,
            [
                domain_role_id
            ]
        );

        if (skillResult.rows.length === 0) {

            return res.status(404).json({

                success: false,

                message: "No skills mapped for this domain."

            });

        }

        const skill = skillResult.rows[0];

        // ----------------------------------------
        // Load Questions
        // ----------------------------------------
        const questionsResult = await pool.query(
            `
            SELECT

                question_id,

                question_text,

                option_a,

                option_b,

                option_c,

                option_d,

                correct_option,

                difficulty_id

            FROM education.questions

            WHERE skill_id = $1

            AND is_active = TRUE
            `,
            [
                skill.skill_id
            ]
        );

        // ----------------------------------------
        // Create Python State
        // ----------------------------------------
        const stateResponse =
            await pythonService.createState({

                session_id,

                skill

            });

        const state = stateResponse.state;

        // ----------------------------------------
        // Remove Existing State (Safety)
        // ----------------------------------------
        await pool.query(
            `
            DELETE FROM education.quiz_state

            WHERE

                session_id = $1

            AND

                skill_id = $2
            `,
            [
                session_id,
                skill.skill_id
            ]
        );

        // ----------------------------------------
        // Save Quiz State
        // ----------------------------------------
        await pool.query(
            `
            INSERT INTO education.quiz_state
            (
                session_id,
                skill_id,
                current_difficulty,
                correct_streak,
                wrong_streak,
                questions_answered,
                obtained_score,
                maximum_score,
                asked_questions
            )
            VALUES
            (
                $1,$2,$3,$4,$5,$6,$7,$8,$9
            )
            `,
            [

                session_id,

                skill.skill_id,

                state.current_difficulty,

                state.correct_streak,

                state.wrong_streak,

                state.questions_answered,

                state.obtained_score,

                state.maximum_score,

                state.asked_questions

            ]
        );

        // ----------------------------------------
        // Get First Question
        // ----------------------------------------
        const questionResponse =
            await pythonService.getNextQuestion({

                state,

                questions: questionsResult.rows

            });

        if (!questionResponse.question) {

            return res.status(404).json({

                success: false,

                message: "No questions available."

            });

        }

        // ----------------------------------------
        // Remove Correct Option
        // ----------------------------------------
        const firstQuestion = {

            ...questionResponse.question

        };

        delete firstQuestion.correct_option;

        // ----------------------------------------
        // Response
        // ----------------------------------------
        return res.json({

            success: true,

            session_id,

            question: firstQuestion

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
// -----------------------------------------------------
// Submit Answer
// -----------------------------------------------------
exports.submitAnswer = async (req, res) => {

    try {

        const {

            session_id,

            question_id,

            selected_option

        } = req.body;

        // ----------------------------------------
        // Validate Request
        // ----------------------------------------
        if (
            !session_id ||
            !question_id ||
            !selected_option
        ) {

            return res.status(400).json({

                success: false,

                message:
                    "session_id, question_id and selected_option are required."

            });

        }

        // ----------------------------------------
        // Get Current Question
        // ----------------------------------------
        const questionResult = await pool.query(
            `
            SELECT

                question_id,

                question_text,

                option_a,

                option_b,

                option_c,

                option_d,

                correct_option,

                difficulty_id,

                skill_id

            FROM education.questions

            WHERE question_id = $1
            `,
            [
                question_id
            ]
        );

        if (questionResult.rows.length === 0) {

            return res.status(404).json({

                success: false,

                message: "Question not found."

            });

        }

        const question = questionResult.rows[0];

        // ----------------------------------------
        // Load Quiz State
        // ----------------------------------------
        const stateResult = await pool.query(
            `
            SELECT

                qs.*,

                s.skill_name

            FROM education.quiz_state qs

            JOIN education.skills s

                ON s.skill_id = qs.skill_id

            WHERE

                qs.session_id = $1

            AND

                qs.skill_id = $2
            `,
            [

                session_id,

                question.skill_id

            ]
        );

        if (stateResult.rows.length === 0) {

            return res.status(404).json({

                success: false,

                message: "Quiz state not found."

            });

        }

        const row = stateResult.rows[0];

        const state = {

            session_id: row.session_id,

            skill_id: row.skill_id,

            skill_name: row.skill_name,

            current_difficulty: row.current_difficulty,

            correct_streak: row.correct_streak,

            wrong_streak: row.wrong_streak,

            questions_answered: row.questions_answered,

            obtained_score: row.obtained_score,

            maximum_score: row.maximum_score,

            asked_questions: row.asked_questions || []

        };

        // ----------------------------------------
        // Call Python
        // ----------------------------------------
        const pythonResult =
            await pythonService.submitAnswer({

                state,

                question,

                selected_option

            });

        const result = pythonResult.result;

        const updatedState = result.updated_state;

        // ----------------------------------------
        // Save Updated State
        // ----------------------------------------
        await pool.query(
            `
            UPDATE education.quiz_state

            SET

                current_difficulty = $1,

                correct_streak = $2,

                wrong_streak = $3,

                questions_answered = $4,

                obtained_score = $5,

                maximum_score = $6,

                asked_questions = $7

            WHERE

                session_id = $8

            AND

                skill_id = $9
            `,
            [

                updatedState.current_difficulty,

                updatedState.correct_streak,

                updatedState.wrong_streak,

                updatedState.questions_answered,

                updatedState.obtained_score,

                updatedState.maximum_score,

                updatedState.asked_questions,

                session_id,

                updatedState.skill_id

            ]
        );

                // ----------------------------------------
        // Skill Completed
        // ----------------------------------------
        if (result.skill_completed) {

            // Calculate Skill Score
            const scoreResponse =
                await pythonService.calculateScore({

                    state: updatedState

                });

            const score = scoreResponse.result;

            // Save Skill Result
            await pool.query(
                `
                INSERT INTO education.student_skill_results
                (
                    session_id,
                    skill_id,
                    obtained_score,
                    maximum_score,
                    percentage,
                    skill_level
                )
                VALUES
                (
                    $1,
                    $2,
                    $3,
                    $4,
                    $5,
                    $6
                )
                `,
                [
                    score.session_id,
                    score.skill_id,
                    score.obtained_score,
                    score.maximum_score,
                    score.percentage,
                    score.skill_level
                ]
            );

            // Remove Completed Skill State
            await pool.query(
                `
                DELETE FROM education.quiz_state
                WHERE
                    session_id = $1
                AND
                    skill_id = $2
                `,
                [
                    session_id,
                    updatedState.skill_id
                ]
            );

            // ----------------------------------------
            // Get Next Skill
            // ----------------------------------------
            const nextSkillResult = await pool.query(
                `
                SELECT

                    s.skill_id,

                    s.skill_name

                FROM education.domain_required_skills drs

                JOIN education.skills s

                    ON s.skill_id = drs.skill_id

                WHERE

                    drs.domain_role_id =
                    (
                        SELECT domain_role_id
                        FROM education.quiz_sessions
                        WHERE session_id = $1
                    )

                AND

                    s.skill_id NOT IN
                    (
                        SELECT skill_id
                        FROM education.student_skill_results
                        WHERE session_id = $1
                    )

                ORDER BY drs.domain_required_skill_id

                LIMIT 1
                `,
                [
                    session_id
                ]
            );

            // ----------------------------------------
            // Assessment Completed
            // ----------------------------------------
            if (nextSkillResult.rows.length === 0) {

                await pool.query(
                    `
                    UPDATE education.quiz_sessions
                    SET

                        status='Completed',

                        end_time=CURRENT_TIMESTAMP

                    WHERE session_id=$1
                    `,
                    [
                        session_id
                    ]
                );

                return res.json({

                    success: true,

                    assessment_completed: true,

                    score

                });

            }

            // ----------------------------------------
            // Start Next Skill
            // ----------------------------------------
            const nextSkill = nextSkillResult.rows[0];

            const questionsResult = await pool.query(
                `
                SELECT

                    question_id,

                    question_text,

                    option_a,

                    option_b,

                    option_c,

                    option_d,

                    correct_option,

                    difficulty_id

                FROM education.questions

                WHERE

                    skill_id=$1

                AND

                    is_active=TRUE
                `,
                [
                    nextSkill.skill_id
                ]
            );

            // Create New State
            const newStateResponse =
                await pythonService.createState({

                    session_id,

                    skill: nextSkill

                });

            const newState = newStateResponse.state;

            // Save New State
            await pool.query(
                `
                INSERT INTO education.quiz_state
                (
                    session_id,
                    skill_id,
                    current_difficulty,
                    correct_streak,
                    wrong_streak,
                    questions_answered,
                    obtained_score,
                    maximum_score,
                    asked_questions
                )
                VALUES
                (
                    $1,$2,$3,$4,$5,$6,$7,$8,$9
                )
                `,
                [
                    session_id,
                    nextSkill.skill_id,
                    newState.current_difficulty,
                    newState.correct_streak,
                    newState.wrong_streak,
                    newState.questions_answered,
                    newState.obtained_score,
                    newState.maximum_score,
                    newState.asked_questions
                ]
            );

            // First Question
            const firstQuestionResponse =
                await pythonService.getNextQuestion({

                    state: newState,

                    questions: questionsResult.rows

                });

            const firstQuestion = {
                ...firstQuestionResponse.question
            };

            delete firstQuestion.correct_option;

            return res.json({

                success: true,

                skill_completed: true,

                completed_skill: score,

                next_skill: {

                    skill_id: nextSkill.skill_id,

                    skill_name: nextSkill.skill_name

                },

                question: firstQuestion

            });

        }

        // ----------------------------------------
        // Continue Current Skill
        // ----------------------------------------
        const questionsResult = await pool.query(
            `
            SELECT

                question_id,

                question_text,

                option_a,

                option_b,

                option_c,

                option_d,

                correct_option,

                difficulty_id

            FROM education.questions

            WHERE

                skill_id = $1

            AND

                is_active = TRUE
            `,
            [
                updatedState.skill_id
            ]
        );

        const nextQuestionResponse =
            await pythonService.getNextQuestion({

                state: updatedState,

                questions: questionsResult.rows

            });

        const nextQuestion = {

            ...nextQuestionResponse.question

        };

        delete nextQuestion.correct_option;

        return res.json({

            success: true,

            skill_completed: false,

            is_correct: result.is_correct,

            marks_awarded: result.marks_awarded,

            question: nextQuestion

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
// -----------------------------------------------------
// Finish Assessment
// -------------------------------------------------
// -----------------------------------------------------
// Finish Assessment
// -----------------------------------------------------
exports.finishAssessment = async (req, res) => {

    const client = await pool.connect();

    try {

        const { session_id } = req.body;

        if (!session_id) {

            client.release();

            return res.status(400).json({

                success: false,

                message: "session_id is required."

            });

        }

        await client.query("BEGIN");

        // ----------------------------------------
        // Update Quiz Session
        // ----------------------------------------
        await client.query(
            `
            UPDATE education.quiz_sessions
            SET
                status = 'Completed',
                end_time = CURRENT_TIMESTAMP
            WHERE
                session_id = $1
            `,
            [
                session_id
            ]
        );

        // ----------------------------------------
        // Delete Quiz State
        // ----------------------------------------
        await client.query(
            `
            DELETE
            FROM education.quiz_state
            WHERE session_id = $1
            `,
            [
                session_id
            ]
        );

        await client.query("COMMIT");

        return res.json({

            success: true,

            assessment_completed: true,

            message: "Assessment completed successfully."

        });

    }
    catch (err) {

        await client.query("ROLLBACK");

        console.error(err);

        return res.status(500).json({

            success: false,

            message: err.message

        });

    }
    finally {

        client.release();

    }

};