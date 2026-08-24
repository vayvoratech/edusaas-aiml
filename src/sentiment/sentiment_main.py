from fastapi import FastAPI

from src.api.sentiment import router as sentiment_router


app = FastAPI(
    title="EduSaaS Sentiment Analysis API",
    description="Sentiment Analysis Model API",
    version="1.0.0"
)


# ---------------------------------------
# Home
# ---------------------------------------

@app.get("/")
def home():

    return {
        "success": True,
        "message": "EduSaaS Sentiment Analysis API Running",
        "data": {
            "service": "sentiment"
        }
    }


# ---------------------------------------
# Health Check
# ---------------------------------------

@app.get("/health")
def health():

    return {
        "success": True,
        "message": "Sentiment Analysis Service Healthy",
        "data": {
            "status": "healthy"
        }
    }


# ---------------------------------------
# Register Sentiment Router
# ---------------------------------------

app.include_router(
    sentiment_router
)