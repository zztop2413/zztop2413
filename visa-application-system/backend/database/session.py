"""
Database session management and connection handling
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from config.settings import settings
from backend.models import Base

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Initialize database by creating all tables
    
    Call this once on application startup
    """
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization complete")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
    
    Yields:
        Database session
        
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get a database session (for use outside of FastAPI dependencies)
    
    Returns:
        Database session
        
    Note: Caller is responsible for closing the session
    """
    return SessionLocal()


def check_database_connection() -> bool:
    """
    Check if database connection is working
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False
