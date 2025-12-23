"""
=============================================================================
SCHEMAS PACKAGE
=============================================================================
Purpose: Pydantic schemas for request/response validation.

Schemas define the structure of data going in and out of the API.
They provide:
- Automatic validation
- Type checking
- Serialization/deserialization
- API documentation

Key difference from Models:
- Models = Database tables (SQLAlchemy)
- Schemas = API data shapes (Pydantic)

We often have multiple schemas per model:
- Create: Fields for creating new records
- Update: Optional fields for partial updates
- Response: Fields to return to clients
=============================================================================
"""

from app.schemas.user import (
    UserCreate,
    UserResponse,
    Token,
    TokenData,
)
from app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostListResponse,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
)

__all__ = [
    "UserCreate",
    "UserResponse",
    "Token",
    "TokenData",
    "PostCreate",
    "PostUpdate",
    "PostResponse",
    "PostListResponse",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
]
