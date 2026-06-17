from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class CVModel(Base):
    __tablename__ = "cvs"
    id            = Column(Integer, primary_key=True, index=True)
    filename      = Column(String, nullable=False)
    candidate_name= Column(String, default="")
    raw_text      = Column(Text,   default="")
    parsed_data   = Column(Text,   default="{}")
    status        = Column(String, default="pending")  # pending/parsed/error
    error_message = Column(String, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    matches       = relationship("MatchModel", back_populates="cv", cascade="all, delete-orphan")

class JobModel(Base):
    __tablename__ = "jobs"
    id            = Column(Integer, primary_key=True, index=True)
    title         = Column(String, nullable=False)
    company       = Column(String, default="")
    description   = Column(Text,   default="")
    parsed_data   = Column(Text,   default="{}")
    status        = Column(String, default="pending")
    error_message = Column(String, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    matches       = relationship("MatchModel", back_populates="job", cascade="all, delete-orphan")

class MatchModel(Base):
    __tablename__ = "matches"
    id                    = Column(Integer, primary_key=True, index=True)
    cv_id                 = Column(Integer, ForeignKey("cvs.id"),  nullable=False)
    job_id                = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    overall_score         = Column(Float,  default=0.0)
    skills_score          = Column(Float,  default=0.0)
    experience_score      = Column(Float,  default=0.0)
    education_score       = Column(Float,  default=0.0)
    culture_score         = Column(Float,  default=0.0)
    potential_score       = Column(Float,  default=0.0)
    communication_score   = Column(Float,  default=0.0)
    recommendation        = Column(String, default="")
    match_data            = Column(Text,   default="{}")
    status                = Column(String, default="pending")  # pending/completed/error
    error_message         = Column(String, nullable=True)
    pipeline_status       = Column(String, default="nouveau")  # nouveau/examen/entretien/offre/recrute/rejete
    notes                 = Column(Text,   default="")
    created_at            = Column(DateTime, default=datetime.utcnow)
    updated_at            = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cv                    = relationship("CVModel",  back_populates="matches")
    job                   = relationship("JobModel", back_populates="matches")
