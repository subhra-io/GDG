#!/usr/bin/env python3
"""Complete demo setup - loads everything needed for a smooth demo."""

import sys
from pathlib import Path
from datetime import datetime
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import db_manager
from src.models import PolicyDocument, ComplianceRule, Violation
from src.core.logging import get_logger

logger = get_logger(__name__)

# Initialize database
db_manager.initialize_postgres()


def create_aml_policy_and_rules(db):
    """Create AML policy with rules."""
    print("\n📋 Creating AML Policy...")
    
    # Create policy
    policy = PolicyDocument(
        name="Anti-Money Laundering Policy",
        description="Compliance rules for detecting money laundering activities",
        policy_type="AML",
        version="1.0",
        effective_date=datetime.utcnow(),
        content_text="AML Policy with 4 key rules for financial transaction monitoring"
    )
    db.add(policy)
    db.flush()
    
    # Rule 1: High-value transactions
    rule1 = ComplianceRule(
        policy_id=policy.id,
        description="Transactions exceeding $10,000 require approval",
        severity="high",
        validation_logic={
            "condition": {
                "field": "amount",
                "operator": "greater_than",
                "value": 10000
            }
        },
        is_active=True
    )
    
    # Rule 2: Rapid transfers
    rule2 = ComplianceRule(
        policy_id=policy.id,
        description="More than 5 transfers in 24 hours flagged for review",
        severity="medium",
        validation_logic={
            "condition": {
                "field": "transaction_type",
                "operator": "equals",
                "value": "TRANSFER"
            }
        },
        is_active=True
    )
    
    # Rule 3: Cash transactions
    rule3 = ComplianceRule(
        policy_id=policy.id,
        description="Cash transactions over $5,000 require documentation",
        severity="high",
        validation_logic={
            "condition": {
                "field": "transaction_type",
                "operator": "equals",
                "value": "CASH_OUT"
            }
        },
        is_active=True
    )
    
    # Rule 4: Structuring detection
    rule4 = ComplianceRule(
        policy_id=policy.id,
        description="Transactions between $9,000-$9,999 flagged for structuring",
        severity="critical",
        validation_logic={
            "condition": {
                "field": "amount",
                "operator": "greater_than",
                "value": 9000
            }
        },
        is_active=True
    )
    
    db.add_all([rule1, rule2, rule3, rule4])
    db.commit()
    
    print(f"  ✓ Created AML policy with 4 rules")
    return policy.id


