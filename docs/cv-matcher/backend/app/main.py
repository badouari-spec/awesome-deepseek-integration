import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import engine, Base
from .routers import cv_router, job_router, match_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DeepSeek CV Matcher",
    description="AI-powered CV/Resume matching engine powered by DeepSeek",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cv_router.router, prefix="/api/cv", tags=["CV Management"])
app.include_router(job_router.router, prefix="/api/jobs", tags=["Job Management"])
app.include_router(match_router.router, prefix="/api/matching", tags=["Matching"])

if getattr(sys, "frozen", False):
    # PyInstaller bundle: frontend is bundled inside _MEIPASS
    FRONTEND_DIR = os.path.join(sys._MEIPASS, "frontend")
else:
    FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")

if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
