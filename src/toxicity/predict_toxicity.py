from src.toxicity.toxicity_service import toxicity_service


def predict_toxicity(
    student_id: int,
    discussion_id: int,
    post_text: str
):
    """
    Predict toxicity for a discussion post.
    """

    return toxicity_service.predict(

        student_id=student_id,

        discussion_id=discussion_id,

        post_text=post_text

    )


if __name__ == "__main__":

    sample_text = "You are a stupid idiot."

    result = predict_toxicity(

        student_id=101,

        discussion_id=5001,

        post_text=sample_text

    )

    print("\nPrediction Result\n")

    print(result)