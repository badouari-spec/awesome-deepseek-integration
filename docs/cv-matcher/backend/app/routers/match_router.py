from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.db_models import CVModel, JobModel, MatchModel
from ..models.schemas import MatchRequest, MatchResponse
from ..services.ai_service import match_cv_to_job

router = APIRouter()


async def _run_match_background(match_id: str, cv_id: str, job_id: str, db: Session):
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    cv = db.query(CVModel).filter(CVModel.id == cv_id).first()
    job = db.query(JobModel).filter(JobModel.id == job_id).first()

    if not match or not cv or not job:
        return
    if not cv.parsed_data or not job.parsed_data:
        match.status = "error"
        match.error_message = "CV or Job not yet parsed. Please wait and retry."
        db.commit()
        return

    try:
        result = await match_cv_to_job(cv.parsed_data, job.parsed_data)
        scores = result.get("scores", {})
        match.overall_score = float(result.get("overall_score", 0))
        match.skills_score = float(scores.get("skills", 0))
        match.experience_score = float(scores.get("experience", 0))
        match.education_score = float(scores.get("education", 0))
        match.culture_score = float(scores.get("culture_fit", 0))
        match.recommendation = result.get("recommendation", "")
        match.match_data = result
        match.status = "completed"
    except Exception as exc:
        match.status = "error"
        match.error_message = str(exc)
    db.commit()


@router.post("/run", response_model=list[MatchResponse], status_code=202)
def run_matching(
    payload: MatchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = db.query(JobModel).filter(JobModel.id == payload.job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")

    results = []
    for cv_id in payload.cv_ids:
        cv = db.query(CVModel).filter(CVModel.id == cv_id).first()
        if not cv:
            continue

        # Avoid duplicates — reuse existing pending/completed match
        existing = (
            db.query(MatchModel)
            .filter(MatchModel.cv_id == cv_id, MatchModel.job_id == payload.job_id)
            .order_by(MatchModel.created_at.desc())
            .first()
        )
        if existing and existing.status in ("pending", "completed"):
            results.append(existing)
            continue

        match = MatchModel(cv_id=cv_id, job_id=payload.job_id, status="pending")
        db.add(match)
        db.commit()
        db.refresh(match)
        background_tasks.add_task(_run_match_background, match.id, cv_id, payload.job_id, db)
        results.append(match)

    return results


@router.get("/job/{job_id}", response_model=list[MatchResponse])
def get_matches_for_job(job_id: str, db: Session = Depends(get_db)):
    return (
        db.query(MatchModel)
        .filter(MatchModel.job_id == job_id)
        .order_by(MatchModel.overall_score.desc().nullslast())
        .all()
    )


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: str, db: Session = Depends(get_db)):
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(404, "Match not found")
    return match


@router.delete("/{match_id}", status_code=204)
def delete_match(match_id: str, db: Session = Depends(get_db)):
    match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not match:
        raise HTTPException(404, "Match not found")
    db.delete(match)
    db.commit()
