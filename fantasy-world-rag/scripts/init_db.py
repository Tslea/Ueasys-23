"""
Database Initialization Script

This script creates all database tables and sets up initial data.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from src.config.settings import get_settings
from src.db.models.base import Base


async def init_database():
    """Initialize the database with all required tables."""
    settings = get_settings()
    
    print(f"🔧 Initializing database...")
    print(f"   Database URL: {settings.database.url.split('@')[-1] if '@' in settings.database.url else 'local'}")
    
    # Create async engine
    engine = create_async_engine(
        settings.database.url,
        echo=settings.database.echo,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow
    )
    
    try:
        # Create all tables
        async with engine.begin() as conn:
            print("📦 Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully!")
        
        # Verify tables
        async with engine.begin() as conn:
            result = await conn.execute(
                text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'")
            )
            tables = [row[0] for row in result]
            print(f"\n📋 Tables created:")
            for table in tables:
                print(f"   - {table}")
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        
        # Try SQLite fallback info
        if "postgresql" in settings.database.url:
            print("\n💡 Tip: Make sure PostgreSQL is running and accessible.")
            print("   You can also use SQLite for development:")
            print("   DATABASE_URL=sqlite+aiosqlite:///./fantasy_rag.db")
        
        raise
    
    finally:
        await engine.dispose()


async def drop_database():
    """Drop all database tables (use with caution!)."""
    settings = get_settings()
    
    print("⚠️  WARNING: This will delete all data!")
    confirmation = input("Type 'DELETE' to confirm: ")
    
    if confirmation != "DELETE":
        print("Cancelled.")
        return
    
    engine = create_async_engine(settings.database.url)
    
    try:
        async with engine.begin() as conn:
            print("🗑️  Dropping all tables...")
            await conn.run_sync(Base.metadata.drop_all)
        
        print("✅ All tables dropped.")
        
    finally:
        await engine.dispose()


async def check_connection():
    """Check database connection."""
    settings = get_settings()
    
    print("🔍 Checking database connection...")
    
    engine = create_async_engine(settings.database.url)
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
        
    finally:
        await engine.dispose()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database management script")
    parser.add_argument(
        "action",
        choices=["init", "drop", "check"],
        help="Action to perform"
    )
    
    args = parser.parse_args()
    
    if args.action == "init":
        asyncio.run(init_database())
    elif args.action == "drop":
        asyncio.run(drop_database())
    elif args.action == "check":
        asyncio.run(check_connection())


if __name__ == "__main__":
    main()
