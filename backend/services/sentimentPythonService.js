const axios = require("axios");


const SENTIMENT_SERVICE =
    process.env.SENTIMENT_SERVICE ||
    "http://127.0.0.1:8002";


class SentimentPythonService {

    async predictSentiment(data) {

        try {

            const response = await axios.post(
                `${SENTIMENT_SERVICE}/sentiment/predict-sentiment`,
                data,
                {
                    timeout: 10000,
                    headers: {
                        "Content-Type":
                            "application/json"
                    }
                }
            );


            return response.data;

        } catch (error) {

            if (
                error.code === "ECONNREFUSED"
            ) {

                throw new Error(
                    "Sentiment service unavailable."
                );
            }


            if (
                error.code === "ETIMEDOUT" ||
                error.code === "ECONNABORTED"
            ) {

                throw new Error(
                    "Sentiment service timed out."
                );
            }


            if (error.response) {

                throw new Error(
                    error.response.data?.detail ||
                    "Sentiment prediction failed."
                );
            }


            throw error;
        }
    }
}


module.exports =
    new SentimentPythonService();