const { runCode } = require("../services/dockerService");
const pool = require("../config/db");

// Standardize output text across OS platforms
function normalizeOutput(str) {
    return String(str || "").replace(/\r\n/g, "\n").trim();
}

/// =========================================================
// Run Student Code against Sample Test Cases
// =========================================================
async function runStudentCode(req, res) {
    try {
        const { questionId, language, code, customInput } = req.body;

        if (!language || !code) {
            return res.status(400).json({
                status: "error",
                message: "language and code are required fields"
            });
        }

        // Standardize output helper for comparison
        const normalizeOutput = (str) => (str || "").replace(/\r\n/g, "\n").trim();

        // ---------------------------------------------------------
        // CASE 1: questionId provided -> Run against Sample Test Cases
        // ---------------------------------------------------------
        if (questionId) {
            // Fetch sample test cases for the question from DB
            const testCaseResult = await pool.query(
                `SELECT test_case_id, input_data, expected_output 
                 FROM education.coding_test_cases 
                 WHERE question_id = $1 AND is_hidden = false
                 ORDER BY test_case_id ASC`,
                [questionId]
            );

            if (testCaseResult.rows.length === 0) {
                return res.status(404).json({
                    status: "error",
                    message: `No sample test cases found for questionId: ${questionId}`
                });
            }

            const sampleTestCases = testCaseResult.rows;
            const testResults = [];
            let passedCount = 0;

            for (const tc of sampleTestCases) {
                const execution = await runCode(language, code, tc.input_data);

                let testStatus = "FAILED";
                const cleanActualOutput = normalizeOutput(execution.stdout);
                const cleanExpectedOutput = normalizeOutput(tc.expected_output);

                if (execution.status === "success") {
                    if (cleanActualOutput === cleanExpectedOutput) {
                        testStatus = "PASSED";
                        passedCount++;
                    } else {
                        testStatus = "FAILED";
                    }
                } else {
                    testStatus = execution.status.toUpperCase(); // 'TIMEOUT' or 'RUNTIME_ERROR'
                }

                testResults.push({
                    testCaseId: tc.test_case_id,
                    inputData: tc.input_data,
                    expectedOutput: tc.expected_output,
                    actualOutput: execution.stdout,
                    stderr: execution.stderr,
                    status: testStatus,
                    executionTimeMs: execution.executionTime
                });
            }

            const totalCount = sampleTestCases.length;

            return res.status(200).json({
                status: "success",
                questionId: parseInt(questionId, 10),
                summary: {
                    totalTestCases: totalCount,
                    passedCount: passedCount,
                    failedCount: totalCount - passedCount,
                    allPassed: passedCount === totalCount
                },
                sampleTestCases: testResults
            });
        }

        // ---------------------------------------------------------
        // CASE 2: No questionId -> Custom execution mode
        // ---------------------------------------------------------
        const execution = await runCode(language, code, customInput || "");
        return res.status(200).json({
            status: "success",
            execution: {
                status: execution.status,
                stdout: execution.stdout,
                stderr: execution.stderr,
                exitCode: execution.exitCode,
                executionTimeMs: execution.executionTime
            }
        });

    } catch (error) {
        console.error("Run code error:", error);
        return res.status(500).json({
            status: "error",
            message: error.message || "An error occurred during execution"
        });
    }
}

