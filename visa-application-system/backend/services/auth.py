"""
Authentication service with JWT token management
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import logging

from backend.models import User
from config.settings import settings

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication service handling user registration, login, and JWT tokens
    """
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_user(self, db: Session, user_data) -> User:
        """
        Create a new user
        
        Args:
            db: Database session
            user_data: UserCreate schema with user details
            
        Returns:
            Created User object
            
        Raises:
            ValueError: If email already exists
        """
        # Check if user already exists
        existing_user = db.query(User).filter(
            User.email == user_data.email
        ).first()
        
        if existing_user:
            raise ValueError("Email already registered")
        
        # Hash password
        hashed_password = self.hash_password(user_data.password)
        
        # Create new user
        user = User(
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            nationality=user_data.nationality,
            is_verified=False,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User created successfully: {user.email}")
        return user
    
    def authenticate_user(
        self, 
        db: Session, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """
        Authenticate user with email and password
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.warning(f"Authentication failed - user not found: {email}")
            return None
        
        if not self.verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed - invalid password: {email}")
            return None
        
        if not user.is_active:
            logger.warning(f"Authentication failed - inactive user: {email}")
            return None
        
        logger.info(f"User authenticated successfully: {email}")
        return user
    
    def create_access_token(self, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token
        
        Args:
            user_id: User ID to encode in token
            expires_delta: Optional custom expiration time
            
        Returns:
            JWT token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Access token created for user {user_id}")
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[int]:
        """
        Verify JWT token and extract user ID
        
        Args:
            token: JWT token string
            
        Returns:
            User ID if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                logger.warning("Token validation failed - no subject")
                return None
            
            logger.info(f"Token validated successfully for user {user_id}")
            return int(user_id)
            
        except JWTError as e:
            logger.error(f"Token validation failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {str(e)}")
            return None
    
    async def get_current_user(self, token: str, db: Session) -> User:
        """
        Get current user from JWT token
        
        Args:
            token: JWT token from Authorization header
            db: Database session
            
        Returns:
            User object
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        from fastapi import HTTPException, status
        
        user_id = self.verify_token(token)
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        
        return user
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_refresh_token(self, user_id: int) -> str:
        """
        Create refresh token for long-lived sessions
        
        Args:
            user_id: User ID
            
        Returns:
            Refresh token string
        """
        expire = datetime.utcnow() + timedelta(days=30)
        
        to_encode = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_refresh_token(self, token: str) -> Optional[int]:
        """
        Verify refresh token
        
        Args:
            token: Refresh token string
            
        Returns:
            User ID if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            token_type = payload.get("type")
            
            if token_type != "refresh":
                logger.warning("Invalid token type for refresh")
                return None
            
            user_id: str = payload.get("sub")
            return int(user_id) if user_id else None
            
        except JWTError:
            logger.error("Refresh token validation failed")
            return None
