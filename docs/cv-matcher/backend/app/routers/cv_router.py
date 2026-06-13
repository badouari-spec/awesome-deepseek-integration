import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.db_models import CVModel
from ..models.schemas import CVResponse
from ..services.document_parser import extract_text
from ..services.ai_service import parse_cv
from ..config import UPLOAD_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS

router = APIRouter()

os.makedirs(UPLOAD_DIR, exist_ok=True)


async def _parse_cv_background(cv_id: str, file_path: str, db: Session):
    cv = db.query(CVModel).filter(CVModel.id == cv_id).first()
    if not cv:
        return
    try:
        raw_text = await extract_text(file_path)
        cv.raw_text = raw_text
        parsed = await parse_cv(raw_text)
        cv.parsed_data = parsed
        cv.candidate_name = parsed.get("name", "Unknown")
        cv.status = "parsed"
    except Exception as exc:
        cv.status = "error"
        cv.error_message = str(exc)
    db.commit()


@router.post("/upload", response_model=CVResponse, status_code=201)
async def upload_cv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 10 MB)")

    file_id = str(uuid.uuid4())
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    with open(save_path, "wb") as f:
        f.write(content)

    cv = CVModel(
        id=file_id,
        filename=file.filename,
        raw_text="",
        status="pending",
    )
    db.add(cv)
    db.commit()
    db.refresh(cv)

    # Parse in background so response is immediate
    background_tasks.add_task(_parse_cv_background, cv.id, save_path, db)

    return cv


@router.get("/", response_model=list[CVResponse])
def list_cvs(db: Session = Depends(get_db)):
    return db.query(CVModel).order_by(CVModel.created_at.desc()).all()


@router.get("/{cv_id}", response_model=CVResponse)
def get_cv(cv_id: str, db: Session = Depends(get_db)):
    cv = db.query(CVModel).filter(CVModel.id == cv_id).first()
    if not cv:
        raise HTTPException(404, "CV not found")
    return cv


@router.delete("/{cv_id}", status_code=204)
def delete_cv(cv_id: str, db: Session = Depends(get_db)):
    cv = db.query(CVModel).filter(CVModel.id == cv_id).first()
    if not cv:
        raise HTTPException(404, "CV not found")
    db.delete(cv)
    db.commit()
