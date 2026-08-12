from fastapi import FastAPI

from src.api.sentiment import router as sentiment_router
from src.api.recommendation import router as recommendation_router
from src.api.dropout_api import router as dropout_router
from src.api.adaptive_quiz import router as adaptive_quiz_router
from src.api.toxicity import router as toxicity_router
from src.api.fraud import router as fraud_router

from src.exceptions.custom_exceptions import EduAIException
from src.exceptions.exception_handler import eduai_exception_handler

from src.middleware.request_logger import RequestLoggerMiddleware

from src.core.config import settings
from src.core.responses import success_response



app = FastAPI(
    title=settings.APP_NAME,
    description="Production AI APIs for EduSaaS",
    version=settings.API_VERSION
)


# ==========================================
# Middleware
# ==========================================

app.add_middleware(
    RequestLoggerMiddleware
)


# ==========================================
# Global Exception Handler
# ==========================================

app.add_exception_handler(
    EduAIException,
    eduai_exception_handler
)


# ==========================================
# Home
# ==========================================

@app.get("/")
def home():

    return success_response(
        message=f"{settings.APP_NAME} is Running",
        data={
            "application": settings.APP_NAME,
            "version": settings.API_VERSION
        }
    )


# ==========================================
# Health Check
# ==========================================

@app.get("/health")
def health():

    return success_response(
        message="Application Healthy",
        data={
            "status": "healthy",
            "application": settings.APP_NAME,
            "version": settings.API_VERSION
        }
    )


# ==========================================
# Register Routers
# ==========================================

app.include_router(sentiment_router)

app.include_router(recommendation_router)

app.include_router(dropout_router)

app.include_router(adaptive_quiz_router)

app.include_router(toxicity_router)

app.include_router(fraud_router)