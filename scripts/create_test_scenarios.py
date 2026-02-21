#!/usr/bin/env python3
"""Create pre-configured test scenarios for PolicySentinel demo.

This script creates realistic test data that will trigger specific compliance violations,
making it easy to demonstrate the system's capabilities.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import db_manager
from src.models import CompanyRecord
from src.core.logging import get_logger

logger = get_logger(__name__)

# Initialize database
db_manager.initialize_postgres()


class TestScenarioGenerator:
    """Generate test scenarios for compliance violations."""
    
    def __init__(self, db):
        """Initialize generator with database session."""
        self.db = db
        self.base_time = datetime.utcnow() - timedelta(days=7)
    
    def create_aml_scenarios(self):
        """Create AML compliance test scenarios."""
        scenarios = []
        
        # Scenario 1: High-value transaction (violates $10,000 threshold)
        scenarios.append(CompanyRecord(
            transaction_id="SCENARIO_AML_001",
            timestamp=self.base_time,
            from_account="ACC1001",
            to_account="ACC2001",
            amount=15750.00,
            transaction_type="TRANSFER",
            record_type="transaction",
            data={
                "currency": "USD",
                "status": "completed",
                "channel": "online",
                "description": "High-value transfer - should trigger $10k threshold rule",
                "scenario": "aml_high_value"
            }
        ))
        
        # Scenario 2: Multiple transactions exceeding $50k in 24h (pattern violation)
        base_time_pattern = self.base_time + timedelta(days=1)
        pattern_amounts = [12000, 15000, 18000, 22000]  # Total: $67,000
        for i, amount in enumerate(pattern_amounts):
            scenarios.append(CompanyRecord(
                transaction_id=f"SCENARIO_AML_002_{i+1}",
                timestamp=base_time_pattern + timedelta(hours=i*4),
                from_account="ACC1002",
                to_account=f"ACC200{i+2}",
                amount=amount,
                transaction_type="TRANSFER",
                record_type="transaction",
                data={
                    "currency": "USD",
                    "status": "completed",
                    "channel": "mobile",
                    "description": f"Pattern violation part {i+1}/4 - total exceeds $50k in 24h",
                    "scenario": "aml_pattern_violation"
                }
            ))
        
        # Scenario 3: Large cash withdrawal (violates $5,000 cash limit)
        scenarios.append(CompanyRecord(
            transaction_id="SCENARIO_AML_003",
            timestamp=self.base_time + timedelta(days=2),
            from_account="ACC1003",
            to_account="CASH",
            amount=7200.00,
            transaction_type="CASH_OUT",
            record_type="transaction",
            data={
                "currency": "USD",
                "status": "completed",
                "channel": "branch",
                "description": "Large cash withdrawal - should trigger $5k cash limit rule",
                "scenario": "aml_cash_limit"
            }
        ))
        
        # Scenario 4: Rapid fund movement (in and out within 1 hour)
        rapid_time = self.base_time + timedelta(days=3)
        scenarios.append(CompanyRecord(
            transaction_id="SCENARIO_AML_004_IN",
            timestamp=rapid_time,
            from_account="ACC1004",
            to_account="ACC1005",
            amount=25000.00,
            transaction_type="TRANSFER",
            record_type="transaction",
            data={
                "currency": "USD",
                "status": "completed",
                "channel": "online",
                "description": "Rapid movement part 1 - funds in",
                "scenario": "aml_rapid_movement"
            }
        ))
        scenarios.append(CompanyRecord(
            transaction_id="SCENARIO_AML_004_OUT",
            timestamp=rapid_time + timedelta(minutes=30),
            from_account="ACC1005",
            to_account="ACC2005",
            amount=24500.00,
            transaction_type="TRANSFER",
            record_type="transaction",
            data={
                "currency": "USD",
                "status": "completed",
                "channel": "online",
                "description": "Rapid movement part 2 - funds out within 1 hour",
                "scenario": "aml_rapid_movement"
            }
        ))
        
        # Scenario 5: Compliant transactions (should NOT trigger violations)
        scenarios.append(CompanyRecord(
            transaction_id="SCENARIO_AML_COMPLIANT_001",
            timestamp=self.base_time + timedelta(days=4),
            from_account="ACC1006",
            to_account="ACC2006",
            amount=4500.00,
            transaction_type="TRANSFER",
            record_type="transaction",
            data={
                "currency": "USD",
                "status": "completed",
                "channel": "online",
                "description": "Compliant transaction - below all thresholds",
                "scenario": "aml_compliant"
            }
        ))
        
        return scenarios
    
    def create_gdpr_scenarios(self):
        """Create GDPR compliance test scenarios."""
        scenarios = []
        
        # Scenario 1: Data retention violation (> 90 days old)
        old_date = datetime.utcnow() - timedelta(days=120)
        scenarios.append(CompanyRecord(
            transaction_id="SCENARIO_GDPR_001",
            timestamp=old_date,
            from_account="USER001",
            to_account="SYSTEM",
            amount=0.0,
            transaction_type="DATA_RECORD",
            record_type="personal_data",
            data={
                "record_type": "user_profile",
                "created_date": old_date.isoformat(),
                "retention_days": 120,
                "purpose_fulfilled": True,
                "description": "Old personal data record - exceeds 90-day retention limit",
                "scenario": "gdpr_retention_violation"
            }
        ))
        
        # Scenario 2: Missing consent
        scenarios.append(CompanyRecord(
            transaction_id="SCENARIO_GDPR_002",
            timestamp=self.base_time,
            from_account="USER002",
            to_account="SYSTEM",
            amount=0.0,
            transaction_type="DATA_RECORD",
            record_type="personal_data",
            data={
                "record_type": "user_profile",
                "consent_status": None,
                "consent_date": None,
                "description": "Personal data without documented consent",
                "scenario": "gdpr_missing_consent"
            }
        ))
        
        # Scenario 3: Withdrawn consent
        scenarios.append(CompanyRecord(
            transaction_id="SCENARIO_GDPR_003",
            timestamp=self.base_time + timedelta(days=1),
            from_account="USER003",
            to_account="SYSTEM",
            amount=0.0,
            transaction_type="DATA_RECORD",
            record_type="personal_data",
            data={
                "record_type": "user_profile",
                "consent_status": "withdrawn",
                "consent_date": (self.base_time - timedelta(days=30)).isoformat(),
                "withdrawal_date": (self.base_time - timedelta(days=5)).isoformat(),
                "description": "Personal data with withdrawn consent - should be deleted",
                "scenario": "gdpr_withdrawn_consent"
            }
        ))
        
        # Scenario 4: Excessive data collection (> 10 fields)
        scenarios.append(CompanyRecord(
            transaction_id="SCENARIO_GDPR_004",
            timestamp=self.base_time + timedelta(days=2),
            from_account="USER004",
            to_account="SYSTEM",
            amount=0.0,
            transaction_type="DATA_RECORD",
            record_type="personal_data",
            data={
                "record_type": "user_profile",
                "field_count": 15,
                "fields": ["name", "email", "phone", "address", "ssn", "dob", "gender", 
                          "income", "employer", "job_title", "education", "marital_status",
                          "children_count", "hobbies", "political_affiliation"],
                "description": "Excessive personal data collection - violates minimization principle",
                "scenario": "gdpr_data_minimization"
            }
        ))
        
        return scenarios
    
    def create_sox_scenarios(self):
        """Create SOX compliance test scenarios."""
        scenarios = []
        
        # Scenario 1: Missing dual authorization (> $25,000)
        scenarios.append(CompanyRecord(
            transaction_id="SCENARIO_SOX_001",
            timestamp=self.base_time,
            from_account="CORP_ACCOUNT",
            to_account="VENDOR_001",
            amount=35000.00,
            transaction_type="PAYMENT",
            record_type="financial_transaction",
            data={
                "approver_1": "EMP123",
                "approver_2": None,  # Missing second approver
                "description": "Large payment without dual authorization",
                "scenario": "sox_missing_dual_auth"
            }
        ))
        
        # Scenario 2: Segregation of duties violation
        scenarios.append(CompanyRecord(
            transaction_id="SCENARIO_SOX_002",
            timestamp=self.base_time + timedelta(days=1),
            from_account="CORP_ACCOUNT",
            to_account="VENDOR_002",
            amount=15000.00,
            transaction_type="PAYMENT",
            record_type="financial_transaction",
            data={
                "created_by": "EMP456",
                "approved_by": "EMP456",  # Same person - violation
                "description": "Transaction created and approved by same person",
                "scenario": "sox_segregation_violation"
            }
        ))
        
        # Scenario 3: Incomplete audit trail
        scenarios.append(CompanyRecord(
            transaction_id="SCENARIO_SOX_003",
            timestamp=self.base_time + timedelta(days=2),
            from_account="CORP_ACCOUNT",
            to_account="VENDOR_003",
            amount=8000.00,
            transaction_type="PAYMENT",
            record_type="financial_transaction",
            data={
                "created_at": self.base_time.isoformat(),
                "created_by": "EMP789",
                "modified_at": None,  # Missing
                "modified_by": None,  # Missing
                "description": "Transaction with incomplete audit trail",
                "scenario": "sox_incomplete_audit"
            }
        ))
        
        return scenarios
    
    def load_all_scenarios(self):
        """Load all test scenarios into the database."""
        print("=== Creating Test Scenarios ===\n")
        
        all_scenarios = []
        
        # AML scenarios
        print("Creating AML test scenarios...")
        aml_scenarios = self.create_aml_scenarios()
        all_scenarios.extend(aml_scenarios)
        print(f"  ✓ Created {len(aml_scenarios)} AML scenarios")
        
        # GDPR scenarios
        print("Creating GDPR test scenarios...")
        gdpr_scenarios = self.create_gdpr_scenarios()
        all_scenarios.extend(gdpr_scenarios)
        print(f"  ✓ Created {len(gdpr_scenarios)} GDPR scenarios")
        
        # SOX scenarios
        print("Creating SOX test scenarios...")
        sox_scenarios = self.create_sox_scenarios()
        all_scenarios.extend(sox_scenarios)
        print(f"  ✓ Created {len(sox_scenarios)} SOX scenarios")
        
        # Save to database
        print(f"\nSaving {len(all_scenarios)} test scenarios to database...")
        for scenario in all_scenarios:
            self.db.add(scenario)
        
        self.db.commit()
        print("✓ All test scenarios saved successfully")
        
        return len(all_scenarios)


def main():
    """Main function."""
    print("\n=== PolicySentinel Test Scenario Generator ===\n")
    
    db = db_manager.get_postgres_session()
    
    try:
        generator = TestScenarioGenerator(db)
        total_scenarios = generator.load_all_scenarios()
        
        print(f"\n=== Summary ===")
        print(f"Total scenarios created: {total_scenarios}")
        print("\nScenario Types:")
        print("  • AML: High-value transactions, pattern violations, cash limits, rapid movement")
        print("  • GDPR: Data retention, missing consent, withdrawn consent, data minimization")
        print("  • SOX: Missing dual auth, segregation violations, incomplete audit trails")
        
        print("\n=== Next Steps ===")
        print("1. Generate policy PDFs: python scripts/create_sample_policy.py --type all")
        print("2. Start backend: uvicorn src.main:app --reload")
        print("3. Upload policies via API")
        print("4. Run compliance scans to detect violations in test scenarios")
        print("\nThe test scenarios are designed to trigger specific violations for demo purposes.")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        logger.exception("Failed to create test scenarios")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
