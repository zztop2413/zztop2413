"""
Celery task definitions for background processing
"""

from celery import Celery
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery application
celery_app = Celery(
    'visa_application_system',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['backend.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)


@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: int, file_path: str, document_type: str):
    """
    Background task for processing uploaded documents
    
    Args:
        document_id: Database ID of the document
        file_path: Path to the uploaded file
        document_type: Type of document
    """
    try:
        from backend.services.document_processor import DocumentProcessor
        from backend.database.session import get_db_session
        from backend.models import Document
        
        processor = DocumentProcessor()
        
        # Process document
        result = processor.process_document(file_path, document_type)
        
        # Update database with results
        db = get_db_session()
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.extracted_data = result.get('extracted_data', {})
                document.ocr_confidence = result.get('ocr_confidence', 0)
                document.status = 'processed' if result.get('success') else 'failed'
                document.validation_errors = result.get('errors', [])
                db.commit()
                logger.info(f"Document {document_id} processed successfully")
        finally:
            db.close()
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task(bind=True, max_retries=3)
def send_email_notification(self, user_email: str, subject: str, body: str):
    """
    Send email notification to user
    
    Args:
        user_email: Recipient email address
        subject: Email subject
        body: Email body content
    """
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = user_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent to {user_email}")
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@celery_app.task
def cleanup_old_documents():
    """
    Scheduled task to clean up old documents based on retention policy
    Runs daily
    """
    from backend.database.session import get_db_session
    from backend.models import Document, VisaApplication
    from datetime import datetime, timedelta
    
    db = get_db_session()
    try:
        # Get applications older than retention period
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        old_applications = db.query(VisaApplication).filter(
            VisaApplication.created_at < cutoff_date
        ).all()
        
        deleted_count = 0
        for app in old_applications:
            # Delete associated documents
            documents = db.query(Document).filter(
                Document.application_id == app.id
            ).all()
            
            for doc in documents:
                # Delete file from storage (implement based on storage backend)
                # os.remove(doc.file_path)
                db.delete(doc)
                deleted_count += 1
            
            # Delete application
            db.delete(app)
        
        db.commit()
        logger.info(f"Cleaned up {deleted_count} old documents")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        db.rollback()
    finally:
        db.close()


@celery_app.task
def validate_application_completeness(application_id: int):
    """
    Validate if an application has all required documents
    
    Args:
        application_id: ID of the application to validate
    """
    from backend.database.session import get_db_session
    from backend.models import VisaApplication, Document
    from backend.services.country_rules import CountryRuleEngine
    
    db = get_db_session()
    try:
        application = db.query(VisaApplication).filter(
            VisaApplication.id == application_id
        ).first()
        
        if not application:
            logger.warning(f"Application {application_id} not found")
            return
        
        documents = db.query(Document).filter(
            Document.application_id == application_id
        ).all()
        
        rule_engine = CountryRuleEngine()
        missing_docs = rule_engine.check_missing_documents(
            application.destination_country,
            documents
        )
        
        if not missing_docs:
            application.status = 'ready_for_review'
            db.commit()
            logger.info(f"Application {application_id} is now complete")
            
            # Send notification to user
            from backend.models import User
            user = db.query(User).filter(User.id == application.user_id).first()
            if user:
                send_email_notification.delay(
                    user.email,
                    "Application Complete",
                    f"Your visa application for {application.destination_country} is complete and ready for review."
                )
        else:
            logger.info(f"Application {application_id} still missing: {missing_docs}")
            
    except Exception as e:
        logger.error(f"Error validating application: {str(e)}")
        db.rollback()
    finally:
        db.close()


# Celery Beat schedule configuration
celery_app.conf.beat_schedule = {
    'cleanup-old-documents-daily': {
        'task': 'backend.tasks.cleanup_old_documents',
        'schedule': 86400.0,  # Run every 24 hours
    },
}
