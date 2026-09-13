from modules.toxicity.predict_toxicity import ToxicityPredictor


class ToxicityService:
    """
    Toxicity detection service connecting API requests to the ML predictor.
    """

    def __init__(self, model_path=None, threshold=0.5):
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
        if not post_text or not post_text.strip():
            raise ValueError("post_text cannot be empty.")

        result = self.predictor.predict(post_text)

        # Resilient mapping for either label key
        predictions_dict = result.get("labels", result.get("predictions", {}))

        return {
            "student_id": student_id,
            "discussion_id": discussion_id,
            "post_text": post_text,
            "is_toxic": result["is_toxic"],
            "toxicity_score": result["toxicity_score"],
            "predictions": predictions_dict,
            "threshold": result["threshold"],
        }