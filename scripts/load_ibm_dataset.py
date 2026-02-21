#!/usr/bin/env python3
"""Load IBM AML dataset into the database.

This script loads the IBM Transactions for Anti-Money Laundering dataset
into the PolicySentinel database for realistic compliance testing.

Dataset: https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml
License: CDLA-Sharing-1.0
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import SessionLocal
from src.datasets import IBMAMLLoader
from src.core.logging import get_logger

logger = get_logger(__name__)


def main():
    """Load IBM AML dataset."""
    parser = argparse.ArgumentParser(
        description="Load IBM AML dataset into PolicySentinel database"
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Path to IBM AML CSV file (e.g., HI-Small_Trans.csv)"
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Maximum number of records to load (default: all)"
    )
    parser.add_argument(
        "--laundering-only",
        action="store_true",
        help="Load only laundering transactions"
    )
    parser.add_argument(
        "--normal-only",
        action="store_true",
        help="Load only normal (non-laundering) transactions"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics about loaded data and exit"
    )
    
    args = parser.parse_args()
    
    # Create database session
    db = SessionLocal()
    
    try:
        loader = IBMAMLLoader(dataset_path=args.path)
        
        # Show statistics if requested
        if args.stats:
            stats = loader.get_statistics(db)
            print("\n=== IBM AML Dataset Statistics ===")
            print(f"Total Records: {stats['total_records']}")
            if stats['total_records'] > 0:
                print(f"Laundering Transactions: {stats['laundering_transactions']} ({stats['laundering_percentage']}%)")
                print(f"Normal Transactions: {stats['normal_transactions']}")
                print(f"\nAmount Statistics:")
                print(f"  Min: ${stats['amount_min']:,.2f}")
                print(f"  Max: ${stats['amount_max']:,.2f}")
                print(f"  Avg: ${stats['amount_avg']:,.2f}")
                print(f"\nTransaction Types:")
                for tx_type, count in stats['transaction_types'].items():
                    print(f"  {tx_type}: {count}")
            else:
                print(stats['message'])
            return
        
        # Determine what to load
        include_laundering = not args.normal_only
        include_normal = not args.laundering_only
        
        print("\n=== Loading IBM AML Dataset ===")
        print(f"Dataset path: {loader.dataset_path or 'Auto-detect'}")
        print(f"Max records: {args.max_records or 'All'}")
        print(f"Include laundering: {include_laundering}")
        print(f"Include normal: {include_normal}")
        print()
        
        # Load data
        records_loaded = loader.load_data(
            db,
            max_records=args.max_records,
            include_laundering=include_laundering,
            include_normal=include_normal
        )
        
        print(f"\n✓ Successfully loaded {records_loaded} records")
        
        # Show statistics
        stats = loader.get_statistics(db)
        print("\n=== Dataset Statistics ===")
        print(f"Total Records: {stats['total_records']}")
        print(f"Laundering Transactions: {stats['laundering_transactions']} ({stats['laundering_percentage']}%)")
        print(f"Normal Transactions: {stats['normal_transactions']}")
        print(f"\nAmount Range: ${stats['amount_min']:,.2f} - ${stats['amount_max']:,.2f}")
        print(f"Average Amount: ${stats['amount_avg']:,.2f}")
        
        print("\n=== Next Steps ===")
        print("1. Upload the sample AML policy: python scripts/create_sample_policy.py")
        print("2. Start the backend: uvicorn src.main:app --reload")
        print("3. Upload sample_aml_policy.pdf via the API")
        print("4. Run compliance scan to detect violations")
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nTo download the IBM AML dataset:")
        print("1. Visit: https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml")
        print("2. Download HI-Small_Trans.csv")
        print("3. Place it in the 'data' directory or specify path with --path")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error loading dataset: {e}")
        logger.exception("Failed to load IBM AML dataset")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
