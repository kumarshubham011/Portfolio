"""
=============================================================================
POST MODEL
=============================================================================
Purpose: Represents a blog post with markdown content.

Blog posts are the core content of the "Learnings" section.
They support:
- Markdown formatting for rich content
- Draft/published states
- SEO-friendly URL slugs
- Timestamps for sorting

CRUD Permissions:
- CREATE: Admin only
- READ: Public (if published)
- UPDATE: Admin only
- DELETE: Admin only
=============================================================================
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime

from app.database import Base


class Post(Base):
    """
    Blog post model with markdown support.
    
    Posts can be drafts (unpublished) or published.
    Only published posts are visible to the public.
    
    Attributes:
        id: Unique identifier
        title: Post title (displayed in listings and detail)
        slug: URL-friendly identifier (e.g., "my-first-post")
        content: Full markdown content
        excerpt: Short preview text for listings
        published: Whether the post is publicly visible
        created_at: Original creation time
        updated_at: Last modification time
    
    Example:
        post = Post(
            title="Learning FastAPI",
            slug="learning-fastapi",
            content="# Introduction\n\nFastAPI is amazing...",
            excerpt="A beginner's journey into modern Python APIs",
            published=True
        )
    """
    
    __tablename__ = "posts"
    
    # -------------------------------------------------------------------------
    # Columns
    # -------------------------------------------------------------------------
    
    # Primary Key
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="Unique post identifier"
    )
    
    # Post title
    # Displayed prominently in the UI
    title = Column(
        String(200), 
        nullable=False,
        comment="Post title"
    )
    
    # URL-friendly slug
    # Example: "My First Post" -> "my-first-post"
    # - unique=True: No duplicate URLs
    # - index=True: Fast lookups by URL
    slug = Column(
        String(200), 
        unique=True, 
        index=True, 
        nullable=False,
        comment="URL-friendly identifier"
    )
    
    # Full markdown content
    # Text type allows unlimited length (unlike String)
    content = Column(
        Text, 
        nullable=False,
        comment="Full post content in Markdown format"
    )
    
    # Short preview text
    # Shown in post listings (blog index page)
    # If not provided, we can auto-generate from content
    excerpt = Column(
        String(500), 
        nullable=True,
        comment="Short preview text for listings"
    )
    
    # Publication status
    # False = draft (only visible to admin)
    # True = published (visible to everyone)
    published = Column(
        Boolean, 
        default=False, 
        nullable=False,
        comment="Is this post publicly visible?"
    )
    
    # Creation timestamp
    # Set automatically when post is created
    created_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False,
        comment="When the post was first created"
    )
    
    # Last update timestamp
    # Updated automatically when post is modified
    # onupdate=datetime.utcnow handles this automatically
    updated_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False,
        comment="When the post was last modified"
    )
    
    # -------------------------------------------------------------------------
    # String Representation
    # -------------------------------------------------------------------------
    
    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        status = "published" if self.published else "draft"
        return f"<Post(id={self.id}, slug='{self.slug}', {status})>"
    
    # -------------------------------------------------------------------------
    # Computed Properties
    # -------------------------------------------------------------------------
    
    @property
    def preview(self) -> str:
        """
        Get preview text for listings.
        
        Returns excerpt if available, otherwise truncates content.
        
        Returns:
            str: Preview text (max 200 characters)
        """
        if self.excerpt:
            return self.excerpt
        
        # Strip markdown and truncate content
        # This is a simple approach; could be enhanced
        text = self.content.replace("#", "").replace("*", "").strip()
        if len(text) > 200:
            return text[:197] + "..."
        return text
