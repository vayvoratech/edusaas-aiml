const pool = require("../config/db");

async function saveFraudPrediction(
    studentId,
    prediction
) {
    const query = `
        INSERT INTO education.fraud_predictions
        (
            user_id,
            fraud_probability,
            risk_level,
            fraud_prediction,
            anomaly_prediction,
            prediction_time,
            model_version
        )
        VALUES
        ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP, $6)
        RETURNING *;
    `;

    const values = [
        studentId,
        prediction.fraud_probability,
        prediction.risk_level,
        prediction.fraud_prediction === "FRAUD",
        prediction.anomaly_status === "ANOMALY",
        "1.0.0"
    ];

    const result = await pool.query(
        query,
        values
    );

    return result.rows[0];
}

module.exports = {
    saveFraudPrediction
};