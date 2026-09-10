from fastapi import APIRouter, HTTPException

from app.models.mini_project_models import (
    MiniProjectPlagiarismRequest
)

from app.services.mini_project_service import (
    compare_mini_project
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/plagiarism/mini-project",
    tags=["Mini Project Plagiarism"]
)


# ============================================================
# HEALTH CHECK
# ============================================================

@router.get("/health")
def mini_project_health():
    return {
        "success": True,
        "service": "Mini Project Plagiarism",
        "status": "running"
    }


# ============================================================
# POST /api/plagiarism/mini-project/check
# ============================================================

@router.post("/check")
def check_mini_project_plagiarism(
    request: MiniProjectPlagiarismRequest
):
    try:

        # ----------------------------------------------------
        # Convert Pydantic models to dictionaries
        # ----------------------------------------------------

        submission = request.submission.model_dump()

        comparison_submissions = [
            comparison.model_dump()
            for comparison in request.comparison_submissions
        ]

        # ----------------------------------------------------
        # Run mini-project plagiarism analysis
        # ----------------------------------------------------

        result = compare_mini_project(
            submission,
            comparison_submissions
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        print(
            "Mini project plagiarism service error:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Internal mini-project plagiarism analysis error"
        )