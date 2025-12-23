"""
=============================================================================
POST SCHEMAS
=============================================================================
Purpose: Pydantic schemas for blog post operations.

We have multiple schemas to handle different scenarios:
- PostCreate: All fields needed for a new post
- PostUpdate: All fields optional (partial updates)
- PostResponse: What we return to clients
- PostListResponse: Lightweight version for listings
=============================================================================
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from slugify import slugify


class PostBase(BaseModel):
    """
    Base schema with common post fields.
    
    Other schemas inherit from this to avoid repetition.
    """
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Post title"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Full post content in Markdown"
    )
    excerpt: Optional[str] = Field(
        None,
        max_length=500,
        description="Short preview text (optional)"
    )
    published: bool = Field(
        False,
        description="Whether post is publicly visible"
    )


class PostCreate(PostBase):
    """
    Schema for creating a new blog post.
    
    Inherits all fields from PostBase.
    Slug is auto-generated from title if not provided.
    
    Example:
        data = PostCreate(
            title="Learning FastAPI",
            content="# Introduction\n\n...",
            published=False
        )
    """
    
    slug: Optional[str] = Field(
        None,
        max_length=200,
        description="URL slug (auto-generated from title if not provided)"
    )
    
    @field_validator("slug", mode="before")
    @classmethod
    def generate_slug(cls, v: Optional[str], info) -> str:
        """
        Generate URL slug from title if not provided.
        
        Uses python-slugify to create clean URLs:
        - "My First Post!" -> "my-first-post"
        - "Learning FastAPI" -> "learning-fastapi"
        
        Args:
            v: Provided slug value (or None)
            info: Validation context (contains other field values)
        
        Returns:
            str: URL-friendly slug
        """
        if v:
            # Clean up provided slug
            return slugify(v)
        
        # Generate from title
        # info.data contains previously validated fields
        title = info.data.get("title", "")
        return slugify(title)


class PostUpdate(BaseModel):
    """
    Schema for updating an existing post.
    
    All fields are optional - only provided fields are updated.
    This is called a "partial update" or "PATCH" pattern.
    
    Example:
        # Update just the title
        data = PostUpdate(title="New Title")
        
        # Update multiple fields
        data = PostUpdate(title="New Title", published=True)
    """
    
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Post title"
    )
    slug: Optional[str] = Field(
        None,
        max_length=200,
        description="URL slug"
    )
    content: Optional[str] = Field(
        None,
        min_length=1,
        description="Post content in Markdown"
    )
    excerpt: Optional[str] = Field(
        None,
        max_length=500,
        description="Short preview text"
    )
    published: Optional[bool] = Field(
        None,
        description="Publication status"
    )
    
    @field_validator("slug", mode="before")
    @classmethod
    def clean_slug(cls, v: Optional[str]) -> Optional[str]:
        """Clean up slug if provided."""
        if v:
            return slugify(v)
        return v


class PostResponse(BaseModel):
    """
    Schema for returning a full post to clients.
    
    Includes all fields plus computed properties.
    Used for single post detail pages.
    """
    
    id: int
    title: str
    slug: str
    content: str
    excerpt: Optional[str]
    published: bool
    created_at: datetime
    updated_at: datetime
    
    # Allow creating from SQLAlchemy models
    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    """
    Lightweight schema for post listings.
    
    Excludes full content (just the excerpt).
    Used for blog index pages to reduce payload size.
    """
    
    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    published: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}
