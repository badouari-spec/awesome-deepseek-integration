import uuid
from sqlalchemy import Column, String, Text, Float, DateTime, JSON
from sqlalchemy.sql import func
from ..database import Base


def _uuid():
    return str(uuid.uuid4())


class CVModel(Base):
    __tablename__ = "cvs"

    id = Column(String, primary_key=True, default=_uuid)
    filename = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    parsed_data = Column(JSON, nullable=True)
    candidate_name = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending | parsed | error
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=_uuid)
    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    parsed_data = Column(JSON, nullable=True)
    status = Column(String, default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class MatchModel(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, default=_uuid)
    cv_id = Column(String, nullable=False)
    job_id = Column(String, nullable=False)
    overall_score = Column(Float, nullable=True)
    skills_score = Column(Float, nullable=True)
    experience_score = Column(Float, nullable=True)
    education_score = Column(Float, nullable=True)
    culture_score = Column(Float, nullable=True)
    recommendation = Column(String, nullable=True)
    match_data = Column(JSON, nullable=True)
    status = Column(String, default="pending")  # pending | completed | error
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
