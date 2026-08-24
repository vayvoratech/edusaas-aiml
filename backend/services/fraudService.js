const {
    getFraudData
} = require("./fraudDataService");

const {
    predictFraud
} = require("./fraudPythonService");

const {
    saveFraudPrediction
} = require("./fraudPredictionRepository");


async function runFraudPrediction(userId) {

    // ----------------------------------------
    // Get data from PostgreSQL
    // ----------------------------------------

    const studentData =
        await getFraudData(userId);


    // ----------------------------------------
    // Send data to Python model
    // ----------------------------------------

    const prediction =
        await predictFraud(studentData);


    // ----------------------------------------
    // Extract prediction data
    // ----------------------------------------

    const predictionData =
        prediction.data;


    // ----------------------------------------
    // Save prediction to PostgreSQL
    // ----------------------------------------

    const savedPrediction =
        await saveFraudPrediction(
            userId,
            predictionData
        );


    // ----------------------------------------
    // Return final response
    // ----------------------------------------

    return {
        success: true,

        message:
            "Fraud prediction completed successfully.",

        data: predictionData,

        prediction_id:
            savedPrediction.id
    };
}


module.exports = {
    runFraudPrediction
};