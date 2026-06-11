"""Visa Application model for the Visa Application System"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from . import Base

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

class VisaApplication(Base):
    """Visa application model"""
    __tablename__ = "visa_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    destination_country = Column(String(100), nullable=False)
    visa_type = Column(String(100), nullable=False)
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

# Import User here to avoid circular imports
from .user import User
User.applications = relationship("VisaApplication", back_populates="user", cascade="all, delete-orphan")