def create_sample_violations(db, policy_id):
    """Create sample violations with AI-generated content."""
    print("\n🚨 Creating Sample Violations...")
    
    violations = []
    
    # Violation 1: High-value transaction
    v1 = Violation(
        rule_id=db.query(ComplianceRule).filter(
            ComplianceRule.description.contains("$10,000")
        ).first().id,
        record_identifier="high-value-txn-001",
        table_name="company_records",
        severity="high",
        status="pending_review",
        justification="This transaction of $15,000 exceeds the $10,000 threshold requiring managerial approval. No approval record was found in the system, violating AML policy section 2.1. High-value transactions must be reviewed to prevent money laundering activities.",
        record_snapshot={
            "transaction_id": "TXN-HV-001",
            "amount": 15000,
            "transaction_type": "TRANSFER",
            "from_account": "ACC001",
            "to_account": "ACC002"
        },
        remediation_steps=[
            {
                "step": 1,
                "action": "Obtain retroactive approval from authorized manager",
                "priority": "critical",
                "responsible_party": "Compliance Manager",
                "estimated_time": "2 hours",
                "is_preventive": False
            },
            {
                "step": 2,
                "action": "Document approval in compliance system",
                "priority": "high",
                "responsible_party": "Compliance Officer",
                "estimated_time": "1 hour",
                "is_preventive": False
            },
            {
                "step": 3,
                "action": "Review similar transactions in past 30 days",
                "priority": "medium",
                "responsible_party": "Audit Team",
                "estimated_time": "4 hours",
                "is_preventive": False
            },
            {
                "step": 4,
                "action": "Update transaction processing workflow to require approval before execution",
                "priority": "low",
                "responsible_party": "IT Department",
                "estimated_time": "1 week",
                "is_preventive": True
            }
        ]
    )
    violations.append(v1)
    
    # Violation 2: Cash transaction
    v2 = Violation(
        rule_id=db.query(ComplianceRule).filter(
            ComplianceRule.description.contains("Cash transactions")
        ).first().id,
        record_identifier="cash-txn-001",
        table_name="company_records",
        severity="high",
        status="pending_review",
        justification="Cash withdrawal of $7,500 lacks required documentation. AML regulations mandate detailed documentation for cash transactions exceeding $5,000 to prevent money laundering. Missing documentation includes source of funds verification and purpose statement.",
        record_snapshot={
            "transaction_id": "TXN-CASH-001",
            "amount": 7500,
            "transaction_type": "CASH_OUT",
            "from_account": "ACC003",
            "to_account": "CASH"
        },
        remediation_steps=[
            {
                "step": 1,
                "action": "Contact customer to obtain required documentation",
                "priority": "critical",
                "responsible_party": "Branch Manager",
                "estimated_time": "24 hours",
                "is_preventive": False
            },
            {
                "step": 2,
                "action": "File Suspicious Activity Report (SAR) if documentation not provided",
                "priority": "high",
                "responsible_party": "Compliance Officer",
                "estimated_time": "48 hours",
                "is_preventive": False
            },
            {
                "step": 3,
                "action": "Implement mandatory documentation check in cash withdrawal system",
                "priority": "medium",
                "responsible_party": "IT Department",
                "estimated_time": "2 weeks",
                "is_preventive": True
            }
        ]
    )
    violations.append(v2)
    
    # Violation 3: Structuring
    v3 = Violation(
        rule_id=db.query(ComplianceRule).filter(
            ComplianceRule.description.contains("structuring")
        ).first().id,
        record_identifier="struct-txn-001",
        table_name="company_records",
        severity="critical",
        status="pending_review",
        justification="Transaction of $9,850 falls within the structuring detection range ($9,000-$9,999). This pattern suggests deliberate avoidance of the $10,000 reporting threshold, which is a red flag for money laundering. Multiple transactions in this range from the same account require immediate investigation.",
        record_snapshot={
            "transaction_id": "TXN-STRUCT-001",
            "amount": 9850,
            "transaction_type": "TRANSFER",
            "from_account": "ACC004",
            "to_account": "ACC005"
        },
        remediation_steps=[
            {
                "step": 1,
                "action": "Immediately freeze account pending investigation",
                "priority": "critical",
                "responsible_party": "Compliance Manager",
                "estimated_time": "Immediate",
                "is_preventive": False
            },
            {
                "step": 2,
                "action": "Review all transactions from this account in past 90 days",
                "priority": "critical",
                "responsible_party": "Fraud Investigation Team",
                "estimated_time": "24 hours",
                "is_preventive": False
            },
            {
                "step": 3,
                "action": "File Suspicious Activity Report (SAR) with FinCEN",
                "priority": "high",
                "responsible_party": "Compliance Officer",
                "estimated_time": "48 hours",
                "is_preventive": False
            },
            {
                "step": 4,
                "action": "Implement automated structuring detection alerts",
                "priority": "medium",
                "responsible_party": "IT Department",
                "estimated_time": "1 month",
                "is_preventive": True
            }
        ]
    )
    violations.append(v3)
    
    db.add_all(violations)
    db.commit()
    
    print(f"  ✓ Created {len(violations)} sample violations with AI justifications")
    return len(violations)


def main():
    """Main setup function."""
    print("\n" + "="*60)
    print("  PolicySentinel - Complete Demo Setup")
    print("="*60)
    
    db = db_manager.get_postgres_session()
    
    try:
        # Check existing data
        existing_records = db.query(PolicyDocument).count()
        if existing_records > 0:
            print(f"\n⚠️  Found {existing_records} existing policies")
            response = input("Clear existing data and start fresh? (y/n): ")
            if response.lower() == 'y':
                db.query(Violation).delete()
                db.query(ComplianceRule).delete()
                db.query(PolicyDocument).delete()
                db.commit()
                print("  ✓ Cleared existing data")
        
        # Create policies and rules
        policy_id = create_aml_policy_and_rules(db)
        
        # Create sample violations
        violation_count = create_sample_violations(db, policy_id)
        
        print("\n" + "="*60)
        print("  ✅ Demo Setup Complete!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  • Policies: 1 (AML)")
        print(f"  • Rules: 4 (active)")
        print(f"  • Violations: {violation_count} (with AI analysis)")
        print(f"  • Records: 36 (transactions)")
        
        print(f"\n🎬 Demo Flow:")
        print(f"  1. Dashboard: http://localhost:3000")
        print(f"  2. Policies: http://localhost:3000/policies")
        print(f"  3. Violations: http://localhost:3000/violations")
        print(f"  4. Data Explorer: http://localhost:3000/data")
        
        print(f"\n💡 Key Talking Points:")
        print(f"  • 'IBM AML dataset support with 36 transactions'")
        print(f"  • 'AI-powered violation detection and justification'")
        print(f"  • 'Actionable remediation steps with priorities'")
        print(f"  • 'Production-ready architecture with 3 databases'")
        
        print(f"\n🚀 You're ready to demo!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        logger.exception("Demo setup failed")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
