from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.database import get_db
from app.services.document_service import DocumentService
from app.models.document import Document
from pydantic import BaseModel

router = APIRouter()


class DocumentResponse(BaseModel):
    id: int
    title: str
    authors: List[str]
    abstract: str
    doi: Optional[str]
    url: Optional[str]
    file_type: str
    extracted_claims: List[str]
    confidence_score: float
    method_quality_score: float
    created_at: str


class DocumentUploadRequest(BaseModel):
    url: Optional[str] = None
    doi: Optional[str] = None


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    doi: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(db)

    try:
        if file:
            document = await service.process_uploaded_file(file)
        elif url:
            document = await service.process_url(url)
        elif doi:
            document = await service.process_doi(doi)
        else:
            raise HTTPException(status_code=400, detail="Must provide file, URL, or DOI")
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=f"Permission denied: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    try:
        return DocumentResponse(
            id=document.id,
            title=document.title,
            authors=document.authors or [],
            abstract=document.abstract or "",
            doi=document.doi,
            url=document.url,
            file_type=document.file_type,
            extracted_claims=document.extracted_claims or [],
            confidence_score=document.confidence_score,
            method_quality_score=document.method_quality_score,
            created_at=document.created_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to format document response: {str(e)}")


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: AsyncSession = Depends(get_db)):
    try:
        service = DocumentService(db)
        document = await service.get_document(document_id)

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid document ID: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    try:
        return DocumentResponse(
            id=document.id,
            title=document.title,
            authors=document.authors or [],
            abstract=document.abstract or "",
            doi=document.doi,
            url=document.url,
            file_type=document.file_type,
            extracted_claims=document.extracted_claims or [],
            confidence_score=document.confidence_score,
            method_quality_score=document.method_quality_score,
            created_at=document.created_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to format document response: {str(e)}")


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    try:
        service = DocumentService(db)
        documents = await service.list_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(e)}")

    try:
        return [
            DocumentResponse(
                id=doc.id,
                title=doc.title,
                authors=doc.authors or [],
                abstract=doc.abstract or "",
                doi=doc.doi,
                url=doc.url,
                file_type=doc.file_type,
                extracted_claims=doc.extracted_claims or [],
                confidence_score=doc.confidence_score,
                method_quality_score=doc.method_quality_score,
                created_at=doc.created_at.isoformat(),
            )
            for doc in documents
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to format document response: {str(e)}")