// =========================================================
// 2. Start Coding Session & Load/Assign Unseen Questions
// =========================================================
async function startAssessment(req, res) {
    const client = await pool.connect();

    try {
        const { userId, sessionId } = req.body;

        if (!userId || !sessionId) {
            return res.status(400).json({
                status: "error",
                message: "userId (UUID) and sessionId (INTEGER) are required"
            });
        }

        await client.query("BEGIN");

        // 1. Ensure user session entry exists in user_coding_sessions
        let sessionResult = await client.query(
            `SELECT session_id, user_id, total_score, max_score, questions_completed, status
             FROM education.user_coding_sessions
             WHERE session_id = $1 AND user_id = $2`,
            [sessionId, userId]
        );

        if (sessionResult.rows.length === 0) {
            sessionResult = await client.query(
                `INSERT INTO education.user_coding_sessions (session_id, user_id)
                 VALUES ($1, $2)
                 RETURNING session_id, user_id, total_score, max_score, questions_completed, status`,
                [sessionId, userId]
            );
        }

        const session = sessionResult.rows[0];

        // 2. Check if user already has questions assigned/asked in student_asked_questions
        let questionsResult = await client.query(
            `SELECT q.question_id, q.title, q.description, q.input_format, 
                    q.output_format, q.constraints_text, q.supported_languages, 
                    q.default_time_limit_ms, q.default_memory_limit_mb, q.total_marks
             FROM education.student_asked_questions saq
             INNER JOIN education.coding_questions q ON q.question_id = saq.question_id
             WHERE saq.user_id = $1
             ORDER BY saq.asked_at DESC
             LIMIT 3`,
            [userId]
        );

        // 3. Assign 3 unseen questions if none assigned yet
        if (questionsResult.rows.length < 3) {
            const unseenQuestions = await client.query(
                `SELECT question_id FROM education.coding_questions
                 WHERE question_id NOT IN (
                     SELECT question_id FROM education.student_asked_questions WHERE user_id = $1
                 )
                 ORDER BY RANDOM()
                 LIMIT $2`,
                [userId, 3 - questionsResult.rows.length]
            );

            if (unseenQuestions.rows.length > 0) {
                for (const row of unseenQuestions.rows) {
                    await client.query(
                        `INSERT INTO education.student_asked_questions (user_id, question_id)
                         VALUES ($1, $2)
                         ON CONFLICT DO NOTHING`,
                        [userId, row.question_id]
                    );
                }

                // Re-fetch questions after insertion
                questionsResult = await client.query(
                    `SELECT q.question_id, q.title, q.description, q.input_format, 
                            q.output_format, q.constraints_text, q.supported_languages, 
                            q.default_time_limit_ms, q.default_memory_limit_mb, q.total_marks
                     FROM education.student_asked_questions saq
                     INNER JOIN education.coding_questions q ON q.question_id = saq.question_id
                     WHERE saq.user_id = $1
                     ORDER BY saq.asked_at DESC
                     LIMIT 3`,
                    [userId]
                );
            }
        }

        await client.query("COMMIT");

        const questions = questionsResult.rows;

        // 4. Attach Sample Test Cases (is_hidden = FALSE)
        if (questions.length > 0) {
            const questionIds = questions.map(q => q.question_id);
            const sampleTestCases = await client.query(
                `SELECT test_case_id, question_id, input_data, expected_output
                 FROM education.coding_test_cases
                 WHERE question_id = ANY($1) AND is_hidden = FALSE
                 ORDER BY test_case_id ASC`,
                [questionIds]
            );

            const sampleMap = {};
            sampleTestCases.rows.forEach(tc => {
                if (!sampleMap[tc.question_id]) sampleMap[tc.question_id] = [];
                sampleMap[tc.question_id].push({
                    testCaseId: tc.test_case_id,
                    inputData: tc.input_data,
                    expectedOutput: tc.expected_output
                });
            });

            questions.forEach(q => {
                q.sample_test_cases = sampleMap[q.question_id] || [];
            });
        }

        return res.status(200).json({
            status: "success",
            session: {
                sessionId: session.session_id,
                totalScore: Number(session.total_score),
                maxScore: Number(session.max_score),
                questionsCompleted: session.questions_completed,
                status: session.status
            },
            questions: questions.map((q, idx) => ({
                order: idx + 1,
                questionId: q.question_id,
                title: q.title,
                description: q.description,
                inputFormat: q.input_format,
                outputFormat: q.output_format,
                constraints: q.constraints_text,
                supportedLanguages: q.supported_languages,
                timeLimitMs: q.default_time_limit_ms,
                memoryLimitMb: q.default_memory_limit_mb,
                totalMarks: q.total_marks,
                sampleTestCases: q.sample_test_cases
            }))
        });

    } catch (error) {
        await client.query("ROLLBACK");
        console.error("Start assessment error:", error);
        return res.status(500).json({
            status: "error",
            message: "Failed to load session questions",
            details: error.message
        });
    } finally {
        client.release();
    }
}

