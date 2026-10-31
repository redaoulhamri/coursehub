# api/admin/professors.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from database.db_manager import get_db
from database.models import Professor
from database.schemas.professors import (
    ProfessorCreate, 
    ProfessorUpdate, 
    ProfessorResponse
)

from ..middleware import get_current_admin 

professors_router = APIRouter(
    prefix="/api/admin/professors", 
    tags=["Admin - Professors"],
    dependencies=[Depends(get_current_admin)] 
)

@professors_router.get("/", response_model=list[ProfessorResponse])
def list_professors(db: Session = Depends(get_db)):
    professors = db.query(Professor).order_by(Professor.last_name, Professor.first_name).all()
    return professors

@professors_router.post("/", response_model=ProfessorResponse, status_code=status.HTTP_201_CREATED)
def create_professor(data: ProfessorCreate, db: Session = Depends(get_db)):
    existing = db.query(Professor).filter(
        and_(
            Professor.first_name.ilike(data.first_name),
            Professor.last_name.ilike(data.last_name)
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="This professor already exists in the system")
    
    new_professor = Professor(
        first_name=data.first_name,
        last_name=data.last_name
    )
    db.add(new_professor)
    db.commit()
    db.refresh(new_professor)
    return new_professor

@professors_router.put("/{professor_id}", response_model=ProfessorResponse)
def update_professor(professor_id: int, data: ProfessorUpdate, db: Session = Depends(get_db)):
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    if not professor:
        raise HTTPException(status_code=404, detail="Professor not found")
    
    professor.first_name = data.first_name
    professor.last_name = data.last_name
    db.commit()
    db.refresh(professor)
    return professor

@professors_router.delete("/{professor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professor(professor_id: int, db: Session = Depends(get_db)):
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    if not professor:
        raise HTTPException(status_code=404, detail="Professor not found")
    
    try:
        db.delete(professor)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete this professor because they are linked to existing documents. Please delete or reassign their documents first."
        )

    