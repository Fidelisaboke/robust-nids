#!/usr/bin/env python3
"""
Database seeder script for NIDS Application.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.database.seeders.manager import SeederManager  # noqa: E402


def seed():
    try:
        print('🚀 Starting NIDS Database Seeder')
        print('=' * 50)

        # Run all seeders
        SeederManager.run_all()

        print('\n✅ Seeding completed successfully!')
        return 0

    except Exception as e:
        print(f'❌ Seeding failed: {e}')
        import traceback

        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(seed())
