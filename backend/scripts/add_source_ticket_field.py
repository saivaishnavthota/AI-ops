#!/usr/bin/env python3
"""
Add source_ticket_id field to kb_articles table.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.config.settings import settings


async def add_source_ticket_field():
    """Add source_ticket_id field to kb_articles table."""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    try:
        async with engine.begin() as conn:
            # Check if column already exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'kb_articles' 
                AND column_name = 'source_ticket_id'
            """))
            
            if result.fetchone() is None:
                # Add the column
                await conn.execute(text("""
                    ALTER TABLE kb_articles 
                    ADD COLUMN source_ticket_id UUID REFERENCES tickets(id) ON DELETE SET NULL
                """))
                print("✓ Added source_ticket_id column to kb_articles table")
            else:
                print("✓ source_ticket_id column already exists")
                
    except Exception as e:
        print(f"✗ Error adding column: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_source_ticket_field())