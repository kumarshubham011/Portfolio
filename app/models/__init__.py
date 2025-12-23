"""
=============================================================================
MODELS PACKAGE
=============================================================================
Purpose: SQLAlchemy ORM models representing database tables.

This package contains:
- User: Admin authentication
- Post: Blog posts with markdown content
- Project: Portfolio projects

Each model maps to a database table. SQLAlchemy handles:
- Creating the table structure
- Converting Python objects to SQL rows
- Converting SQL rows back to Python objects

Import models from here for convenience:
    from app.models import User, Post, Project
=============================================================================
"""

from app.models.user import User
from app.models.post import Post
from app.models.project import Project

# Export all models for easy importing
__all__ = ["User", "Post", "Project"]
