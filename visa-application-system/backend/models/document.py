"""Document model for the Visa Application System"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base

class Document(Base):
    """Document model for uploaded files"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("visa_applications.id"), nullable=False)
    document_type = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # OCR and extraction results
    extracted_data = Column(JSON, default=dict)
    ocr_confidence = Column(Integer)
    
    # Validation
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(JSON, default=list)
    status = Column(String(50), default="uploaded")
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Relationships
    application = relationship("VisaApplication", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, type={self.document_type}, status={self.status})>"

# Import to establish relationship
from .application import VisaApplication
VisaApplication.documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
