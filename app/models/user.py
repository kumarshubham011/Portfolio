"""
=============================================================================
USER MODEL
=============================================================================
Purpose: Represents an admin user who can manage site content.

This is a SINGLE-USER system:
- Only one admin account exists
- No public registration
- Used for authentication to protected routes

Security Notes:
- Passwords are NEVER stored in plain text
- We use bcrypt for one-way hashing
- The hash is computationally expensive to crack
=============================================================================
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base


class User(Base):
    """
    Admin user model for site authentication.
    
    This portfolio only has ONE user - the site owner (you!).
    The user table stores login credentials for the admin panel.
    
    Attributes:
        id: Unique identifier (auto-generated)
        username: Login name (must be unique)
        hashed_password: bcrypt hash of the password
        created_at: When the account was created
    
    Example:
        user = User(
            username="admin",
            hashed_password=get_password_hash("secret123")
        )
        db.add(user)
        db.commit()
    """
    
    # Table name in the database
    # SQLAlchemy converts this to lowercase snake_case by default
    __tablename__ = "users"
    
    # -------------------------------------------------------------------------
    # Columns
    # -------------------------------------------------------------------------
    
    # Primary Key: Unique ID for each user
    # Auto-incrementing integer (1, 2, 3, ...)
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="Unique user identifier"
    )
    
    # Username for login
    # - unique=True: No two users can have the same username
    # - index=True: Fast lookups by username (for login)
    username = Column(
        String(50), 
        unique=True, 
        index=True, 
        nullable=False,
        comment="Unique login username"
    )
    
    # Hashed password
    # NEVER store plain text passwords!
    # bcrypt hashes are 60 characters long
    hashed_password = Column(
        String(128), 
        nullable=False,
        comment="bcrypt hashed password"
    )
    
    # Timestamp when user was created
    # default=datetime.utcnow means it's set automatically on insert
    created_at = Column(
        DateTime, 
        default=datetime.utcnow,
        comment="Account creation timestamp"
    )
    
    # -------------------------------------------------------------------------
    # String Representation
    # -------------------------------------------------------------------------
    
    def __repr__(self) -> str:
        """
        Developer-friendly string representation.
        Used when printing the object (useful for debugging).
        """
        return f"<User(id={self.id}, username='{self.username}')>"
