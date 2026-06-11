"""
Database models for the Visa Application System
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class ApplicationStatus(enum.Enum):
    """Visa application status options"""
    DRAFT = "draft"
    INCOMPLETE = "incomplete"
    READY_FOR_REVIEW = "ready_for_review"
    PENDING_AGENT_REVIEW = "pending_agent_review"
    UNDER_REVIEW = "under_review"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    """User model for applicants"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20))
    nationality = Column(String(100), default="Bangladeshi")
    passport_number = Column(String(50))
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = relationship("VisaApplication", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class VisaApplication(Base):
    """Visa application model"""
    __tablename__ = "visa_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destination_country = Column(String(100), nullable=False)
    visa_type = Column(String(100), nullable=False)  # tourist, business, work, student, etc.
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.DRAFT)
    application_reference = Column(String(100), unique=True)
    submitted_at = Column(DateTime)
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Extracted applicant data
    applicant_data = Column(JSON, default=dict)
    
    # Relationships
    user = relationship("User", back_populates="applications")
    documents = relationship("Document", back_populates="application", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VisaApplication(id={self.id}, country={self.destination_country}, status={self.status})>"


class Document(Base):
    """Document model for uploaded files"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("visa_applications.id"), nullable=False)
    document_type = Column(String(100), nullable=False)  # passport, photo, bank_statement, etc.
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255))
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # OCR and extraction results
    extracted_data = Column(JSON, default=dict)
    ocr_confidence = Column(Integer)  # 0-100
    
    # Validation
    is_valid = Column(Boolean, default=True)
    validation_errors = Column(JSON, default=list)
    status = Column(String(50), default="uploaded")  # uploaded, processing, processed, failed
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Relationships
    application = relationship("VisaApplication", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, type={self.document_type}, status={self.status})>"


class CountryRequirement(Base):
    """Country-specific visa requirements"""
    __tablename__ = "country_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(10), nullable=False)
    country_name = Column(String(100), nullable=False)
    visa_required = Column(Boolean, default=True)
    
    # Required documents (stored as JSON array)
    required_documents = Column(JSON, default=list)
    
    # Specific requirements
    passport_validity_months = Column(Integer, default=6)
    min_financial_proof = Column(Integer)  # Minimum funds required
    requires_biometric = Column(Boolean, default=False)
    requires_interview = Column(Boolean, default=False)
    processing_time_days = Column(Integer)
    
    # Data handling regulations
    gdpr_compliant = Column(Boolean, default=False)
    data_retention_days = Column(Integer, default=90)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CountryRequirement(code={self.country_code}, name={self.country_name})>"


class AuditLog(Base):
    """Audit log for tracking all actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, timestamp={self.created_at})>"
