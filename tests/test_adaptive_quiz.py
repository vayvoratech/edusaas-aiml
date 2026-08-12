from src.adaptive_quiz.quiz_service import start_quiz


def test_start_quiz():

    result = start_quiz(
        student_id=1,
        role_id=1
    )

    assert result is not None

    assert "attempt_id" in result