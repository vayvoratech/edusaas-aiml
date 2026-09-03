from src.toxicity.predict_toxicity import ToxicityPredictor


class ToxicityService:
    """
    Toxicity detection service.

    Responsible for connecting the application/API layer
    with the toxicity prediction pipeline.

    Database persistence is handled by the backend.
    """

    def __init__(
        self,
        model_path="models/toxicity",
        threshold=0.5,
    ):
        self.predictor = ToxicityPredictor(
            model_path=model_path,
            threshold=threshold,
        )

    def predict(
        self,
        student_id: str,
        discussion_id: str,
        post_text: str,
    ):
        """
        Run toxicity prediction for a discussion post.

        student_id and discussion_id are returned as metadata.
        They are NOT passed to the ML model.
        """

        if not post_text or not post_text.strip():
            raise ValueError(
                "post_text cannot be empty."
            )

        result = self.predictor.predict(
            post_text
        )

        return {
            "student_id": student_id,
            "discussion_id": discussion_id,
            "post_text": post_text,

            "is_toxic": result["is_toxic"],

            "toxicity_score": result[
                "toxicity_score"
            ],

            "predictions": result[
                "labels"
            ],

            "threshold": result[
                "threshold"
            ],
        }