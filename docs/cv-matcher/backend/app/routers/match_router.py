import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.db_models import MatchModel, CVModel, JobModel
from ..models.schemas import MatchRequest, MatchResponse, PipelineUpdate
from ..services.ai_service import match_cv_to_job

router = APIRouter(prefix="/api/matching", tags=["matching"])

async def _run_match_background(match_id: int, cv_id: int, job_id: int, db_url: str):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        match = db.query(MatchModel).filter(MatchModel.id == match_id).first()
        cv    = db.query(CVModel).filter(CVModel.id == cv_id).first()
        job   = db.query(JobModel).filter(JobModel.id == job_id).first()
        if not match or not cv or not job:
            return
        cv_data  = json.loads(cv.parsed_data  or "{}")
        job_data = json.loads(job.parsed_data  or "{}")
        result   = await match_cv_to_job(cv_data, job_data)
        if not result:
            match.status = "error"
            match.error_message = "AI returned empty result"
            db.commit()
            return
        sd = result.get("scores_detail", {})
        match.overall_score       = float(result.get("score_global", 0))
        match.skills_score        = float(sd.get("competences_techniques", 0))
        match.experience_score    = float(sd.get("experience_pertinente", 0))
        match.education_score     = float(sd.get("formation", 0))
        match.culture_score       = float(sd.get("culture_fit", 0))
        match.potential_score     = float(sd.get("potentiel_evolution", 0))
        match.communication_score = float(sd.get("communication_leadership", 0))
        match.recommendation      = result.get("recommendation", "MOYEN")
        match.match_data          = json.dumps(result, ensure_ascii=False)
        match.status              = "completed"
        db.commit()
    except Exception as e:
        try:
            match.status = "error"
            match.error_message = str(e)[:500]
            db.commit()
        except Exception:
            pass
    finally:
        db.close()

@router.post("/run")
async def run_matching(req: MatchRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    from ..config import DATABASE_URL
    import asyncio
    job = db.query(JobModel).filter(JobModel.id == req.job_id).first()
    if not job:
        raise HTTPException(404, "Job not found")
    created = []
    for cv_id in req.cv_ids:
        cv = db.query(CVModel).filter(CVModel.id == cv_id).first()
        if not cv:
            continue
        existing = db.query(MatchModel).filter(
            MatchModel.cv_id == cv_id, MatchModel.job_id == req.job_id
        ).first()
        if existing:
            if existing.status == "error":
                existing.status = "pending"
                db.commit()
                background_tasks.add_task(
                    lambda eid=existing.id, cid=cv_id: asyncio.run(_run_match_background(eid, cid, req.job_id, DATABASE_URL))
                )
            created.append(existing.id)
            continue
        m = MatchModel(cv_id=cv_id, job_id=req.job_id, status="pending")
        db.add(m)
        db.commit()
        db.refresh(m)
        background_tasks.add_task(
            lambda mid=m.id, cid=cv_id: asyncio.run(_run_match_background(mid, cid, req.job_id, DATABASE_URL))
        )
        created.append(m.id)
    return {"created": len(created), "match_ids": created}

@router.get("/job/{job_id}", response_model=list[MatchResponse])
def get_matches_for_job(job_id: int, db: Session = Depends(get_db)):
    matches = (
        db.query(MatchModel)
        .filter(MatchModel.job_id == job_id)
        .order_by(MatchModel.overall_score.desc())
        .all()
    )
    result = []
    for m in matches:
        d = m.__dict__.copy()
        d["match_data"]     = json.loads(m.match_data or "{}")
        d["candidate_name"] = m.cv.candidate_name  if m.cv  else ""
        d["job_title"]      = m.job.title           if m.job else ""
        result.append(d)
    return result

@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: int, db: Session = Depends(get_db)):
    m = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not m:
        raise HTTPException(404, "Match not found")
    d = m.__dict__.copy()
    d["match_data"]     = json.loads(m.match_data or "{}")
    d["candidate_name"] = m.cv.candidate_name  if m.cv  else ""
    d["job_title"]      = m.job.title           if m.job else ""
    return d

@router.patch("/{match_id}/pipeline")
def update_pipeline(match_id: int, update: PipelineUpdate, db: Session = Depends(get_db)):
    m = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not m:
        raise HTTPException(404, "Match not found")
    valid = {"nouveau", "examen", "entretien", "offre", "recrute", "rejete"}
    if update.pipeline_status not in valid:
        raise HTTPException(400, f"Status must be one of: {valid}")
    m.pipeline_status = update.pipeline_status
    if update.notes is not None:
        m.notes = update.notes
    db.commit()
    return {"ok": True, "pipeline_status": m.pipeline_status}

@router.delete("/{match_id}")
def delete_match(match_id: int, db: Session = Depends(get_db)):
    m = db.query(MatchModel).filter(MatchModel.id == match_id).first()
    if not m:
        raise HTTPException(404, "Match not found")
    db.delete(m)
    db.commit()
    return {"ok": True}

@router.get("/stats/overview")
def get_stats(db: Session = Depends(get_db)):
    from ..models.db_models import CVModel, JobModel
    nb_cvs    = db.query(CVModel).count()
    nb_jobs   = db.query(JobModel).count()
    nb_matches= db.query(MatchModel).filter(MatchModel.status == "completed").count()
    nb_top    = db.query(MatchModel).filter(MatchModel.overall_score >= 80).count()
    pipeline  = {}
    for row in db.query(MatchModel.pipeline_status).all():
        s = row[0] or "nouveau"
        pipeline[s] = pipeline.get(s, 0) + 1
    return {
        "nb_cvs": nb_cvs,
        "nb_jobs": nb_jobs,
        "nb_matches": nb_matches,
        "nb_top": nb_top,
        "pipeline": pipeline,
    }
