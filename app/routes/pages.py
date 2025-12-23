"""
=============================================================================
PUBLIC PAGES ROUTES
=============================================================================
Purpose: Handle all public-facing page routes.

These routes:
- Render HTML pages using Jinja2 templates
- Are accessible without authentication
- Display portfolio content to visitors

Routes:
- GET /          → Home page
- GET /about     → About page
- GET /projects  → Projects listing
- GET /blog      → Blog listing
- GET /blog/{slug} → Single post
- GET /contact   → Contact page
=============================================================================
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Post, Project, User
from app.services.auth import get_current_user_optional
from app.services.markdown import render_markdown, estimate_reading_time
from app.config import settings


# Create router with prefix for these routes
router = APIRouter(tags=["pages"])


# =============================================================================
# HELPER: GET TEMPLATE CONTEXT
# =============================================================================

def get_base_context(request: Request, user: Optional[User] = None) -> dict:
    """
    Build the base context for all templates.
    
    This context is passed to every template and includes:
    - Site configuration (name, tagline, social links)
    - Current request info
    - Authentication status
    
    Args:
        request: FastAPI request object
        user: Current user (if authenticated)
    
    Returns:
        dict: Context for template rendering
    """
    return {
        "request": request,  # Required by Jinja2 for url_for, etc.
        "user": user,        # Current user or None
        
        # Site configuration
        "site_name": settings.SITE_NAME,
        "site_tagline": settings.SITE_TAGLINE,
        "github_url": settings.GITHUB_URL,
        "linkedin_url": settings.LINKEDIN_URL,
        "leetcode_url": settings.LEETCODE_URL,
        "email": settings.EMAIL,
        "current_company": settings.CURRENT_COMPANY,
        "company_url": settings.COMPANY_URL,
        
        # Helper functions for templates
        "render_markdown": render_markdown,
        "estimate_reading_time": estimate_reading_time,
    }


# =============================================================================
# HOME PAGE
# =============================================================================

@router.get("/", response_class=HTMLResponse)
async def home(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Home page: Minimal intro with featured projects.
    
    Shows:
    - Welcome message and tagline
    - Featured projects (if any)
    - Recent blog posts (if any)
    """
    # Get featured projects
    featured_projects = (
        db.query(Project)
        .filter(Project.featured == True)
        .order_by(Project.order)
        .limit(3)
        .all()
    )
    
    # Get recent published posts
    recent_posts = (
        db.query(Post)
        .filter(Post.published == True)
        .order_by(Post.created_at.desc())
        .limit(3)
        .all()
    )
    
    # Build context
    context = get_base_context(request, user)
    context.update({
        "featured_projects": featured_projects,
        "recent_posts": recent_posts,
    })
    
    # Get templates from app state
    templates = request.app.state.templates
    return templates.TemplateResponse("pages/home.html", context)


# =============================================================================
# ABOUT PAGE
# =============================================================================

@router.get("/about", response_class=HTMLResponse)
async def about(
    request: Request,
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    About page: Personal info, interests, and current role.
    
    This is a static page - content comes from the template.
    For dynamic content, you could add an "About" model to the database.
    """
    context = get_base_context(request, user)
    
    templates = request.app.state.templates
    return templates.TemplateResponse("pages/about.html", context)


# =============================================================================
# PROJECTS PAGE
# =============================================================================

@router.get("/projects", response_class=HTMLResponse)
async def projects(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Projects page: List all portfolio projects.
    
    Projects are ordered by their 'order' field (manual sorting).
    Featured projects are highlighted.
    """
    # Get all projects, ordered
    all_projects = (
        db.query(Project)
        .order_by(Project.order, Project.created_at.desc())
        .all()
    )
    
    context = get_base_context(request, user)
    context["projects"] = all_projects
    
    templates = request.app.state.templates
    return templates.TemplateResponse("pages/projects.html", context)


# =============================================================================
# BLOG PAGES
# =============================================================================

@router.get("/blog", response_class=HTMLResponse)
async def blog_index(
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Blog index: List all published posts.
    
    Shows posts in reverse chronological order (newest first).
    Only published posts are visible to public.
    Admin sees all posts including drafts.
    """
    # Query posts
    query = db.query(Post).order_by(Post.created_at.desc())
    
    # If admin, show all; otherwise only published
    if user is None:
        query = query.filter(Post.published == True)
    
    posts = query.all()
    
    context = get_base_context(request, user)
    context["posts"] = posts
    
    templates = request.app.state.templates
    return templates.TemplateResponse("pages/blog.html", context)


@router.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post(
    request: Request,
    slug: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Single blog post page.
    
    Finds post by slug (URL-friendly identifier).
    Only published posts visible to public.
    Admin can view drafts.
    
    Args:
        slug: URL slug of the post (e.g., "my-first-post")
    """
    # Query by slug
    query = db.query(Post).filter(Post.slug == slug)
    
    # If not admin, only allow published posts
    if user is None:
        query = query.filter(Post.published == True)
    
    post = query.first()
    
    # 404 if not found
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    context = get_base_context(request, user)
    context["post"] = post
    
    templates = request.app.state.templates
    return templates.TemplateResponse("pages/post.html", context)


# =============================================================================
# CONTACT PAGE
# =============================================================================

@router.get("/contact", response_class=HTMLResponse)
async def contact(
    request: Request,
    user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Contact page: Social links and ways to reach you.
    
    Static page - links come from settings/environment.
    """
    context = get_base_context(request, user)
    
    templates = request.app.state.templates
    return templates.TemplateResponse("pages/contact.html", context)
