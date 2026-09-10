const axios = require("axios");


const AIML_BASE_URL =
    process.env.AIML_BASE_URL || "http://localhost:8001";


// ============================================================
// MINI PROJECT PLAGIARISM
// ============================================================

async function checkMiniProjectPlagiarism(
    submission,
    comparisonSubmissions
) {
    try {

        const response = await axios.post(
            `${AIML_BASE_URL}/api/plagiarism/mini-project/check`,

            {
                submission,
                comparison_submissions:
                    comparisonSubmissions
            },

            {
                headers: {
                    "Content-Type": "application/json"
                },

                // Mini-projects can contain many files,
                // so allow more time than normal code comparison.
                timeout: 300000
            }
        );

        return response.data;

    } catch (error) {

        console.error(
            "AIML mini-project plagiarism service error:"
        );

        console.error(
            "Status:",
            error.response?.status
        );

        console.error(
            "Response:",
            error.response?.data
        );

        console.error(
            "Message:",
            error.message
        );

        throw new Error(
            "AIML mini-project plagiarism service unavailable"
        );
    }
}


module.exports = {
    checkMiniProjectPlagiarism
};