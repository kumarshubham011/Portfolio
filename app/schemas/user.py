"""
=============================================================================
USER SCHEMAS
=============================================================================
Purpose: Pydantic schemas for user authentication.

These schemas handle:
- Login form data
- JWT tokens
- User response data

Security Note:
We NEVER return the password hash in responses.
The UserResponse schema explicitly excludes it.
=============================================================================
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """
    Schema for creating a new user (admin registration).
    
    Note: This is only used internally for initial setup.
    There's no public registration endpoint.
    
    Attributes:
        username: Desired username
        password: Plain text password (will be hashed)
    """
    
    username: str = Field(
        ...,  # Required field
        min_length=3,
        max_length=50,
        description="Username for login"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (will be hashed, never stored as plain text)"
    )


class UserResponse(BaseModel):
    """
    Schema for returning user data in responses.
    
    SECURITY: This explicitly excludes the password hash.
    Never expose sensitive data in API responses!
    
    Attributes:
        id: User ID
        username: Username
        created_at: Account creation time
    """
    
    id: int
    username: str
    created_at: datetime
    
    # Pydantic V2 configuration
    model_config = {
        # Allow creating from ORM objects (SQLAlchemy models)
        "from_attributes": True
    }


class Token(BaseModel):
    """
    Schema for JWT token response.
    
    Returned after successful login.
    
    Attributes:
        access_token: The JWT string
        token_type: Always "bearer" for our setup
    """
    
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Schema for data encoded in the JWT.
    
    This is what we put INSIDE the token.
    Used to identify the user on subsequent requests.
    
    Attributes:
        username: The logged-in user's username
    """
    
    username: Optional[str] = None


class LoginForm(BaseModel):
    """
    Schema for login form submission.
    
    Attributes:
        username: User's username
        password: User's password (plain text for comparison)
    """
    
    username: str = Field(..., description="Your username")
    password: str = Field(..., description="Your password")
