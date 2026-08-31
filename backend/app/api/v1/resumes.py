from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.domains.candidate.text_extractor import TextExtractionError
from app.domains.candidate.schemas import ResumeExtractionResponse
from app.domains.candidate.resume_service import ResumeExtractionService

router = APIRouter(prefix="/resumes", tags=["Resumes"])

@router.post("/extract", response_model=ResumeExtractionResponse)
async def extract_resume(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Extract candidate claims, education, skills, and projects from a PDF or DOCX resume.
    
    IMPORTANT: This endpoint returns UNCONFIRMED claims only. It does not calculate proficiency,
    readiness, or hiring probability.
    """
    try:
        content = await file.read()
        return await ResumeExtractionService.extract_and_normalize(
            db=db,
            file_bytes=content,
            filename=file.filename or "resume.pdf",
        )
    except TextExtractionError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during resume extraction: {str(e)}",
        )
