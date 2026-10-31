# database/schemas/admins.py

from pydantic import BaseModel, EmailStr, Field, ConfigDict

class AdminCreate(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, max_length=72, description="Password must be at least 8 characters")

class AdminResponse(BaseModel):
    id: int
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class AdminPasswordChange(BaseModel):
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=72, description="New password must be at least 8 characters")

    