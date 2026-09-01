from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.plagiarism_service import (
    compare_code
)


router = APIRouter(
    prefix="/api/plagiarism",
    tags=["Plagiarism"]
)


# ============================================================
# REQUEST MODELS
# ============================================================

class Submission(BaseModel):

    submission_id: str

    code: str = Field(
        min_length=1
    )


class PlagiarismRequest(BaseModel):

    language: str | None = None

    submission: Submission

    comparison_submissions: list[Submission] = []


# ============================================================
# POST /api/plagiarism/check
# ============================================================

@router.post("/check")
def check_plagiarism(
    request: PlagiarismRequest
):

    try:

        # ----------------------------------------------------
        # No comparison submissions
        # ----------------------------------------------------

        if not request.comparison_submissions:

            return {
                "submission_id":
                    request.submission.submission_id,

                "comparison_count": 0,

                "matches": []
            }

        # ----------------------------------------------------
        # Compare every submission
        # ----------------------------------------------------

        matches = []

        detected_language = request.language

        for comparison in (
            request.comparison_submissions
        ):

            result = compare_code(
                request.submission.code,
                comparison.code,
                detected_language
            )

            # If language was not explicitly provided,
            # compare_code detects it.

            if detected_language is None:

                detected_language = (
                    result["language"]
                )

            matches.append({

                "submission_id":
                    comparison.submission_id,

                "original_token_similarity":
                    result[
                        "original_token_similarity"
                    ],

                "normalized_token_similarity":
                    result[
                        "normalized_token_similarity"
                    ],

                "weighted_ast_similarity":
                    result[
                        "weighted_ast_similarity"
                    ],

                "final_similarity":
                    result[
                        "final_similarity"
                    ],

                "risk_level":
                    result[
                        "risk_level"
                    ]
            })

        # ----------------------------------------------------
        # Highest similarity
        # ----------------------------------------------------

        highest_similarity = max(
            match["final_similarity"]
            for match in matches
        )

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return {

            "submission_id":
                request.submission.submission_id,

            "language":
                detected_language,

            "comparison_count":
                len(matches),

            "matches":
                matches
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        print(
            "Plagiarism service error:",
            repr(error)
        )

        raise HTTPException(
            status_code=500,
            detail="Internal plagiarism analysis error"
        )