from fastapi import APIRouter
from app.api.v1 import resumes, candidates, evidence, jobs, sessions

api_router = APIRouter()
api_router.include_router(resumes.router)
api_router.include_router(candidates.router)
api_router.include_router(evidence.router)
api_router.include_router(jobs.router)
api_router.include_router(sessions.router)
