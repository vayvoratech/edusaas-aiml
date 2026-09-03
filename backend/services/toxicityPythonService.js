const axios = require("axios");

const TOXICITY_SERVICE =
    process.env.TOXICITY_SERVICE ||
    "http://127.0.0.1:8004";


async function predictToxicity(data) {

    try {

        const response = await axios.post(
            `${TOXICITY_SERVICE}/toxicity/predict`,
            data,
            {
                timeout: 10000
            }
        );

        return response.data;

    } catch (error) {

        console.error(
            "Toxicity Python Service Error:",
            error.response?.data ||
            error.message
        );

        throw error;
    }
}


module.exports = {
    predictToxicity
};