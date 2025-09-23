#!/usr/bin/env python3

import sys

from database.db import db
from database.models import Base


def drop_all_tables():
    """Safely drop all tables using SQLAlchemy"""
    print("🗑️  Dropping all tables...")
    Base.metadata.drop_all(bind=db.engine)
    print("✅  All tables dropped successfully!")


def create_all_tables():
    """Create all tables using SQLAlchemy"""
    print("🏗️  Creating all tables...")
    Base.metadata.create_all(bind=db.engine)
    print("✅  All tables created successfully!")


def migrate():
    """Apply database schema changes"""
    try:
        print("🚀  Starting Data Migration...")
        print("=" * 50)

        if len(sys.argv) > 1 and sys.argv[1] == "--fresh":
            drop_all_tables()

        create_all_tables()
        print("\n✅  Migration completed successfully!")

    except Exception as e:
        print(f"❌ SMigration failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(migrate())
