from fastapi import FastAPI

from src.api.recommendation import router as recommendation_router


app = FastAPI(
    title="EduSaaS Recommendation API",
    description="Recommendation Model API",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "success": True,
        "message": "EduSaaS Recommendation API Running",
        "data": {
            "service": "recommendation"
        }
    }


@app.get("/health")
def health():
    return {
        "success": True,
        "message": "Recommendation Service Healthy",
        "data": {
            "status": "healthy"
        }
    }


app.include_router(
    recommendation_router
)