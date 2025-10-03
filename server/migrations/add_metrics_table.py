#!/usr/bin/env python3
"""
Database migration script to add the interaction_metrics table.
Run this script to add the new metrics table to your database.
"""

import asyncio
import sys
from pathlib import Path

# Add the server directory to the Python path
server_dir = Path(__file__).parent.parent
sys.path.insert(0, str(server_dir))

from common.database import get_engine
from common.models import Base, InteractionMetrics
from sqlalchemy import text


async def create_metrics_table():
    """Create the interaction_metrics table."""
    engine = get_engine()
    
    try:
        # Create the table
        async with engine.begin() as conn:
            # Check if table already exists
            result = await conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='interaction_metrics'
            """))
            
            if result.fetchone():
                print("✅ interaction_metrics table already exists")
                return
            
            # Create the table
            await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, tables=[InteractionMetrics.__table__]))
            print("✅ Successfully created interaction_metrics table")
            
    except Exception as e:
        print(f"❌ Error creating metrics table: {e}")
        raise


async def main():
    """Main migration function."""
    print("🚀 Starting database migration: Adding interaction_metrics table")
    
    try:
        await create_metrics_table()
        print("✅ Migration completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
