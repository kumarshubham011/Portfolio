"""
=============================================================================
PROJECT SCHEMAS
=============================================================================
Purpose: Pydantic schemas for portfolio project operations.

Similar structure to posts:
- ProjectCreate: Fields for new projects
- ProjectUpdate: Optional fields for updates
- ProjectResponse: What we return to clients
=============================================================================
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, field_validator


class ProjectBase(BaseModel):
    """
    Base schema with common project fields.
    """
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Project name"
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Detailed description in Markdown"
    )
    tech_stack: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Comma-separated list of technologies"
    )


class ProjectCreate(ProjectBase):
    """
    Schema for creating a new project.
    
    Inherits required fields from ProjectBase.
    Adds optional fields for URLs and display settings.
    
    Example:
        data = ProjectCreate(
            title="My App",
            description="# Overview\n\nA cool app...",
            tech_stack="Python, FastAPI, React",
            github_url="https://github.com/me/myapp",
            featured=True
        )
    """
    
    url: Optional[str] = Field(
        None,
        max_length=500,
        description="Live project URL"
    )
    github_url: Optional[str] = Field(
        None,
        max_length=500,
        description="GitHub repository URL"
    )
    image_url: Optional[str] = Field(
        None,
        max_length=500,
        description="Preview image URL"
    )
    featured: bool = Field(
        False,
        description="Show on homepage?"
    )
    order: int = Field(
        0,
        ge=0,
        description="Display order (lower = first)"
    )
    
    @field_validator("url", "github_url", "image_url", mode="before")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """
        Basic URL validation.
        
        Ensures URLs start with http:// or https://.
        Returns None for empty strings.
        """
        if not v:
            return None
        
        v = v.strip()
        if v and not v.startswith(("http://", "https://")):
            # Assume https if no protocol
            return f"https://{v}"
        return v


class ProjectUpdate(BaseModel):
    """
    Schema for updating an existing project.
    
    All fields optional for partial updates.
    """
    
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Project name"
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        description="Description in Markdown"
    )
    tech_stack: Optional[str] = Field(
        None,
        max_length=500,
        description="Technologies used"
    )
    url: Optional[str] = Field(
        None,
        max_length=500,
        description="Live project URL"
    )
    github_url: Optional[str] = Field(
        None,
        max_length=500,
        description="GitHub URL"
    )
    image_url: Optional[str] = Field(
        None,
        max_length=500,
        description="Preview image URL"
    )
    featured: Optional[bool] = Field(
        None,
        description="Show on homepage?"
    )
    order: Optional[int] = Field(
        None,
        ge=0,
        description="Display order"
    )


class ProjectResponse(BaseModel):
    """
    Schema for returning project data to clients.
    
    Includes all fields plus tech_list computed property.
    """
    
    id: int
    title: str
    description: str
    tech_stack: str
    url: Optional[str]
    github_url: Optional[str]
    image_url: Optional[str]
    featured: bool
    order: int
    created_at: datetime
    
    # Computed field: tech stack as a list
    tech_list: List[str] = Field(
        default_factory=list,
        description="Technologies as a list"
    )
    
    model_config = {"from_attributes": True}
    
    @field_validator("tech_list", mode="before")
    @classmethod
    def compute_tech_list(cls, v, info) -> List[str]:
        """
        Compute tech_list from tech_stack string.
        
        This runs when creating the response object.
        """
        # If already a list, return it
        if isinstance(v, list):
            return v
        
        # Try to get tech_stack from the source object
        tech_stack = info.data.get("tech_stack", "")
        if tech_stack:
            return [t.strip() for t in tech_stack.split(",")]
        return []
