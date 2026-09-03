from fastapi import FastAPI

from src.api.dropout_api import router as dropout_router


app = FastAPI(
    title="EduSaaS Dropout Prediction API",
    description="Dropout Prediction ML Service",
    version="1.0.0"
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def home():

    return {
        "success": True,
        "message": "EduSaaS Dropout Prediction API Running",
        "data": {
            "service": "dropout"
        }
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "success": True,
        "message": "Dropout Prediction Service Healthy",
        "data": {
            "status": "healthy",
            "models_loaded": True
        }
    }


# ============================================================
# DROPOUT ROUTES
# ============================================================

app.include_router(
    dropout_router
)