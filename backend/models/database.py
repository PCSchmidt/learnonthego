"""
Database configuration and setup for LearnOnTheGo
Supports both SQLite (development) and PostgreSQL (production)
"""

import os
from typing import AsyncGenerator
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./learnonthego.db")

# Convert postgres:// to postgresql:// for SQLAlchemy compatibility (Railway fix)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# For async operations, convert to async URL format
ASYNC_DATABASE_URL = DATABASE_URL
if DATABASE_URL.startswith("sqlite"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
elif DATABASE_URL.startswith("postgresql"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# SQLAlchemy Base
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

# Synchronous engine (for migrations and simple operations)
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",  # SQL logging in debug mode
    pool_pre_ping=True,  # Verify connections before use
)

# Asynchronous engine (for FastAPI operations)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_pre_ping=True,
)

# Session factories
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Dependency for FastAPI (async sessions)
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI routes to get async database session
    Usage: db: AsyncSession = Depends(get_async_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Dependency for FastAPI (sync sessions - for migrations)
def get_sync_db() -> Session:
    """
    Dependency for sync database operations (mainly for migrations)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database initialization functions
def create_tables():
    """
    Create all tables in the database (sync)
    Used for initial setup and migrations
    """
    Base.metadata.create_all(bind=engine)


async def create_tables_async():
    """
    Create all tables in the database (async)
    Used for testing and development
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables_async():
    """
    Drop all tables in the database (async)
    Used for testing cleanup
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Database health check
async def check_database_health() -> bool:
    """
    Check if database connection is healthy
    Returns True if connection successful, False otherwise
    """
    try:
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            result = await session.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False


# Connection info for debugging
def get_database_info() -> dict:
    """
    Get database connection information for debugging
    """
    return {
        "database_url": DATABASE_URL.replace(
            DATABASE_URL.split("@")[0].split("://")[1] + "@", "***@"
        ) if "@" in DATABASE_URL else DATABASE_URL,
        "async_database_url": ASYNC_DATABASE_URL.replace(
            ASYNC_DATABASE_URL.split("@")[0].split("://")[1] + "@", "***@"
        ) if "@" in ASYNC_DATABASE_URL else ASYNC_DATABASE_URL,
        "engine_info": str(engine.url).replace(
            str(engine.url).split("@")[0].split("://")[1] + "@", "***@"
        ) if "@" in str(engine.url) else str(engine.url),
        "debug_mode": os.getenv("DEBUG", "false").lower() == "true"
    }
