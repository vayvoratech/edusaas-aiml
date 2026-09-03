const {
    runFraudPrediction
} = require("../services/fraudService");


async function predictFraud(req, res, next) {

    try {

        const { user_id, student_id } = req.body;

        const userId = user_id || student_id;

        if (!userId) {

            return res.status(400).json({
                success: false,
                message: "user_id is required."
            });
        }

        const result =
            await runFraudPrediction(userId);

        return res.status(200).json(result);

    } catch (error) {

        next(error);
    }
}


module.exports = {
    predictFraud
};