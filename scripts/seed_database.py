#!/usr/bin/env python3
"""
Database seeder script for NIDS Application.
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.seeders import SeederManager
from database.db import db
from database.models import Base


def drop_all_tables():
    """Safely drop all tables using SQLAlchemy"""
    print("🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=db.engine)
    print("✅ All tables dropped successfully!")


def create_all_tables():
    """Create all tables using SQLAlchemy"""
    print("🏗️  Creating all tables...")
    Base.metadata.create_all(bind=db.engine)
    print("✅ All tables created successfully!")


def main():
    try:
        print("🚀 Starting NIDS Database Seeder")
        print("=" * 50)

        # Optional: Fresh mode (drop and recreate tables)
        if len(sys.argv) > 1 and sys.argv[1] == "--fresh":
            drop_all_tables()
            create_all_tables()

        # Run all seeders
        SeederManager.run_all()

        print("\n✅ Seeding completed successfully!")
        return 0

    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())