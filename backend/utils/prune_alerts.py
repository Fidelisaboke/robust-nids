import argparse
import os
import sys
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func

# --- Path Setup ---
# This adds the 'backend' directory to the Python path
# so we can import our application modules.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)
# ------------------

try:
    from database.db import db
    from database.models import Alert
except ImportError as e:
    print(f"Error: Could not import application modules. {e}")
    print("Please ensure this script is run from the 'backend/scripts' directory")
    print(f"Project Root: {PROJECT_ROOT}")
    sys.exit(1)


def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Prune old alerts from the database.")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Delete alerts older than this many days. Default: 30",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the script to see how many alerts *would* be deleted, but don't delete them.",
    )
    return parser.parse_args()


def prune_old_alerts(days_to_keep: int, dry_run: bool = False):
    """
    Connects to the database and deletes alerts older than the specified cutoff.
    """
    # 1. Calculate the cutoff date
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
    print(f"Target: Deleting alerts with a 'flow_timestamp' before {cutoff_date.isoformat()}")

    # 2. Build the SQLAlchemy query
    # We filter on 'flow_timestamp' as it's the most relevant time.
    stmt = delete(Alert).where(Alert.flow_timestamp < cutoff_date)

    with db.get_session() as session:
        try:
            if dry_run:
                print("--- [DRY RUN] ---")
                # For a dry run, we just do a COUNT.
                count_stmt = stmt.with_only_columns(func.count(Alert.id)).select()
                count = session.execute(count_stmt).scalar()
                print(f"Found {count} alerts that would be pruned.")
                print("No data was deleted.")
            else:
                print("--- [PRUNING] ---")
                # 3. Execute the delete query
                result = session.execute(stmt)

                # 4. Commit the transaction
                session.commit()
                print(f"✅ Success! Pruned {result.rowcount} alerts.")

        except Exception as e:
            print(f"❌ An error occurred during pruning: {e}")
            print("Transaction rolled back.")
            session.rollback()


if __name__ == "__main__":
    args = parse_args()
    if args.dry_run:
        print("Running in DRY-RUN mode. No data will be deleted.")

    prune_old_alerts(args.days, args.dry_run)
