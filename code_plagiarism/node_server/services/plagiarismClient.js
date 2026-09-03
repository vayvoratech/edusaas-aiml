const axios = require("axios");

const AIML_BASE_URL =
    process.env.AIML_BASE_URL || "http://localhost:8001";

async function checkPlagiarism(
    submission,
    comparisonSubmissions
) {
    try {
        const response = await axios.post(
            `${AIML_BASE_URL}/api/plagiarism/check`,
            {
                submission,
                comparison_submissions: comparisonSubmissions
            },
            {
                headers: {
                    "Content-Type": "application/json"
                },
                timeout: 120000
            }
        );

        return response.data;

    } catch (error) {
        console.error(
            "AIML plagiarism service error:",
            error.response?.data || error.message
        );

        throw new Error(
            "AIML plagiarism service unavailable"
        );
    }
}

module.exports = {
    checkPlagiarism
};