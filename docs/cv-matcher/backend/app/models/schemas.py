from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class CVResponse(BaseModel):
    id: int
    filename: str
    candidate_name: str
    status: str
    parsed_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    title: str
    company: str = ""
    description: str

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    description: str
    status: str
    parsed_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    class Config:
        from_attributes = True

class MatchRequest(BaseModel):
    job_id: int
    cv_ids: List[int]

class PipelineUpdate(BaseModel):
    pipeline_status: str
    notes: Optional[str] = None

class MatchResponse(BaseModel):
    id: int
    cv_id: int
    job_id: int
    overall_score: float
    skills_score: float
    experience_score: float
    education_score: float
    culture_score: float
    potential_score: float
    communication_score: float
    recommendation: str
    pipeline_status: str
    notes: str
    match_data: Optional[Dict[str, Any]] = None
    status: str
    candidate_name: Optional[str] = None
    job_title: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True