// =========================================================
// 3. Submit Code & Evaluate Test Cases
// =========================================================
async function submitCode(req, res) {
    const client = await pool.connect();

    try {
        const { userId, sessionId, questionId, language, code } = req.body;

        if (!userId || !sessionId || !questionId) {
            return res.status(400).json({ 
                status: "error", 
                message: "userId, sessionId, and questionId are required" 
            });
        }

        if (!language || typeof language !== "string" || !code || typeof code !== "string" || !code.trim()) {
            return res.status(400).json({ 
                status: "error", 
                message: "Language and non-empty code are required" 
            });
        }

        const normalizedLang = language.trim().toLowerCase();

        // 1. Fetch Question Details
        const questionResult = await client.query(
            `SELECT question_id, title, default_time_limit_ms, default_memory_limit_mb, total_marks
             FROM education.coding_questions
             WHERE question_id = $1`,
            [questionId]
        );

        if (questionResult.rows.length === 0) {
            return res.status(404).json({ status: "error", message: "Question not found" });
        }

        const question = questionResult.rows[0];

        // 2. Fetch Test Cases
        const testCaseResult = await client.query(
            `SELECT test_case_id, input_data, expected_output, is_hidden, weight, time_limit_ms
             FROM education.coding_test_cases
             WHERE question_id = $1
             ORDER BY is_hidden ASC, test_case_id ASC`,
            [questionId]
        );

        const testCases = testCaseResult.rows;
        if (testCases.length === 0) {
            return res.status(400).json({ 
                status: "error", 
                message: "No test cases configured for this question" 
            });
        }

        // 3. Insert Initial Submission Record
        const submissionResult = await client.query(
            `INSERT INTO education.coding_submissions
             (user_id, session_id, question_id, language, source_code, status, total_marks, total_test_cases)
             VALUES ($1, $2, $3, $4, $5, 'Running', $6, $7)
             RETURNING submission_id`,
            [userId, sessionId, questionId, normalizedLang, code, question.total_marks || 100, testCases.length]
        );

        const submissionId = submissionResult.rows[0].submission_id;

        // Release DB connection while Docker executes code
        client.release();

        // 4. Parallel Test Execution
        const evaluationPromises = testCases.map(async (tc) => {
            let execResult;
            try {
                execResult = await runCode(normalizedLang, code, tc.input_data);
            } catch (err) {
                execResult = { status: "error", stdout: "", stderr: err.message, executionTime: 0 };
            }

            const actualOutput = normalizeOutput(execResult.stdout);
            const expectedOutput = normalizeOutput(tc.expected_output);
            const execTime = Number(execResult.executionTime || 0);
            const testWeight = Number(tc.weight || 1);

            let testStatus = "Failed";
            let errorMessage = null;

            if (execResult.status === "timeout") {
                testStatus = "Time Limit Exceeded";
                errorMessage = "Execution time limit exceeded";
            } else if (execResult.status === "runtime_error") {
                testStatus = "Runtime Error";
                errorMessage = execResult.stderr || "Runtime error";
            } else if (execResult.status === "error") {
                testStatus = "Execution Error";
                errorMessage = execResult.stderr || "Execution error";
            } else if (actualOutput === expectedOutput) {
                testStatus = "Passed";
            } else {
                testStatus = "Wrong Answer";
                errorMessage = "Output does not match expected output";
            }

            return {
                testCaseId: tc.test_case_id,
                isHidden: tc.is_hidden,
                inputData: tc.input_data,
                expectedOutput,
                actualOutput,
                testStatus,
                errorMessage,
                execTime,
                weight: testWeight
            };
        });

        const evaluatedResults = await Promise.all(evaluationPromises);

        // 5. Calculate Final Metrics
        let passedTestCases = 0;
        let totalWeight = 0;
        let passedWeight = 0;
        let maxExecutionTime = 0;
        let firstError = null;
        let primaryFailureStatus = null;

        const testCaseDetails = [];
        const dbInsertValues = [];

        evaluatedResults.forEach((res, idx) => {
            totalWeight += res.weight;
            if (res.execTime > maxExecutionTime) maxExecutionTime = res.execTime;

            if (res.testStatus === "Passed") {
                passedTestCases++;
                passedWeight += res.weight;
            } else {
                if (!firstError && res.errorMessage) firstError = res.errorMessage;
                if (!primaryFailureStatus) primaryFailureStatus = res.testStatus;
            }

            dbInsertValues.push([
                submissionId,
                res.testCaseId,
                res.testStatus,
                res.actualOutput,
                res.expectedOutput,
                res.execTime,
                res.errorMessage
            ]);

            testCaseDetails.push({
                testCaseNumber: idx + 1,
                testCaseId: res.testCaseId,
                status: res.testStatus,
                isHidden: res.isHidden,
                input: res.isHidden ? "[Hidden]" : res.inputData,
                expectedOutput: res.isHidden ? "[Hidden]" : res.expectedOutput,
                actualOutput: res.isHidden ? (res.testStatus === "Passed" ? "[Matched]" : "[Output Hidden]") : res.actualOutput,
                executionTimeMs: res.execTime,
                errorMessage: res.isHidden && res.testStatus !== "Passed" ? "Test case failed" : res.errorMessage
            });
        });

        let finalStatus = "Accepted";
        if (passedTestCases === 0) {
            finalStatus = primaryFailureStatus || "Wrong Answer";
        } else if (passedTestCases < testCases.length) {
            finalStatus = "Partially Accepted";
        }

        const scorePercentage = totalWeight > 0 ? (passedWeight / totalWeight) : 0;
        const finalScore = Number((scorePercentage * Number(question.total_marks || 100)).toFixed(2));

        // 6. Save Test Results and Update Submission in Database
        const dbClient = await pool.connect();
        try {
            await dbClient.query("BEGIN");

            // Bulk Insert Test Results
            const valuePlaceholders = dbInsertValues.map((_, idx) => 
                `($${idx * 7 + 1}, $${idx * 7 + 2}, $${idx * 7 + 3}, $${idx * 7 + 4}, $${idx * 7 + 5}, $${idx * 7 + 6}, $${idx * 7 + 7})`
            ).join(", ");

            await dbClient.query(
                `INSERT INTO education.submission_test_results
                 (submission_id, test_case_id, status, actual_output, expected_output, execution_time_ms, error_message)
                 VALUES ${valuePlaceholders}`,
                dbInsertValues.flat()
            );

            // Update Master Submission Status & Score
            await dbClient.query(
                `UPDATE education.coding_submissions
                 SET status = $1, score = $2, passed_test_cases = $3, execution_time_ms = $4
                 WHERE submission_id = $5`,
                [finalStatus, finalScore, passedTestCases, maxExecutionTime, submissionId]
            );

            // Update User Coding Session Aggregate Score
            await dbClient.query(
                `UPDATE education.user_coding_sessions
                 SET total_score = (
                     SELECT COALESCE(SUM(max_score_per_question), 0)
                     FROM (
                         SELECT MAX(score) as max_score_per_question
                         FROM education.coding_submissions
                         WHERE session_id = $1
                         GROUP BY question_id
                     ) subquery
                 )
                 WHERE session_id = $1`,
                [sessionId]
            );

            await dbClient.query("COMMIT");
        } catch (dbErr) {
            await dbClient.query("ROLLBACK");
            throw dbErr;
        } finally {
            dbClient.release();
        }

        return res.status(200).json({
            status: "success",
            submissionId,
            sessionId,
            questionId,
            result: {
                status: finalStatus,
                score: finalScore,
                totalMarks: Number(question.total_marks || 100),
                passSummary: `${passedTestCases}/${testCases.length} Passed`,
                passedTestCases,
                totalTestCases: testCases.length,
                executionTimeMs: maxExecutionTime,
                errorDetails: firstError,
                testResults: testCaseDetails
            }
        });

    } catch (error) {
        console.error("Submission error:", error);
        return res.status(500).json({
            status: "error",
            message: "Code submission failed",
            details: error.message
        });
    }
}

