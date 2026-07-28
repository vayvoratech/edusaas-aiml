from fastapi import FastAPI
from pydantic import BaseModel

from src.dropout.predict_dropout import predict_dropout


app = FastAPI(
    title="EduAI Dropout Prediction API",
    description="API for predicting student dropout risk",
    version="1.0"
)


# --------------------------------
# Input Schema
# --------------------------------

class DropoutInput(BaseModel):

    sessions_last_30_days: int
    avg_session_minutes: float
    videos_watched: int
    assignments_attempted: int
    discussion_interactions: int

    logins_last_30_days: int
    days_since_last_login: int

    completion_percentage: float
    quiz_average: float
    assignment_completion_rate: float


# --------------------------------
# Home Endpoint
# --------------------------------

@app.get("/")
def home():

    return {
        "message": "EduAI Dropout Prediction API is running"
    }


# --------------------------------
# Dropout Prediction Endpoint
# --------------------------------

@app.post("/predict-dropout")
def dropout_prediction(data: DropoutInput):

    result = predict_dropout(data.model_dump())

    return result