const {
    getToxicityData
} = require("./toxicityDataService");

const {
    predictToxicity
} = require("./toxicityPythonService");

const {
    saveToxicityPrediction
} = require("./toxicityPredictionRepository");


async function runToxicityPrediction(
    postId,
    postText
) {
    const postData =
        await getToxicityData(
            postId,
            postText
        );

    const prediction =
        await predictToxicity(
            postData
        );

    const predictionData =
        prediction.data;

    const saved =
        await saveToxicityPrediction(
            postId,
            predictionData.predictions
        );

    return {
        success: true,
        message:
            "Toxicity prediction completed successfully.",
        data: predictionData,
        prediction_id: saved.id
    };
}


module.exports = {
    runToxicityPrediction
};