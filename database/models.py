# database/models.py

from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import (
    BigInteger, 
    DateTime, 
    ForeignKey, 
    Index, 
    Integer, 
    SmallInteger, 
    String, 
    Column,
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from .db_manager import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class DocumentType(str, Enum):
    exam_norm = "exam_norm"
    td = "td"
    controle = "controle"
    exam_ratt = "exam_ratt"
    course = "course"
    tp = "tp"
    corrige = "corrige"


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    def verify_pwd(self, plain_pwd: str) -> bool:
        return pwd_context.verify(plain_pwd, self.hashed_password)

    @staticmethod
    def hash_pwd(plain_pwd: str) -> str:
        return pwd_context.hash(plain_pwd)
    

class Speciality(Base):
    __tablename__ = "specialities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40), nullable=False, unique=True)

    # Relationships
    speciality_modules = relationship(
        "SpecialityModule", 
        back_populates="speciality", 
        cascade="all, delete-orphan"
    )


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(40), nullable=False)

    # Relationships
    speciality_modules = relationship(
        "SpecialityModule", 
        back_populates="module", 
        cascade="all, delete-orphan"
    )


class SpecialityModule(Base):
    """
    Junction table linking Specialities and Modules.
    Documents link to this table to ensure a document belongs to a specific module within a specific speciality.
    """
    __tablename__ = "speciality_modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(
        Integer, 
        ForeignKey("modules.id", ondelete="CASCADE"), 
        nullable=False
    )
    speciality_id = Column(
        Integer, 
        ForeignKey("specialities.id", ondelete="CASCADE"), 
        nullable=False
    )

    # Relationships
    speciality = relationship("Speciality", back_populates="speciality_modules")
    module = relationship("Module", back_populates="speciality_modules")
    documents = relationship("Document", back_populates="speciality_module")

    # Ensure a speciality cannot have the exact same module added twice
    __table_args__ = (
        Index("idx_unique_spec_mod", "speciality_id", "module_id", unique=True),
    )


class Professor(Base):
    __tablename__ = "professors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(40), nullable=False)
    last_name = Column(String(40), nullable=False)

    # Relationships
    documents = relationship("Document", back_populates="professor")


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(255), nullable=False, default="application/pdf")
    alt = Column(String(255), nullable=False)
    path = Column(String(255), nullable=False) 

    # Relationships
    document = relationship("Document", back_populates="media", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    media_id = Column(
        Integer, 
        ForeignKey("media.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False
    )
    professor_id = Column(
        Integer, 
        ForeignKey("professors.id", ondelete="RESTRICT"), 
        nullable=False
    )
    speciality_module_id = Column(
        Integer, 
        ForeignKey("speciality_modules.id", ondelete="RESTRICT"), 
        nullable=False
    )

    # Data Columns
    title = Column(String(255), nullable=False)
    number_of_pages = Column(Integer, nullable=False)
    semester = Column(SmallInteger, nullable=False) 
    type = Column(SQLEnum(DocumentType), nullable=False)
    download_count = Column(Integer, default=0, nullable=False)
    school_year = Column(String(9), nullable=False) 
    
    # Timestamps
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    # Relationships
    media = relationship("Media", back_populates="document")
    professor = relationship("Professor", back_populates="documents")
    speciality_module = relationship("SpecialityModule", back_populates="documents")

    # Composite Index for fast frontend querying
    __table_args__ = (
        Index("idx_semester", "semester"),
        Index("idx_professor", "professor_id"),
    )

    