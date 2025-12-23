"""
=============================================================================
AUTHENTICATION ROUTES
=============================================================================
Purpose: Handle admin login and logout.

Routes:
- GET  /login  → Display login form
- POST /login  → Process login, set cookie, redirect
- GET  /logout → Clear cookie, redirect to home

Security:
- Passwords are never stored in plain text
- JWT tokens expire automatically
- HTTP-only cookies prevent XSS
- CSRF protection via SameSite cookie
=============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth import (
    authenticate_user,
    create_access_token,
    set_auth_cookie,
    clear_auth_cookie,
    get_current_user_optional,
)
from app.models import User
from app.config import settings


router = APIRouter(prefix="/auth", tags=["authentication"])


# =============================================================================
# LOGIN PAGE
# =============================================================================

@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    user: User = Depends(get_current_user_optional)
):
    """
    Display the login form.
    
    If already logged in, redirect to admin dashboard.
    """
    # Already logged in? Go to admin
    if user is not None:
        return RedirectResponse(url="/admin", status_code=status.HTTP_302_FOUND)
    
    # Show login form
    templates = request.app.state.templates
    return templates.TemplateResponse("pages/login.html", {
        "request": request,
        "site_name": settings.SITE_NAME,
        "error": None,  # No error on initial load
    })


@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Process login form submission.
    
    Steps:
    1. Get credentials from form
    2. Validate against database
    3. Create JWT token
    4. Set HTTP-only cookie
    5. Redirect to admin dashboard
    
    If credentials are invalid, re-render login form with error.
    """
    # Get form data
    form = await request.form()
    username = form.get("username", "").strip()
    password = form.get("password", "")
    
    # Validate credentials
    user = authenticate_user(db, username, password)
    
    if not user:
        # Invalid credentials - show error
        templates = request.app.state.templates
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "site_name": settings.SITE_NAME,
                "error": "Invalid username or password",
            },
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    # Create token
    access_token = create_access_token(data={"sub": user.username})
    
    # Create redirect response
    redirect = RedirectResponse(
        url="/admin",
        status_code=status.HTTP_302_FOUND
    )
    
    # Set auth cookie on redirect response
    set_auth_cookie(redirect, access_token)
    
    return redirect


# =============================================================================
# LOGOUT
# =============================================================================

@router.get("/logout")
async def logout(response: Response):
    """
    Log out the current user.
    
    Clears the auth cookie and redirects to home.
    Simple and stateless - no server-side session to invalidate.
    """
    # Create redirect response
    redirect = RedirectResponse(
        url="/",
        status_code=status.HTTP_302_FOUND
    )
    
    # Clear auth cookie
    clear_auth_cookie(redirect)
    
    return redirect
