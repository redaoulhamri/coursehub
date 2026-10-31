# database/schemas/documents.py

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from database.models import DocumentType

# --- Media ---
class MediaResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    mime_type: str
    alt: str
    path: str
    model_config = ConfigDict(from_attributes=True)

# --- Document ---
class DocumentResponse(BaseModel):
    id: int
    title: str
    number_of_pages: int
    semester: int
    type: DocumentType
    download_count: int
    school_year: str
    professor_id: int
    speciality_module_id: int
    created_at: datetime
    updated_at: datetime
    media: MediaResponse
    model_config = ConfigDict(from_attributes=True)

class DocumentUpdate(BaseModel):
    # All fields are optional for partial updates (PUT/PATCH)
    title: str | None = Field(None, min_length=2, max_length=255)
    number_of_pages: int | None = Field(None, ge=1)
    semester: int | None = Field(None, ge=1, le=6)
    type: DocumentType | None = None
    school_year: str | None = Field(None, min_length=9, max_length=9)
    professor_id: int | None = None
    speciality_module_id: int | None = None

    