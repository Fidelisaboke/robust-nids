#!/usr/bin/env python3
"""
Database seeder script for NIDS Application.
"""

import sys

from database.seeders import SeederManager
from migrate import drop_all_tables, create_all_tables


def seed():
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
    sys.exit(seed())
