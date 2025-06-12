"""Database configuration and connection management"""

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# SQLAlchemy database URL
DATABASE_URL = settings.DATABASE_URL

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create declarative base
Base = declarative_base()


async def get_async_session():
    """Get async database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_db():
    """Dependency to get database session (FastAPI dependency)"""
    async for session in get_async_session():
        yield session


def create_tables():
    """
    Create all database tables
    This is a synchronous version for startup
    """
    try:
        # Import all models to ensure they're registered with Base
        from app.models import user, company, financial_statements
        
        # Create synchronous engine for table creation
        sync_engine = create_engine(
            DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"),
            echo=False
        )
        
        # Create all tables
        Base.metadata.create_all(bind=sync_engine)
        print("✅ Database tables created/verified successfully")
        
    except Exception as e:
        print(f"⚠️  Database table creation failed: {e}")
        print("ℹ️  This might be normal if database is not running")


async def init_db():
    """Initialize the database (async version)"""
    async with engine.begin() as conn:
        # Import all models to ensure they're registered with Base
        from app.models import user, company, financial_statements
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()
