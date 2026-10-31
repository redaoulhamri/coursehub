# database/schemas/catalog.py

from pydantic import BaseModel, Field, ConfigDict

# --- Speciality ---
class SpecialityCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=40)

class SpecialityUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=40)

class SpecialityResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

# --- Module ---
class ModuleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=40)

class ModuleUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=40)

class ModuleResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

# --- Speciality Module (Junction) ---
class SpecialityModuleCreate(BaseModel):
    speciality_id: int
    module_id: int

class SpecialityModuleResponse(BaseModel):
    id: int
    speciality_id: int
    module_id: int
    model_config = ConfigDict(from_attributes=True)
    