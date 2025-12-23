"""
=============================================================================
DATABASE MODULE
=============================================================================
Purpose: Database connection and session management with SQLAlchemy.

This module:
- Creates the SQLAlchemy engine (connection to database)
- Sets up the session factory (for creating sessions)
- Provides a dependency for request-scoped sessions
- Initializes the database and creates tables

Key Concepts:
- Engine: The connection pool to the database
- Session: A workspace for database operations (unit of work)
- Base: Declarative base for ORM models to inherit from

Usage:
    # In routes, use the get_db dependency
    @app.get("/items")
    def get_items(db: Session = Depends(get_db)):
        return db.query(Item).all()
=============================================================================
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from app.config import settings

# =============================================================================
# ENGINE SETUP
# =============================================================================

# Create the SQLAlchemy engine
# The engine is the starting point for any SQLAlchemy application.
# It's the home base for the database connection pool.
engine = create_engine(
    settings.DATABASE_URL,
    # SQLite-specific setting: allows multiple threads to use same connection
    # This is needed because FastAPI runs in async mode with multiple threads
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    # Echo SQL statements to console in debug mode (useful for learning!)
    echo=settings.DEBUG,
)


# Enable foreign key enforcement for SQLite
# SQLite has foreign keys disabled by default (for legacy reasons)
# This listener ensures they're always enabled for data integrity
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints in SQLite."""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# =============================================================================
# SESSION SETUP
# =============================================================================

# SessionLocal is a factory for creating new Session objects
# Think of it as a "session template" - each call creates a new session
SessionLocal = sessionmaker(
    # Don't auto-commit; we'll manage transactions explicitly
    autocommit=False,
    # Don't auto-flush before queries; gives us more control
    autoflush=False,
    # Bind sessions to our engine
    bind=engine,
)

# =============================================================================
# DECLARATIVE BASE
# =============================================================================

# Base class for all ORM models
# All your models inherit from this, gaining SQLAlchemy powers
Base = declarative_base()


# =============================================================================
# DEPENDENCY
# =============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    
    This is a generator that:
    1. Creates a new session at the start of a request
    2. Yields it for the route handler to use
    3. Closes it when the request is complete
    
    The try/finally ensures the session is ALWAYS closed,
    even if an exception occurs during request handling.
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Session: A SQLAlchemy session for database operations
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# INITIALIZATION
# =============================================================================

def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This function:
    1. Imports all models (so SQLAlchemy knows about them)
    2. Creates tables that don't exist yet
    3. Skips tables that already exist (safe to run multiple times)
    
    Call this once at application startup.
    """
    # Import models here to register them with Base
    # This must happen BEFORE create_all() is called
    from app.models import user, post, project  # noqa: F401
    
    # Create all tables
    # checkfirst=True (default) means it won't fail if tables exist
    Base.metadata.create_all(bind=engine)
    
    # Create initial admin user if needed
    _create_initial_admin()


def _create_initial_admin() -> None:
    """
    Create the initial admin user if none exists.
    
    This ensures there's always an admin account for the site owner.
    Credentials come from environment variables (settings).
    """
    from app.models.user import User
    from app.services.auth import get_password_hash
    
    db = SessionLocal()
    try:
        # Check if any user exists
        existing_user = db.query(User).first()
        if existing_user is None:
            # Create the admin user
            admin = User(
                username=settings.ADMIN_USERNAME,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD)
            )
            db.add(admin)
            db.commit()
            print(f"✅ Created admin user: {settings.ADMIN_USERNAME}")
        else:
            print(f"ℹ️  Admin user already exists: {existing_user.username}")
    finally:
        db.close()
