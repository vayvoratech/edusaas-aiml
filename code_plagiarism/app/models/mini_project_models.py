from pydantic import BaseModel, Field
from typing import List


class MiniProjectFile(BaseModel):
    path: str
    language: str
    code: str


class MiniProjectSubmission(BaseModel):
    submission_id: str
    files: List[MiniProjectFile] = Field(default_factory=list)


class MiniProjectPlagiarismRequest(BaseModel):
    submission: MiniProjectSubmission
    comparison_submissions: List[MiniProjectSubmission] = Field(
        default_factory=list
    )