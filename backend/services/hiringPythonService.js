const axios = require("axios");

const PYTHON_HIRING_URL =
    process.env.HIRING_PYTHON_URL ||
    "http://127.0.0.1:8004";


async function predictHiring(studentData) {

    try {

        const response = await axios.post(
            `${PYTHON_HIRING_URL}/hiring/predict`,
            studentData,
            {
                headers: {
                    "Content-Type": "application/json"
                },
                timeout: 30000
            }
        );

        return response.data;

    } catch (error) {

        console.error(
            "Hiring Python Service Error:",
            error.response?.data || error.message
        );

        throw error;
    }
}


module.exports = {
    predictHiring
};