# api/middleware.py

from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from config import SECRET_KEY, ALGO
from database.db_manager import get_db
from database.models import Admin

EXPIRATION = 30

Oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/api/auth/login")

def create_token(user_id : int, exp : int = None) -> str:
    if exp is None :
        exp = EXPIRATION
        
    payload = {
        "sub" : str(user_id),
        "exp" : datetime.now(timezone.utc) + timedelta(minutes=exp)
    }

    return jwt.encode(payload,SECRET_KEY,algorithm=ALGO)


def get_current_admin(
    token: str = Depends(Oauth2_scheme), 
    db: Session = Depends(get_db)
) -> Admin:
    """
    Extracts the token, decodes it, and returns the Admin object from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decode the JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        
        # 2. Extract the admin ID from the 'sub' claim
        admin_id_str: str = payload.get("sub")
        if admin_id_str is None:
            raise credentials_exception
            
        admin_id = int(admin_id_str)
        
    except JWTError:
        # Token is expired, signature is invalid, or malformed
        raise credentials_exception
    except ValueError:
        # The 'sub' claim was not a valid integer
        raise credentials_exception

    # 3. Fetch the admin from the database
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if admin is None:
        # Token is valid, but the admin was deleted from the DB
        raise credentials_exception

    return admin


def is_admin(current_admin: Admin = Depends(get_current_admin)) -> bool:
    """
    A dependency that ensures the user is an admin. 
    Since get_current_admin already raises 401 if not found, 
    if this executes, the user is guaranteed to be an admin.
    """
    if not current_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return True

