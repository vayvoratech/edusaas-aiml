const {
    runToxicityPrediction
} = require("../services/toxicityService");


async function predictToxicityController(
    req,
    res,
    next
) {
    try {

        const {
            post_id,
            post_text
        } = req.body;

        if (!post_id || !post_text) {
            return res.status(400).json({
                success: false,
                message:
                    "post_id and post_text are required."
            });
        }

        const result =
            await runToxicityPrediction(
                post_id,
                post_text
            );

        return res.status(200).json(result);

    } catch (error) {

        next(error);
    }
}


module.exports = {
    predictToxicityController
};