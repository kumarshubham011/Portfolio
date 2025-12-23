"""
=============================================================================
SERVICES PACKAGE
=============================================================================
Purpose: Business logic layer between routes and models.

Services contain the "how" of operations:
- Authentication logic (JWT, password hashing)
- Content processing (Markdown rendering)
- Data transformations

Why separate services?
- Keeps routes thin and focused on HTTP handling
- Makes business logic testable in isolation
- Promotes code reuse across routes
=============================================================================
"""

from app.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    get_current_user,
    get_current_user_optional,
)
from app.services.markdown import render_markdown

__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_token",
    "get_current_user",
    "get_current_user_optional",
    "render_markdown",
]
