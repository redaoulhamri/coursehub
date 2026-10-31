# api/admin/admins.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db_manager import get_db
from database.models import Admin
from database.schemas.admins import (
    AdminCreate, 
    AdminResponse, 
    AdminPasswordChange
)

from ..middleware import get_current_admin 

admins_router = APIRouter(
    prefix="/api/admin/admins", 
    tags=["Admin - Admins"],
    dependencies=[Depends(get_current_admin)] 
)

@admins_router.get("/", response_model=list[AdminResponse])
def list_admins(db: Session = Depends(get_db)):
    admins = db.query(Admin).order_by(Admin.id).all()
    return admins

@admins_router.post("/", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def create_admin(data: AdminCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_admin = db.query(Admin).filter(Admin.email == data.email).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="An admin with this email already exists"
        )
    
    # Hash the password
    hashed_pwd = Admin.hash_pwd(data.password)
    
    new_admin = Admin(
        email=data.email,
        hashed_password=hashed_pwd
    )
    
    try:
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while creating admin")
        
    return new_admin

@admins_router.put("/change-password", status_code=status.HTTP_200_OK)
def change_my_password(
    data: AdminPasswordChange, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin) # Injects the logged-in admin
):
    # 1. Verify old password
    if not current_admin.verify_pwd(data.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect old password"
        )
    
    # 2. Prevent using the exact same password again
    if data.old_password == data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="New password cannot be the same as the old password"
        )

    # 3. Hash new password and save
    current_admin.hashed_password = Admin.hash_pwd(data.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

@admins_router.delete("/{admin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin(
    admin_id: int, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    # 1. Prevent admins from deleting themselves
    if current_admin.id == admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="You cannot delete your own account while logged in"
        )
        
    admin_to_delete = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin_to_delete:
        raise HTTPException(status_code=404, detail="Admin not found")
    
    # 2. Prevent deleting the last remaining admin in the DB
    total_admins = db.query(Admin).count()
    if total_admins <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot delete the last remaining admin account"
        )

    db.delete(admin_to_delete)
    db.commit()
    
    return None

