# api/admin/documents.py

import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.db_manager import get_db
from database.models import Document, Media, Professor, SpecialityModule, DocumentType
from database.schemas.documents import DocumentResponse, DocumentUpdate

from ..middleware import get_current_admin 

documents_router = APIRouter(
    prefix="/api/admin/documents", 
    tags=["Admin - Documents"],
    dependencies=[Depends(get_current_admin)]
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True) 


@documents_router.get("/", response_model=list[DocumentResponse])
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    documents = db.query(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    return documents


@documents_router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@documents_router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    title: str = Form(...),
    number_of_pages: int = Form(...),
    semester: int = Form(...),
    type: DocumentType = Form(...),
    school_year: str = Form(...),
    professor_id: int = Form(...),
    speciality_module_id: int = Form(...),
    alt: str = Form(...), 
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Validate Foreign Keys
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    if not professor:
        raise HTTPException(status_code=404, detail="Professor not found")
    
    spec_module = db.query(SpecialityModule).filter(SpecialityModule.id == speciality_module_id).first()
    if not spec_module:
        raise HTTPException(status_code=404, detail="Speciality Module link not found")

    # 2. Validate File Type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # 3. Save File to Disk
    file_extension = ".pdf"
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # 4. Create Media Record
    file_size = os.path.getsize(file_path)
    
    new_media = Media(
        filename=file.filename, 
        file_size=file_size,
        mime_type=file.content_type,
        alt=alt,
        path=f"/uploads/{unique_filename}" 
    )
    db.add(new_media)
    db.flush() 

    # 5. Create Document Record
    new_document = Document(
        media_id=new_media.id,
        professor_id=professor_id,
        speciality_module_id=speciality_module_id,
        title=title,
        number_of_pages=number_of_pages,
        semester=semester,
        type=type,
        school_year=school_year
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    
    return new_document


@documents_router.put("/{document_id}", response_model=DocumentResponse)
def update_document(document_id: int, data: DocumentUpdate, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(document, key, value)

    try:
        db.commit()
        db.refresh(document)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid update data. Check foreign keys.")
    
    return document


@documents_router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = Path(document.media.path.lstrip("/"))
    
    try:
        db.delete(document)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # 3. Delete Physical File
    if file_path.exists():
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not delete physical file {file_path}. Error: {e}")
    
    return None

