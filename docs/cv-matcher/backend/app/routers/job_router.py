import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.db_models import JobModel
from ..models.schemas import JobCreate, JobResponse
from ..services.ai_service import parse_job
from ..services.document_parser import extract_text, SUPPORTED_EXTENSIONS
from ..config import UPLOAD_DIR, MAX_FILE_SIZE

router = APIRouter()

os.makedirs(UPLOAD_DIR, exist_ok=True)


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
    """Create a job description from pasted text."""
    if not payload.description.strip():
        raise HTTPException(400, "La description est vide")
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


@router.post("/upload", response_model=JobResponse, status_code=201)
async def upload_job_file(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    company: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Create a job description by uploading a file (PDF, DOCX, TXT, HTML, …)."""
    import pathlib
    ext = pathlib.Path(file.filename or "file").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            400,
            f"Format « {ext} » non supporté. "
            f"Formats acceptés : {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"Fichier trop volumineux (max {MAX_FILE_SIZE // 1024 // 1024} Mo)")

    tmp_path = os.path.join(UPLOAD_DIR, f"jd_{uuid.uuid4()}{ext}")
    try:
        with open(tmp_path, "wb") as f_out:
            f_out.write(content)
        description = await extract_text(tmp_path)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    if not description.strip():
        raise HTTPException(422, "Impossible d'extraire du texte de ce fichier")

    job = JobModel(
        title=title,
        company=company or None,
        description=description,
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
        raise HTTPException(404, "Poste non trouvé")
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(JobModel).filter(JobModel.id == job_id).first()
    if not job:
        raise HTTPException(404, "Poste non trouvé")
    db.delete(job)
    db.commit()
