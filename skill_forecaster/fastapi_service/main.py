# main.py (inside skill_forecaster/)
from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi_service.skill_demand_service import SkillDemandService

# Initialize the standalone app and router without prefix
app = FastAPI(title="Skill Demand Prediction Engine")
router = APIRouter(tags=["Skill Demand"])

# Instantiate the service
service = SkillDemandService()

@router.get("/skills")
def get_skills():
    skills = service.get_available_skills()
    if not skills:
        raise HTTPException(status_code=500, detail="Metadata artifact missing or empty.")
    return {"skills": skills}

@router.get("/predict/{skill_name}")
def predict_skill(skill_name: str, periods: int = Query(6, ge=1, le=24)):
    try:
        return service.forecast_skill(skill_name=skill_name, periods=periods)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        # Invalid skill name or missing history
        raise HTTPException(status_code=404, detail=str(e))

# Mount router to local standalone app
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)