const pool = require("../config/db");


class SentimentDataService {

    async savePrediction(result) {

        const query = `
            INSERT INTO education.sentiment_predictions (
                id,
                post_id,
                prediction,
                confidence,
                negative_score,
                neutral_score,
                positive_score,
                predicted_at,
                model_version
            )
            VALUES (
                gen_random_uuid(),
                $1,
                $2,
                $3,
                $4,
                $5,
                $6,
                CURRENT_TIMESTAMP,
                $7
            )
            RETURNING
                id,
                post_id,
                prediction,
                confidence,
                negative_score,
                neutral_score,
                positive_score,
                predicted_at,
                model_version;
        `;


        const values = [
            result.data.post_id,
            result.data.prediction,
            result.data.confidence,
            result.data.negative_score,
            result.data.neutral_score,
            result.data.positive_score,
            result.data.model_version
        ];


        const response =
            await pool.query(
                query,
                values
            );


        return response.rows[0];
    }
}


module.exports =
    new SentimentDataService();