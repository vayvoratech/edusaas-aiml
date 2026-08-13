const axios = require("axios");
require("dotenv").config();

const RECOMMENDATION_SERVICE =
    process.env.RECOMMENDATION_SERVICE;


class RecommendationPythonService {

    async getRecommendations(payload) {

        try {

            const response = await axios.post(
                `${RECOMMENDATION_SERVICE}/recommendation/recommend`,
                payload,
                {
                    timeout: 10000,
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            );

            return response.data;

        }
        catch (error) {

            // Python API returned an HTTP error
            if (error.response) {

                const serviceError =
                    new Error(
                        error.response.data?.detail ||
                        error.response.data?.message ||
                        "Recommendation service error."
                    );

                serviceError.status =
                    error.response.status;

                throw serviceError;
            }


            // Python service timeout
            if (error.code === "ECONNABORTED") {

                const serviceError =
                    new Error(
                        "Recommendation service request timed out."
                    );

                serviceError.status = 504;

                throw serviceError;
            }


            // Python service unavailable
            if (error.code === "ECONNREFUSED") {

                const serviceError =
                    new Error(
                        "Recommendation service unavailable."
                    );

                serviceError.status = 503;

                throw serviceError;
            }


            throw error;
        }
    }
}


module.exports =
    new RecommendationPythonService();