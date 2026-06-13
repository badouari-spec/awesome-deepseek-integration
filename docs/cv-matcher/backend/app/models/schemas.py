from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class CVResponse(BaseModel):
    id: str
    filename: str
    candidate_name: Optional[str]
    status: str
    parsed_data: Optional[Any]
    created_at: datetime

    class Config:
        from_attributes = True


class JobCreate(BaseModel):
    title: str
    company: Optional[str] = None
    description: str


class JobResponse(BaseModel):
    id: str
    title: str
    company: Optional[str]
    status: str
    parsed_data: Optional[Any]
    created_at: datetime

    class Config:
        from_attributes = True


class MatchRequest(BaseModel):
    cv_ids: list[str]
    job_id: str


class MatchResponse(BaseModel):
    id: str
    cv_id: str
    job_id: str
    overall_score: Optional[float]
    skills_score: Optional[float]
    experience_score: Optional[float]
    education_score: Optional[float]
    culture_score: Optional[float]
    recommendation: Optional[str]
    match_data: Optional[Any]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
