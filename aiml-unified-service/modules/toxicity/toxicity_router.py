from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from modules.toxicity.toxicity_service import ToxicityService

router = APIRouter(
    prefix="/toxicity",
    tags=["Toxicity Detection"]
)

class ToxicityRequest(BaseModel):
    student_id: str = Field(..., description="Student identifier")
    discussion_id: str = Field(..., description="Discussion/post identifier")
    post_text: str = Field(..., min_length=1, description="Discussion post text")

toxicity_service = None

def get_toxicity_service():
    global toxicity_service
    if toxicity_service is None:
        toxicity_service = ToxicityService()
    return toxicity_service

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "toxicity",
    }

@router.post("/predict")
def predict_toxicity(request: ToxicityRequest):
    try:
        service = get_toxicity_service()
        result = service.predict(
            student_id=request.student_id,
            discussion_id=request.discussion_id,
            post_text=request.post_text,
        )
        return {
            "success": True,
            "data": result,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Toxicity prediction failed: {exc}",
        )