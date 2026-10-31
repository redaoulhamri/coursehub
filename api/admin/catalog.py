# api/admin/catalog.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.db_manager import get_db
from database.models import Speciality, Module, SpecialityModule
from database.schemas.catalog import (
    SpecialityCreate, SpecialityUpdate, SpecialityResponse,
    ModuleCreate, ModuleUpdate, ModuleResponse,
    SpecialityModuleCreate, SpecialityModuleResponse
)

from ..middleware import get_current_admin 

catalog_router = APIRouter(
    prefix="/api/admin/catalog", 
    tags=["Admin - Catalog"],
    dependencies=[Depends(get_current_admin)]
)

# ==========================================
# SPECIALITIES
# ==========================================

@catalog_router.get("/specialities", response_model=list[SpecialityResponse])
def list_specialities(db: Session = Depends(get_db)):
    return db.query(Speciality).order_by(Speciality.name).all()

@catalog_router.post("/specialities", response_model=SpecialityResponse, status_code=status.HTTP_201_CREATED)
def create_speciality(data: SpecialityCreate, db: Session = Depends(get_db)):
    existing = db.query(Speciality).filter(Speciality.name.ilike(data.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Speciality already exists")
    
    new_speciality = Speciality(name=data.name)
    db.add(new_speciality)
    db.commit()
    db.refresh(new_speciality)
    return new_speciality

@catalog_router.put("/specialities/{speciality_id}", response_model=SpecialityResponse)
def update_speciality(speciality_id: int, data: SpecialityUpdate, db: Session = Depends(get_db)):
    speciality = db.query(Speciality).filter(Speciality.id == speciality_id).first()
    if not speciality:
        raise HTTPException(status_code=404, detail="Speciality not found")
    
    speciality.name = data.name
    db.commit()
    db.refresh(speciality)
    return speciality

@catalog_router.delete("/specialities/{speciality_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_speciality(speciality_id: int, db: Session = Depends(get_db)):
    speciality = db.query(Speciality).filter(Speciality.id == speciality_id).first()
    if not speciality:
        raise HTTPException(status_code=404, detail="Speciality not found")
    
    try:
        db.delete(speciality)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete this speciality because it is linked to existing documents or modules."
        )

# ==========================================
# MODULES
# ==========================================

@catalog_router.get("/modules", response_model=list[ModuleResponse])
def list_modules(db: Session = Depends(get_db)):
    return db.query(Module).order_by(Module.name).all()

@catalog_router.post("/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
def create_module(data: ModuleCreate, db: Session = Depends(get_db)):
    existing = db.query(Module).filter(Module.name.ilike(data.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Module already exists")
    
    new_module = Module(name=data.name)
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    return new_module

@catalog_router.put("/modules/{module_id}", response_model=ModuleResponse)
def update_module(module_id: int, data: ModuleUpdate, db: Session = Depends(get_db)):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    module.name = data.name
    db.commit()
    db.refresh(module)
    return module

@catalog_router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(module_id: int, db: Session = Depends(get_db)):
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    try:
        db.delete(module)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete this module because it is linked to existing documents."
        )

# ==========================================
# SPECIALITY MODULES (Linking)
# ==========================================

@catalog_router.get("/speciality-modules", response_model=list[SpecialityModuleResponse])
def list_speciality_modules(db: Session = Depends(get_db)):
    return db.query(SpecialityModule).all()

@catalog_router.post("/speciality-modules", response_model=SpecialityModuleResponse, status_code=status.HTTP_201_CREATED)
def link_module_to_speciality(data: SpecialityModuleCreate, db: Session = Depends(get_db)):
    speciality = db.query(Speciality).filter(Speciality.id == data.speciality_id).first()
    if not speciality:
        raise HTTPException(status_code=404, detail="Speciality not found")
        
    module = db.query(Module).filter(Module.id == data.module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
        
    existing_link = db.query(SpecialityModule).filter(
        SpecialityModule.speciality_id == data.speciality_id,
        SpecialityModule.module_id == data.module_id
    ).first()
    
    if existing_link:
        raise HTTPException(status_code=400, detail="This module is already linked to this speciality")

    new_link = SpecialityModule(
        speciality_id=data.speciality_id,
        module_id=data.module_id
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link

@catalog_router.delete("/speciality-modules/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_module_from_speciality(link_id: int, db: Session = Depends(get_db)):
    link = db.query(SpecialityModule).filter(SpecialityModule.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
        
    try:
        db.delete(link)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Cannot unlink this module because there are documents attached to it."
        )
    