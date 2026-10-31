# database/schemas/professors.py

from pydantic import BaseModel, Field, ConfigDict

class ProfessorCreate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=40)
    last_name: str = Field(..., min_length=2, max_length=40)

class ProfessorUpdate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=40)
    last_name: str = Field(..., min_length=2, max_length=40)

class ProfessorResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    model_config = ConfigDict(from_attributes=True)

    