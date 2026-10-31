# api/auth.py 
 
from fastapi import APIRouter, status, Depends, HTTPException, Request
from sqlalchemy.orm import Session 

from database.models import Admin 
from database.schemas.auth import LoginForm, LoginSuccess
from database.db_manager import get_db 

from .middleware import create_token 

auth_router = APIRouter(prefix="/api/auth", tags=["Authentification"])


@auth_router.post("/login",
             status_code=status.HTTP_200_OK,
             responses={
    status.HTTP_200_OK: {"model": LoginSuccess, "description": "Login successful"},
    status.HTTP_404_NOT_FOUND : {"description" : "Invalid credentials"}
})
def login(request : Request, login_credentials : LoginForm, db : Session = Depends(get_db)):
    email = login_credentials.email
    password = login_credentials.password
        
    admin = db.query(Admin).filter(Admin.email == email).first()
    
    if not admin :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")

    if not admin.verify_pwd(password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Credentials")
  
    # Token
    if login_credentials.rememberme :
        token = create_token(admin.id,4320)  # 3 days
    else :
        token = create_token(admin.id)

    return LoginSuccess(
        access_token=token
    )


