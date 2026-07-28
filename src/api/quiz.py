from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.adaptive_quiz.quiz_service import (
    start_quiz,
    get_question,
    submit_answer,
    get_quiz_results
)

app = FastAPI(
    title="EduAI Adaptive Quiz API",
    description="Adaptive Difficulty Quiz API",
    version="1.0"
)


class StartQuizRequest(BaseModel):
    student_id: int
    role_id: int


class SubmitAnswerRequest(BaseModel):
    attempt_id: int
    question_id: int
    student_answer: str
    response_time_seconds: float


@app.get("/")
def home():
    return {
        "message": "Adaptive Quiz API is running"
    }


@app.post("/quiz/start")
def start_quiz_api(request: StartQuizRequest):

    try:
        return start_quiz(
            student_id=request.student_id,
            role_id=request.role_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@app.get("/quiz/question/{attempt_id}")
def get_quiz_question(attempt_id: int):

    try:
        return get_question(attempt_id)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@app.post("/quiz/answer")
def submit_quiz_answer(
    request: SubmitAnswerRequest
):

    try:
        return submit_answer(
            attempt_id=request.attempt_id,
            question_id=request.question_id,
            student_answer=request.student_answer,
            response_time_seconds=request.response_time_seconds
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    # -----------------------------------------
# Get Quiz Results for Skill Gap Analysis
# -----------------------------------------

@app.get("/quiz/results/{attempt_id}")
def quiz_results(attempt_id: int):

    try:

        return get_quiz_results(
            attempt_id
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )