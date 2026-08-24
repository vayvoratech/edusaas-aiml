const axios = require("axios");

const FRAUD_SERVICE =
    process.env.FRAUD_SERVICE || "http://127.0.0.1:8003";

async function predictFraud(studentData) {

    try {

        const response = await axios.post(
            `${FRAUD_SERVICE}/fraud/predict`,
            studentData,
            {
                timeout: 10000
            }
        );

        return response.data;

    } catch (error) {

        console.error(
            "Fraud Python Service Error:",
            error.response?.data || error.message
        );

        throw error;
    }
}

module.exports = {
    predictFraud
};