// =========================================================
// 4. Complete Assessment Session
// =========================================================
async function completeAssessment(req, res) {
    const client = await pool.connect();

    try {
        const { userId, sessionId } = req.body;

        if (!userId || !sessionId) {
            return res.status(400).json({
                status: "error",
                message: "userId (UUID) and sessionId (INTEGER) are required"
            });
        }

        await client.query("BEGIN");

        // 1. Calculate highest score per question and total completed count
        const statsResult = await client.query(
            `SELECT 
                COUNT(DISTINCT question_id) as completed_count,
                COALESCE(SUM(max_score_per_q), 0) as aggregate_score
             FROM (
                SELECT question_id, MAX(score) as max_score_per_q
                FROM education.coding_submissions
                WHERE session_id = $1 AND user_id = $2
                GROUP BY question_id
             ) sub`,
            [sessionId, userId]
        );

        const completedCount = parseInt(statsResult.rows[0].completed_count, 10) || 0;
        const aggregateScore = Number(statsResult.rows[0].aggregate_score) || 0;

        // 2. Update session status to 'Completed'
        const updateResult = await client.query(
            `UPDATE education.user_coding_sessions
             SET status = 'Completed',
                 total_score = $1,
                 questions_completed = $2
             WHERE session_id = $3 AND user_id = $4
             RETURNING session_id, user_id, total_score, max_score, questions_completed, status`,
            [aggregateScore, completedCount, sessionId, userId]
        );

        if (updateResult.rows.length === 0) {
            await client.query("ROLLBACK");
            return res.status(404).json({
                status: "error",
                message: "Session not found for the specified user"
            });
        }

        await client.query("COMMIT");

        const session = updateResult.rows[0];

        return res.status(200).json({
            status: "success",
            message: "Assessment completed successfully",
            session: {
                sessionId: session.session_id,
                userId: session.user_id,
                totalScore: Number(session.total_score),
                maxScore: Number(session.max_score),
                questionsCompleted: session.questions_completed,
                status: session.status
            }
        });

    } catch (error) {
        await client.query("ROLLBACK");
        console.error("Complete assessment error:", error);
        return res.status(500).json({
            status: "error",
            message: "Failed to complete assessment",
            details: error.message
        });
    } finally {
        client.release();
    }
}

module.exports = {
    runStudentCode,
    startAssessment,
    submitCode,
    completeAssessment
};



