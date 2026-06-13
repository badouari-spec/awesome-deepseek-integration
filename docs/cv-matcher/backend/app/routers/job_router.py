from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.db_models import JobModel
from ..models.schemas import JobCreate, JobResponse
from ..services.ai_service import parse_job

router = APIRouter()


async def _parse_job_background(job_id: str, db: Session):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        return
    try:
        parsed = await parse_job(job.description)
        job.parsed_data = parsed
        job.status = "parsed"
    except Exception as exc:
        job.status = "error"
        job.error_message = str(exc)
    db.commit()


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(
    payload: JobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = JobModel(
        title=payload.title,
        company=payload.company,
        description=payload.description,
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(_parse_job_background, job.id, db)

    return job


@router.get("/", response_model=list[JobResponse])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(JobModel).order_by(JobModel.created_at.desc()).all()


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    db.delete(job)
    db.commit()
