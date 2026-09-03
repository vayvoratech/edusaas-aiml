const {
    getHiringData
} = require("./hiringDataService");

const {
    predictHiring
} = require("./hiringPythonService");


async function runHiringPrediction(
    userId,
    jobId
) {

    // ----------------------------------------
    // Get student + job data
    // ----------------------------------------

    const hiringData =
        await getHiringData(
            userId,
            jobId
        );


    // ----------------------------------------
    // Send calculated features
    // to Python model
    // ----------------------------------------

    const prediction =
        await predictHiring(
            hiringData
        );


    // ----------------------------------------
    // Return final response
    // ----------------------------------------

    return {

        success: true,

        message:
            "Hiring prediction completed successfully.",

        data: {

            user_id:
                userId,

            job_id:
                jobId,

            ...hiringData,

            prediction:
                prediction.data

        }

    };
}


module.exports = {
    runHiringPrediction
};