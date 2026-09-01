const axios = require("axios");

const PYTHON_PLAGIARISM_URL =
    process.env.PYTHON_PLAGIARISM_URL ||
    "http://localhost:8001/api/plagiarism/check";


async function checkPlagiarism(
    submission,
    comparisonSubmissions
) {
    try {

        const response = await axios.post(
            PYTHON_PLAGIARISM_URL,
            {
                submission,
                comparison_submissions:
                    comparisonSubmissions
            },
            {
                headers: {
                    "Content-Type": "application/json"
                },
                timeout: 60000
            }
        );

        return response.data;

    } catch (error) {

        console.error(
            "Python plagiarism service error:",
            error.response?.data ||
            error.message
        );

        throw new Error(
            "Plagiarism service unavailable"
        );
    }
}


module.exports = {
    checkPlagiarism
};