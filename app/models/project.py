"""
=============================================================================
PROJECT MODEL
=============================================================================
Purpose: Represents a portfolio project to showcase.

Projects highlight your work and skills:
- Technical description (markdown supported)
- Technology stack used
- Links to live demos and source code
- Featured flag for homepage display

CRUD Permissions:
- CREATE: Admin only
- READ: Public (all projects)
- UPDATE: Admin only
- DELETE: Admin only
=============================================================================
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime

from app.database import Base


class Project(Base):
    """
    Portfolio project model.
    
    Showcases technical work with descriptions, tech stacks,
    and links to live demos or repositories.
    
    Attributes:
        id: Unique identifier
        title: Project name
        description: Detailed markdown description
        tech_stack: Technologies used (comma-separated)
        url: Live project URL (optional)
        github_url: Source code repository (optional)
        image_url: Preview image URL (optional)
        featured: Whether to show on homepage
        order: Display order (lower = first)
        created_at: When project was added
    
    Example:
        project = Project(
            title="Portfolio Website",
            description="# Overview\n\nA minimalist portfolio...",
            tech_stack="Python, FastAPI, SQLite, Tailwind CSS",
            url="https://myportfolio.com",
            github_url="https://github.com/me/portfolio",
            featured=True,
            order=1
        )
    """
    
    __tablename__ = "projects"
    
    # -------------------------------------------------------------------------
    # Columns
    # -------------------------------------------------------------------------
    
    # Primary Key
    id = Column(
        Integer, 
        primary_key=True, 
        index=True,
        comment="Unique project identifier"
    )
    
    # Project name
    title = Column(
        String(200), 
        nullable=False,
        comment="Project name"
    )
    
    # Detailed description (markdown)
    # Can include features, challenges, learnings, etc.
    description = Column(
        Text, 
        nullable=False,
        comment="Detailed description in Markdown"
    )
    
    # Technologies used
    # Store as comma-separated string for simplicity
    # Example: "Python, FastAPI, SQLite, Tailwind CSS"
    tech_stack = Column(
        String(500), 
        nullable=False,
        comment="Comma-separated list of technologies"
    )
    
    # Live project URL (optional)
    # Where visitors can see the project in action
    url = Column(
        String(500), 
        nullable=True,
        comment="Live project URL"
    )
    
    # Source code repository (optional)
    # Usually a GitHub link
    github_url = Column(
        String(500), 
        nullable=True,
        comment="GitHub repository URL"
    )
    
    # Preview image (optional)
    # URL to a screenshot or logo
    image_url = Column(
        String(500), 
        nullable=True,
        comment="Preview image URL"
    )
    
    # Featured flag
    # Featured projects appear on the homepage
    featured = Column(
        Boolean, 
        default=False, 
        nullable=False,
        comment="Show on homepage?"
    )
    
    # Display order
    # Lower numbers appear first
    # Allows manual sorting of projects
    order = Column(
        Integer, 
        default=0, 
        nullable=False,
        comment="Display order (lower = first)"
    )
    
    # Creation timestamp
    created_at = Column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False,
        comment="When project was added"
    )
    
    # -------------------------------------------------------------------------
    # String Representation
    # -------------------------------------------------------------------------
    
    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        featured = "⭐" if self.featured else ""
        return f"<Project(id={self.id}, title='{self.title}'{featured})>"
    
    # -------------------------------------------------------------------------
    # Computed Properties
    # -------------------------------------------------------------------------
    
    @property
    def tech_list(self) -> list[str]:
        """
        Get technologies as a list.
        
        Splits the comma-separated tech_stack string.
        Strips whitespace from each item.
        
        Returns:
            list[str]: List of technology names
        
        Example:
            project.tech_stack = "Python, FastAPI, SQLite"
            project.tech_list  # ["Python", "FastAPI", "SQLite"]
        """
        if not self.tech_stack:
            return []
        return [tech.strip() for tech in self.tech_stack.split(",")]
    
    @property
    def short_description(self) -> str:
        """
        Get a shortened description for listings.
        
        Returns:
            str: First 150 characters of plain text
        """
        # Strip markdown formatting (simple approach)
        text = self.description.replace("#", "").replace("*", "").strip()
        # Take first paragraph
        first_para = text.split("\n\n")[0]
        if len(first_para) > 150:
            return first_para[:147] + "..."
        return first_para
