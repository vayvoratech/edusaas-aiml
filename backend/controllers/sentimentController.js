const sentimentPythonService =
    require("../services/sentimentPythonService");

const sentimentDataService =
    require("../services/sentimentDataService");


exports.predictSentiment = async (
    req,
    res
) => {

    try {

        const {
            post_id,
            post_text
        } = req.body;


        // -----------------------------------------
        // Validate input
        // -----------------------------------------

        if (!post_id) {

            return res.status(400).json({
                success: false,
                message: "post_id is required."
            });
        }


        if (!post_text) {

            return res.status(400).json({
                success: false,
                message: "post_text is required."
            });
        }


        // -----------------------------------------
        // Node → Python → Model
        // -----------------------------------------

        const prediction =
            await sentimentPythonService
                .predictSentiment({
                    post_id,
                    post_text
                });


        // -----------------------------------------
        // Save prediction to PostgreSQL
        // -----------------------------------------

        const savedPrediction =
            await sentimentDataService
                .savePrediction(prediction);


        // -----------------------------------------
        // Response
        // -----------------------------------------

        return res.status(200).json({

            success: true,

            message:
                "Sentiment prediction completed successfully.",

            data: savedPrediction

        });


    } catch (error) {

        console.error(
            "Sentiment Prediction Error:",
            error.message
        );


        if (
            error.message.includes(
                "unavailable"
            )
        ) {

            return res.status(503).json({

                success: false,

                message:
                    "Sentiment service unavailable."

            });
        }


        if (
            error.message.includes(
                "timed out"
            )
        ) {

            return res.status(504).json({

                success: false,

                message:
                    "Sentiment service timed out."

            });
        }


        return res.status(500).json({

            success: false,

            message:
                "Failed to generate sentiment prediction.",

            error:
                error.message

        });
    }
};