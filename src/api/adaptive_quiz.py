from fastapi import APIRouter
from pydantic import BaseModel

from src.adaptive_quiz.quiz_service import (
    start_quiz,
    get_question,
    submit_answer,
    get_quiz_results
)

from src.exceptions.custom_exceptions import EduAIException


router = APIRouter(
    prefix="/adaptive-quiz",
    tags=["Adaptive Quiz"]
)


# ---------------------------------------
# Request Schemas
# ---------------------------------------

class StartQuizRequest(BaseModel):
    student_id: int
    role_id: int


class SubmitAnswerRequest(BaseModel):
    attempt_id: int
    question_id: int
    student_answer: str
    response_time_seconds: float


# ---------------------------------------
# Home
# ---------------------------------------

@router.get("/")
def home():

    return {
        "success": True,
        "message": "Adaptive Quiz API is Running",
        "data": None
    }


# ---------------------------------------
# Health
# ---------------------------------------

@router.get("/health")
def health():

    return {
        "success": True,
        "message": "Adaptive Quiz Service Healthy",
        "data": None
    }


# ---------------------------------------
# Start Quiz
# ---------------------------------------

@router.post("/start")
def start_quiz_api(request: StartQuizRequest):

    try:

        result = start_quiz(
            student_id=request.student_id,
            role_id=request.role_id
        )

        return {
            "success": True,
            "message": "Quiz started successfully.",
            "data": result
        }

    except Exception as e:

        raise EduAIException(str(e))


# ---------------------------------------
# Get Next Question
# ---------------------------------------

@router.get("/question/{attempt_id}")
def get_quiz_question(attempt_id: int):

    try:

        result = get_question(attempt_id)

        return {
            "success": True,
            "message": "Question fetched successfully.",
            "data": result
        }

    except Exception as e:

        raise EduAIException(str(e))


# ---------------------------------------
# Submit Answer
# ---------------------------------------

@router.post("/answer")
def submit_quiz_answer(request: SubmitAnswerRequest):

    try:

        result = submit_answer(
            attempt_id=request.attempt_id,
            question_id=request.question_id,
            student_answer=request.student_answer,
            response_time_seconds=request.response_time_seconds
        )

        return {
            "success": True,
            "message": "Answer submitted successfully.",
            "data": result
        }

    except Exception as e:

        raise EduAIException(str(e))


# ---------------------------------------
# Quiz Results
# ---------------------------------------

@router.get("/results/{attempt_id}")
def quiz_results(attempt_id: int):

    try:

        result = get_quiz_results(attempt_id)

        return {
            "success": True,
            "message": "Quiz results fetched successfully.",
            "data": result
        }

    except Exception as e:

        raise EduAIException(str(e))