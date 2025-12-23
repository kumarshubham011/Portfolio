"""
=============================================================================
ADMIN ROUTES
=============================================================================
Purpose: Protected routes for content management (CRUD).

All routes in this file require authentication.
The get_current_user dependency enforces this.

Routes:
- GET  /admin                → Dashboard
- GET  /admin/posts/new      → New post form
- POST /admin/posts          → Create post
- GET  /admin/posts/{id}/edit → Edit post form
- POST /admin/posts/{id}     → Update post
- POST /admin/posts/{id}/delete → Delete post
- Similar routes for projects

CRUD = Create, Read, Update, Delete
- Create: POST /admin/posts
- Read: GET /admin (list), GET /admin/posts/{id}/edit (single)
- Update: POST /admin/posts/{id}
- Delete: POST /admin/posts/{id}/delete
=============================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from slugify import slugify

from app.database import get_db
from app.models import User, Post, Project
from app.services.auth import get_current_user
from app.services.markdown import render_markdown
from app.config import settings


router = APIRouter(prefix="/admin", tags=["admin"])


# =============================================================================
# HELPER: ADMIN CONTEXT
# =============================================================================

def get_admin_context(request: Request, user: User) -> dict:
    """Build base context for admin pages."""
    return {
        "request": request,
        "user": user,
        "site_name": settings.SITE_NAME,
        "render_markdown": render_markdown,
    }


# =============================================================================
# DASHBOARD
# =============================================================================

@router.get("", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)  # Requires auth!
):
    """
    Admin dashboard: Overview of all content.
    
    Shows:
    - Total posts (published/drafts)
    - Total projects
    - Quick links to create new content
    """
    # Get counts
    total_posts = db.query(Post).count()
    published_posts = db.query(Post).filter(Post.published == True).count()
    total_projects = db.query(Project).count()
    
    # Get recent posts
    recent_posts = (
        db.query(Post)
        .order_by(Post.updated_at.desc())
        .limit(5)
        .all()
    )
    
    # Get all projects
    all_projects = (
        db.query(Project)
        .order_by(Project.order)
        .all()
    )
    
    context = get_admin_context(request, user)
    context.update({
        "total_posts": total_posts,
        "published_posts": published_posts,
        "draft_posts": total_posts - published_posts,
        "total_projects": total_projects,
        "recent_posts": recent_posts,
        "projects": all_projects,
    })
    
    templates = request.app.state.templates
    return templates.TemplateResponse("pages/admin/dashboard.html", context)


# =============================================================================
# POST CRUD
# =============================================================================

@router.get("/posts/new", response_class=HTMLResponse)
async def new_post_form(
    request: Request,
    user: User = Depends(get_current_user)
):
    """Display form to create a new post."""
    context = get_admin_context(request, user)
    context["post"] = None  # No existing post
    context["action"] = "Create"
    context["item_type"] = "post"
    
    templates = request.app.state.templates
    return templates.TemplateResponse("pages/admin/editor.html", context)


@router.post("/posts", response_class=HTMLResponse)
async def create_post(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Create a new blog post.
    
    Reads form data and creates a new Post in the database.
    Redirects to edit page on success.
    """
    form = await request.form()
    
    # Extract form fields
    title = form.get("title", "").strip()
    content = form.get("content", "").strip()
    excerpt = form.get("excerpt", "").strip() or None
    published = form.get("published") == "on"
    
    # Validate
    if not title or not content:
        context = get_admin_context(request, user)
        context.update({
            "post": None,
            "action": "Create",
            "item_type": "post",
            "error": "Title and content are required",
        })
        templates = request.app.state.templates
        return templates.TemplateResponse("pages/admin/editor.html", context)
    
    # Generate slug
    slug = slugify(title)
    
    # Check for duplicate slug
    existing = db.query(Post).filter(Post.slug == slug).first()
    if existing:
        counter = 1
        while db.query(Post).filter(Post.slug == f"{slug}-{counter}").first():
            counter += 1
        slug = f"{slug}-{counter}"
    
    # Create post
    post = Post(
        title=title,
        slug=slug,
        content=content,
        excerpt=excerpt,
        published=published,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return RedirectResponse(
        url=f"/admin/posts/{post.id}/edit?saved=1",
        status_code=status.HTTP_302_FOUND
    )


@router.get("/posts/{post_id}/edit", response_class=HTMLResponse)
async def edit_post_form(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Display form to edit an existing post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    context = get_admin_context(request, user)
    context.update({
        "post": post,
        "action": "Update",
        "item_type": "post",
        "success": request.query_params.get("saved") == "1",
    })
    
    templates = request.app.state.templates
    return templates.TemplateResponse("pages/admin/editor.html", context)


@router.post("/posts/{post_id}", response_class=HTMLResponse)
async def update_post(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update an existing blog post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    form = await request.form()
    
    # Update fields
    post.title = form.get("title", post.title).strip()
    post.content = form.get("content", post.content).strip()
    post.excerpt = form.get("excerpt", "").strip() or None
    post.published = form.get("published") == "on"
    
    # Update slug if title changed
    new_slug = slugify(post.title)
    if new_slug != post.slug:
        # Check for conflicts
        existing = db.query(Post).filter(
            Post.slug == new_slug,
            Post.id != post.id
        ).first()
        if not existing:
            post.slug = new_slug
    
    db.commit()
    
    return RedirectResponse(
        url=f"/admin/posts/{post.id}/edit?saved=1",
        status_code=status.HTTP_302_FOUND
    )


@router.post("/posts/{post_id}/delete")
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete a blog post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    db.delete(post)
    db.commit()
    
    return RedirectResponse(
        url="/admin",
        status_code=status.HTTP_302_FOUND
    )


# =============================================================================
# PROJECT CRUD
# =============================================================================

@router.get("/projects/new", response_class=HTMLResponse)
async def new_project_form(
    request: Request,
    user: User = Depends(get_current_user)
):
    """Display form to create a new project."""
    context = get_admin_context(request, user)
    context["project"] = None
    context["action"] = "Create"
    context["item_type"] = "project"
    
    templates = request.app.state.templates
    return templates.TemplateResponse("pages/admin/project_editor.html", context)


@router.post("/projects", response_class=HTMLResponse)
async def create_project(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a new project."""
    form = await request.form()
    
    # Extract form fields
    title = form.get("title", "").strip()
    description = form.get("description", "").strip()
    tech_stack = form.get("tech_stack", "").strip()
    url = form.get("url", "").strip() or None
    github_url = form.get("github_url", "").strip() or None
    image_url = form.get("image_url", "").strip() or None
    featured = form.get("featured") == "on"
    order = int(form.get("order", 0) or 0)
    
    # Validate
    if not title or not description or not tech_stack:
        context = get_admin_context(request, user)
        context.update({
            "project": None,
            "action": "Create",
            "item_type": "project",
            "error": "Title, description, and tech stack are required",
        })
        templates = request.app.state.templates
        return templates.TemplateResponse("pages/admin/project_editor.html", context)
    
    # Create project
    project = Project(
        title=title,
        description=description,
        tech_stack=tech_stack,
        url=url,
        github_url=github_url,
        image_url=image_url,
        featured=featured,
        order=order,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return RedirectResponse(
        url=f"/admin/projects/{project.id}/edit?saved=1",
        status_code=status.HTTP_302_FOUND
    )


@router.get("/projects/{project_id}/edit", response_class=HTMLResponse)
async def edit_project_form(
    request: Request,
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Display form to edit an existing project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    context = get_admin_context(request, user)
    context.update({
        "project": project,
        "action": "Update",
        "item_type": "project",
        "success": request.query_params.get("saved") == "1",
    })
    
    templates = request.app.state.templates
    return templates.TemplateResponse("pages/admin/project_editor.html", context)


@router.post("/projects/{project_id}", response_class=HTMLResponse)
async def update_project(
    request: Request,
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update an existing project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    form = await request.form()
    
    # Update fields
    project.title = form.get("title", project.title).strip()
    project.description = form.get("description", project.description).strip()
    project.tech_stack = form.get("tech_stack", project.tech_stack).strip()
    project.url = form.get("url", "").strip() or None
    project.github_url = form.get("github_url", "").strip() or None
    project.image_url = form.get("image_url", "").strip() or None
    project.featured = form.get("featured") == "on"
    project.order = int(form.get("order", 0) or 0)
    
    db.commit()
    
    return RedirectResponse(
        url=f"/admin/projects/{project.id}/edit?saved=1",
        status_code=status.HTTP_302_FOUND
    )


@router.post("/projects/{project_id}/delete")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db.delete(project)
    db.commit()
    
    return RedirectResponse(
        url="/admin",
        status_code=status.HTTP_302_FOUND
    )
