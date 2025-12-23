"""
=============================================================================
ROUTES PACKAGE
=============================================================================
Purpose: HTTP route handlers organized by concern.

Route files:
- pages.py: Public page routes (home, about, projects, blog, contact)
- auth.py: Authentication routes (login, logout)
- admin.py: Protected admin routes (CRUD operations)
- api.py: JSON API endpoints (if needed)

Each route file creates an APIRouter that's included in main.py.
This organization keeps the main file clean and routes manageable.
=============================================================================
"""

from app.routes.pages import router as pages_router
from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router

__all__ = ["pages_router", "auth_router", "admin_router"]
