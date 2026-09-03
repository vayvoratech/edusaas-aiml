const {
    runHiringPrediction
} = require("../services/hiringService");


async function predictHiringController(
    req,
    res
) {

    try {

        const {
            user_id,
            job_id
        } = req.body;


        if (!user_id || !job_id) {

            return res.status(400).json({

                success: false,

                message:
                    "user_id and job_id are required."

            });
        }


        const result =
            await runHiringPrediction(
                user_id,
                job_id
            );


        return res.json(
            result
        );

    } catch (error) {

        console.error(
            "Hiring Controller Error:",
            error
        );


        return res.status(500).json({

            success: false,

            message:
                "Hiring prediction failed.",

            error:
                error.response?.data ||
                error.message

        });
    }
}


module.exports = {
    predictHiringController
};