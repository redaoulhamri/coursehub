# api/views.py

from fastapi import APIRouter, status, Depends, HTTPException, Query
from sqlalchemy.orm import Session 
from sqlalchemy import or_

from database.models import Speciality, Module, SpecialityModule, Document, Professor, DocumentType
from database.db_manager import get_db 
from database.schemas.views import (
    SpecialityResponse, 
    ModuleResponse, 
    ProfessorGroupResponse, 
    PdfItemResponse,
    DownloadResponse
)

views_router = APIRouter(prefix="/api", tags=["Views"])


@views_router.get("/views/specialities",
                  status_code=status.HTTP_200_OK,
                  response_model=list[SpecialityResponse])
def get_specialities(db: Session = Depends(get_db)):
    specialities = db.query(Speciality).order_by(Speciality.name).all()
    return specialities


@views_router.get("/views/specialities/{speciality_id}/modules",
                  status_code=status.HTTP_200_OK,
                  response_model=list[ModuleResponse])
def get_modules_by_speciality(speciality_id: int, db: Session = Depends(get_db)):
    # Check if speciality exists
    speciality = db.query(Speciality).filter(Speciality.id == speciality_id).first()
    if not speciality:
        raise HTTPException(status_code=404, detail="Speciality not found")

    # Join Module and SpecialityModule to get modules for this speciality
    modules = db.query(Module).join(
        SpecialityModule, Module.id == SpecialityModule.module_id
    ).filter(SpecialityModule.speciality_id == speciality_id).all()
    
    return modules


@views_router.get("/views/documents",
                  status_code=status.HTTP_200_OK,
                  response_model=list[ProfessorGroupResponse])
def get_documents(
    speciality_id: int = Query(..., description="Filter by Speciality ID"),
    semester: int = Query(..., ge=1, le=6, description="Filter by Semester (1-6)"),
    type: DocumentType | None = Query(None, description="Filter by Document Type"),
    search: str | None = Query(None, description="Search by title, module, or professor name"),
    db: Session = Depends(get_db)
):
    # 1. Base Query
    query = db.query(Document).join(
        SpecialityModule, Document.speciality_module_id == SpecialityModule.id
    ).join(
        Professor, Document.professor_id == Professor.id
    ).join(
        Module, SpecialityModule.module_id == Module.id
    ).filter(
        SpecialityModule.speciality_id == speciality_id,
        Document.semester == semester
    )

    # 2. Apply Type Filter
    if type:
        query = query.filter(Document.type == type)

    # 3. Apply Search Filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Document.title.ilike(search_filter),
                Module.name.ilike(search_filter),
                Professor.first_name.ilike(search_filter),
                Professor.last_name.ilike(search_filter)
            )
        )

    # 4. Fetch and Sort Documents
    documents = query.order_by(Document.created_at.desc()).all()

    # 5. Group by Professor
    grouped_data = {}
    
    for doc in documents:
        prof_id = doc.professor_id
        
        if prof_id not in grouped_data:
            grouped_data[prof_id] = {
                "professor_id": prof_id,
                "professor_name": f"Pr. {doc.professor.first_name} {doc.professor.last_name}",
                "module_name": doc.speciality_module.module.name,
                "pdfs": []
            }
            
        # Add the PDF to the professor's list
        grouped_data[prof_id]["pdfs"].append(
            PdfItemResponse(
                id=doc.id,
                title=doc.title,
                type=doc.type,
                number_of_pages=doc.number_of_pages,
                file_size=doc.media.file_size,
                mime_type=doc.media.mime_type,
                created_at=doc.created_at
            )
        )

    return list(grouped_data.values())


@views_router.get("/views/documents/{document_id}/download",
                  status_code=status.HTTP_200_OK,
                  response_model=DownloadResponse)
def download_document(document_id: int, db: Session = Depends(get_db)):
    # 1. Find the document
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # 2. Increment download count
    document.download_count += 1
    db.commit()

    # 3. Return the file URL 
    return DownloadResponse(
        download_url=document.media.path,
        filename=document.media.filename
    )

