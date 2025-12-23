"""
=============================================================================
AUTHENTICATION SERVICE
=============================================================================
Purpose: Handle all authentication logic for the admin user.

This module provides:
- Password hashing and verification (bcrypt)
- JWT token creation and validation
- FastAPI dependencies for protected routes

Security Features:
- bcrypt for password hashing (slow, resistant to brute force)
- JWT for stateless authentication
- HTTP-only cookies (prevents XSS attacks)
- Token expiration (limits damage if leaked)

Flow:
1. Admin logs in with username/password
2. Server validates credentials
3. Server creates JWT and sets HTTP-only cookie
4. Subsequent requests include cookie automatically
5. Server validates JWT on protected routes
=============================================================================
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenData


# =============================================================================
# PASSWORD HASHING
# =============================================================================

# Configure password hashing
# bcrypt is the recommended algorithm for password hashing:
# - Automatically handles salt generation
# - Deliberately slow (prevents brute force)
# - Configurable work factor (adjustable security)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hash.
    
    bcrypt handles:
    - Extracting the salt from the hash
    - Hashing the plain password with that salt
    - Comparing the results
    
    Args:
        plain_password: The password attempt
        hashed_password: The stored hash
    
    Returns:
        bool: True if password matches, False otherwise
    
    Example:
        if verify_password("secret123", user.hashed_password):
            print("Password correct!")
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storage.
    
    Creates a bcrypt hash with automatic salt.
    The salt is embedded in the hash string.
    
    Args:
        password: Plain text password
    
    Returns:
        str: bcrypt hash (60 characters)
    
    Example:
        hashed = get_password_hash("secret123")
        # Store hashed in database, NEVER the plain password
    """
    return pwd_context.hash(password)


# =============================================================================
# JWT TOKEN HANDLING
# =============================================================================

# Security scheme for Swagger UI (optional, for testing)
security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    JWTs are self-contained tokens that include:
    - The user identity (payload)
    - Expiration time
    - Cryptographic signature
    
    The signature ensures the token hasn't been tampered with.
    
    Args:
        data: Payload to encode (usually {"sub": username})
        expires_delta: Custom expiration time (optional)
    
    Returns:
        str: Encoded JWT string
    
    Example:
        token = create_access_token(data={"sub": "admin"})
    """
    # Copy the data so we don't modify the original
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Add expiration to payload
    to_encode.update({"exp": expire})
    
    # Create the token
    # HS256 = HMAC with SHA-256 (symmetric encryption)
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT token.
    
    Checks:
    - Token signature is valid (not tampered)
    - Token hasn't expired
    - Required fields are present
    
    Args:
        token: JWT string to decode
    
    Returns:
        TokenData: Decoded payload, or None if invalid
    
    Example:
        token_data = decode_token(token)
        if token_data:
            print(f"User: {token_data.username}")
    """
    try:
        # Decode the token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract username from "sub" (subject) claim
        username: str = payload.get("sub")
        if username is None:
            return None
        
        return TokenData(username=username)
        
    except JWTError:
        # Token is invalid (expired, bad signature, etc.)
        return None


# =============================================================================
# FASTAPI DEPENDENCIES
# =============================================================================

# Cookie name for storing the JWT
COOKIE_NAME = "portfolio_auth"


def get_token_from_cookie(request: Request) -> Optional[str]:
    """
    Extract JWT from HTTP-only cookie.
    
    We use cookies instead of Authorization header because:
    - Cookies are sent automatically by browsers
    - HTTP-only cookies can't be accessed by JavaScript (XSS protection)
    - No client-side token management needed
    
    Args:
        request: FastAPI request object
    
    Returns:
        str: JWT token, or None if not found
    """
    return request.cookies.get(COOKIE_NAME)


def set_auth_cookie(response: Response, token: str) -> None:
    """
    Set the authentication cookie on a response.
    
    Cookie settings:
    - httponly: Not accessible via JavaScript
    - secure: Only sent over HTTPS (disabled in dev)
    - samesite: Prevents CSRF attacks
    - max_age: Cookie expiration in seconds
    
    Args:
        response: FastAPI response object
        token: JWT to store
    """
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,  # Can't be read by JavaScript
        secure=not settings.DEBUG,  # HTTPS only in production
        samesite="lax",  # CSRF protection
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Seconds
    )


def clear_auth_cookie(response: Response) -> None:
    """
    Remove the authentication cookie (logout).
    
    Args:
        response: FastAPI response object
    """
    response.delete_cookie(key=COOKIE_NAME)


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    FastAPI dependency: Get the current authenticated user.
    
    Use this to protect routes that require authentication.
    If not authenticated, raises 401 Unauthorized.
    
    Args:
        request: FastAPI request (for cookie access)
        db: Database session
    
    Returns:
        User: The authenticated user object
    
    Raises:
        HTTPException: 401 if not authenticated
    
    Usage:
        @app.get("/admin")
        def admin_page(user: User = Depends(get_current_user)):
            return f"Hello, {user.username}!"
    """
    # Get token from cookie
    token = get_token_from_cookie(request)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Decode and validate token
    token_data = decode_token(token)
    if token_data is None or token_data.username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    FastAPI dependency: Get current user if authenticated, else None.
    
    Use this for pages that work both logged in and logged out,
    but show different content based on authentication status.
    
    Args:
        request: FastAPI request
        db: Database session
    
    Returns:
        User if authenticated, None otherwise
    
    Usage:
        @app.get("/")
        def home(user: Optional[User] = Depends(get_current_user_optional)):
            if user:
                return f"Welcome back, {user.username}!"
            return "Welcome, guest!"
    """
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None


# =============================================================================
# USER AUTHENTICATION
# =============================================================================

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username and password.
    
    This is the main login function:
    1. Find user by username
    2. Verify password against stored hash
    3. Return user if valid, None otherwise
    
    Args:
        db: Database session
        username: Login username
        password: Login password (plain text)
    
    Returns:
        User if credentials valid, None otherwise
    
    Example:
        user = authenticate_user(db, "admin", "secret123")
        if user:
            token = create_access_token(data={"sub": user.username})
    """
    # Find user by username
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        # User doesn't exist
        return None
    
    if not verify_password(password, user.hashed_password):
        # Password doesn't match
        return None
    
    return user
