"""
Visa Application Filing System - Backend API
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import datetime
import logging

from config.settings import settings
from backend.models.user import User, UserCreate
from backend.models.application import VisaApplication, ApplicationCreate
from backend.models.document import Document, DocumentUpload
from backend.services.auth import AuthService
from backend.services.document_processor import DocumentProcessor
from backend.services.country_rules import CountryRuleEngine
from backend.database.session import get_db
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Visa Application Filing System",
    description="Automated visa application filing system for Bangladeshi applicants",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()

# Initialize services
auth_service = AuthService()
doc_processor = DocumentProcessor()
rule_engine = CountryRuleEngine()


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Visa Application Filing System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/auth/register", response_model=User)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user = auth_service.create_user(db, user_data)
        logger.info(f"New user registered: {user.email}")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login")
async def login_user(credentials: dict, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    user = auth_service.authenticate_user(
        db, 
        credentials.get("email"), 
        credentials.get("password")
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token = auth_service.create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/api/user/profile")
async def get_user_profile(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    return current_user


@app.get("/api/countries")
async def get_supported_countries():
    """Get list of supported destination countries"""
    return {
        "countries": [
            {
                "code": "SCH",
                "name": "Schengen Area",
                "countries": ["France", "Germany", "Italy", "Spain", "Netherlands", "Belgium", "Austria", "Portugal", "Greece", "Sweden", "Denmark", "Finland", "Norway", "Iceland", "Switzerland"],
                "visa_required": True
            },
            {
                "code": "CHN",
                "name": "China",
                "visa_required": True
            },
            {
                "code": "THA",
                "name": "Thailand",
                "visa_required": True
            },
            {
                "code": "MYS",
                "name": "Malaysia",
                "visa_required": True
            },
            {
                "code": "SGP",
                "name": "Singapore",
                "visa_required": True
            }
        ]
    }


@app.get("/api/countries/{country_code}/requirements")
async def get_country_requirements(country_code: str):
    """Get specific document requirements for a country"""
    requirements = rule_engine.get_requirements(country_code)
    if not requirements:
        raise HTTPException(status_code=404, detail="Country not found")
    return requirements


@app.post("/api/applications", response_model=VisaApplication)
async def create_application(
    application_data: ApplicationCreate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new visa application"""
    try:
        # Validate country requirements
        requirements = rule_engine.get_requirements(application_data.destination_country)
        
        application = VisaApplication(
            user_id=current_user.id,
            destination_country=application_data.destination_country,
            visa_type=application_data.visa_type,
            status="draft",
            created_at=datetime.utcnow()
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        logger.info(f"Application created: {application.id} for user {current_user.id}")
        return application
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating application: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create application")


@app.get("/api/applications")
async def list_applications(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """List all applications for current user"""
    applications = db.query(VisaApplication).filter(
        VisaApplication.user_id == current_user.id
    ).all()
    return {"applications": applications}


@app.get("/api/applications/{application_id}")
async def get_application(
    application_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific application details"""
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id,
        VisaApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return application


@app.post("/api/applications/{application_id}/documents")
async def upload_document(
    application_id: int,
    document_data: DocumentUpload,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document for an application"""
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id,
        VisaApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Process uploaded document
    try:
        extracted_data = await doc_processor.process_document(
            document_data.file_path,
            document_data.document_type
        )
        
        document = Document(
            application_id=application_id,
            document_type=document_data.document_type,
            file_path=document_data.file_path,
            extracted_data=extracted_data,
            status="processed"
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Check if all required documents are now present
        missing_docs = rule_engine.check_missing_documents(
            application.destination_country,
            db.query(Document).filter(Document.application_id == application_id).all()
        )
        
        if not missing_docs:
            application.status = "ready_for_review"
            db.commit()
        
        logger.info(f"Document uploaded: {document.id} for application {application_id}")
        return {
            "document": document,
            "missing_documents": missing_docs,
            "application_status": application.status
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process document")


@app.get("/api/applications/{application_id}/documents")
async def list_documents(
    application_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents for an application"""
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id,
        VisaApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    documents = db.query(Document).filter(
        Document.application_id == application_id
    ).all()
    
    return {"documents": documents}


@app.get("/api/applications/{application_id}/validation")
async def validate_application(
    application_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Validate application completeness and identify missing documents"""
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id,
        VisaApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    documents = db.query(Document).filter(
        Document.application_id == application_id
    ).all()
    
    # Get required documents for destination country
    requirements = rule_engine.get_requirements(application.destination_country)
    
    # Check for missing documents
    missing_docs = rule_engine.check_missing_documents(
        application.destination_country,
        documents
    )
    
    # Validate extracted data consistency
    validation_errors = rule_engine.validate_data_consistency(documents)
    
    is_complete = len(missing_docs) == 0 and len(validation_errors) == 0
    
    return {
        "application_id": application_id,
        "is_complete": is_complete,
        "missing_documents": missing_docs,
        "validation_errors": validation_errors,
        "status": "ready_for_review" if is_complete else "incomplete"
    }


@app.post("/api/applications/{application_id}/submit-for-review")
async def submit_for_review(
    application_id: int,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Submit application for human agent review"""
    application = db.query(VisaApplication).filter(
        VisaApplication.id == application_id,
        VisaApplication.user_id == current_user.id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Validate application is complete
    documents = db.query(Document).filter(
        Document.application_id == application_id
    ).all()
    
    missing_docs = rule_engine.check_missing_documents(
        application.destination_country,
        documents
    )
    
    if missing_docs:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required documents: {', '.join(missing_docs)}"
        )
    
    # Update application status
    application.status = "pending_agent_review"
    application.submitted_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Application {application_id} submitted for agent review")
    
    return {
        "message": "Application submitted for agent review",
        "application_id": application_id,
        "status": application.status,
        "submitted_at": application.submitted_at
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
