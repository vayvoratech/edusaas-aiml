const axios = require("axios");
require("dotenv").config();

const BASE_URL = process.env.PYTHON_SERVICE;

class PythonService {

    async createState(payload) {
        const response = await axios.post(
            `${BASE_URL}/create-state`,
            payload
        );
        return response.data;
    }

    async getNextQuestion(payload) {
        const response = await axios.post(
            `${BASE_URL}/next-question`,
            payload
        );
        return response.data;
    }

    async submitAnswer(payload) {

    console.log("Payload sent to Python:");
    console.log(JSON.stringify(payload, null, 2));

    const response = await axios.post(
        `${BASE_URL}/submit-answer`,
        payload
    );

    return response.data;
}

    async calculateScore(payload) {
        const response = await axios.post(
            `${BASE_URL}/calculate-score`,
            payload
        );
        return response.data;
    }

    async getNextSkill(payload) {
        const response = await axios.post(
            `${BASE_URL}/next-skill`,
            payload
        );
        return response.data;
    }

    async finishQuiz(payload) {
        const response = await axios.post(
            `${BASE_URL}/finish`,
            payload
        );
        return response.data;
    }

}

module.exports = new PythonService();