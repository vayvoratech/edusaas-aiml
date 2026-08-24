const pool = require("../config/db");

async function saveToxicityPrediction(
    postId,
    predictions
) {
    const query = `
        INSERT INTO education.toxicity_predictions
        (
            id,
            post_id,
            predictions,
            created_at,
            model_version
        )
        VALUES
        (
            gen_random_uuid(),
            $1,
            $2::jsonb,
            CURRENT_TIMESTAMP,
            $3
        )
        RETURNING *;
    `;

    const values = [
        postId,
        JSON.stringify(predictions),
        "1.0.0"
    ];

    const result = await pool.query(
        query,
        values
    );

    return result.rows[0];
}

module.exports = {
    saveToxicityPrediction
};