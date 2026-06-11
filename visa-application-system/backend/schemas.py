"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ApplicationStatusEnum(str, Enum):
    """Application status options"""
    DRAFT = "draft"
    INCOMPLETE = "incomplete"
    READY_FOR_REVIEW = "ready_for_review"
    PENDING_AGENT_REVIEW = "pending_agent_review"
    UNDER_REVIEW = "under_review"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    nationality: str = "Bangladeshi"


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str = "bearer"


# Application Schemas
class ApplicationBase(BaseModel):
    """Base application schema"""
    destination_country: str
    visa_type: str


class ApplicationCreate(ApplicationBase):
    """Schema for creating a new application"""
    pass


class ApplicationResponse(ApplicationBase):
    """Schema for application response"""
    id: int
    user_id: int
    status: ApplicationStatusEnum
    application_reference: Optional[str] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    applicant_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


# Document Schemas
class DocumentBase(BaseModel):
    """Base document schema"""
    document_type: str


class DocumentUpload(DocumentBase):
    """Schema for document upload"""
    file_path: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: int
    application_id: int
    file_path: str
    file_name: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    ocr_confidence: Optional[int] = None
    is_valid: bool
    validation_errors: Optional[List[str]] = None
    status: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# Country Requirements Schema
class CountryRequirementResponse(BaseModel):
    """Schema for country requirements response"""
    country_code: str
    country_name: str
    visa_required: bool
    required_documents: List[str]
    passport_validity_months: int
    min_financial_proof: Optional[int] = None
    requires_biometric: bool
    requires_interview: bool
    processing_time_days: Optional[int] = None
    gdpr_compliant: bool
    data_retention_days: int


# Validation Response Schema
class ValidationResponse(BaseModel):
    """Schema for application validation response"""
    application_id: int
    is_complete: bool
    missing_documents: List[str]
    validation_errors: List[str]
    status: str


# Agent Review Schema
class AgentReviewRequest(BaseModel):
    """Schema for agent review submission"""
    agent_notes: Optional[str] = None
    decision: Optional[str] = None  # approve, reject, request_more_info


class AgentReviewResponse(BaseModel):
    """Schema for agent review response"""
    application_id: int
    status: str
    reviewed_by: int
    reviewed_at: datetime
    agent_notes: Optional[str] = None
