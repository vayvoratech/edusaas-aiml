const axios = require("axios");


const DROPOUT_SERVICE =
    process.env.DROPOUT_SERVICE ||
    "http://127.0.0.1:8001";


class DropoutPythonService {

    async predictDropout(data) {

        try {

            const response = await axios.post(
                `${DROPOUT_SERVICE}/dropout/predict`,
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

            if (error.code === "ECONNREFUSED") {

                throw new Error(
                    "Dropout service unavailable."
                );
            }


            if (
                error.code === "ETIMEDOUT" ||
                error.code === "ECONNABORTED"
            ) {

                throw new Error(
                    "Dropout service timed out."
                );
            }


            if (error.response) {

                throw new Error(
                    error.response.data?.detail ||
                    "Dropout prediction failed."
                );
            }


            throw error;
        }
    }
}


module.exports =
    new DropoutPythonService();