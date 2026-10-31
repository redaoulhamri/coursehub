# database/schemas/views.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from database.models import DocumentType

# --- Specialities & Modules ---
class SpecialityResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class ModuleResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


# --- Documents (Grouped by Professor) ---
class PdfItemResponse(BaseModel):
    id: int
    title: str
    type: DocumentType
    number_of_pages: int
    file_size: int
    mime_type: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ProfessorGroupResponse(BaseModel):
    professor_id: int
    professor_name: str
    module_name: str
    pdfs: list[PdfItemResponse]


# --- Download ---
class DownloadResponse(BaseModel):
    download_url: str
    filename: str
    