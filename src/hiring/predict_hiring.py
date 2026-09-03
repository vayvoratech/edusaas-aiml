from src.hiring.hiring_service import hiring_service


def predict_hiring(
    student_data: dict
):
    """
    Predict whether a student matches a job.
    """

    return hiring_service.predict(
        student_data
    )


if __name__ == "__main__":

    sample_student = {

        "experience_years": 2.5,

        "required_experience_years": 2.0,

        "skill_match_score": 0.85,

        "experience_match_score": 1.0,

        "domain_match": 1,

        "profile_score": 88

    }

    result = predict_hiring(
        sample_student
    )

    print(
        "\nPredictive Hiring Result\n"
    )

    print(result)