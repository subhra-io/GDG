"""Quick demo data setup."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import db_manager
from src.models import ComplianceRule, Violation, CompanyRecord
from src.core.logging import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)

def create_demo_data():
    """Create demo rules and violations."""
    
    db_manager.initialize_postgres()
    session = db_manager.get_postgres_session()
    
    try:
        # First create a dummy policy document
        from src.models import PolicyDocument
        import hashlib
        
        policy = PolicyDocument(
            filename="demo_policy.pdf",
            file_size_bytes=1024,
            file_hash=hashlib.md5(b"demo_policy").hexdigest(),
            extracted_text="Demo compliance policy for testing"
        )
        session.add(policy)
        session.flush()
        logger.info(f"Created policy document: {policy.filename}")
        
        # Create sample rules
        rules = [
            {
                "description": "Transactions over $10,000 require additional verification",
                "severity": "high",
                "validation_logic": {
                    "condition": {
                        "field": "amount",
                        "operator": "greater_than",
                        "value": 10000
                    }
                }
            },
            {
                "description": "Wire transfers to high-risk countries must be flagged",
                "severity": "critical",
                "validation_logic": {
                    "condition": {
                        "field": "transaction_type",
                        "operator": "equals",
                        "value": "wire_transfer"
                    }
                }
            },
            {
                "description": "Cash transactions over $5,000 require documentation",
                "severity": "medium",
                "validation_logic": {
                    "condition": {
                        "field": "amount",
                        "operator": "greater_than",
                        "value": 5000
                    }
                }
            }
        ]
        
        created_rules = []
        for rule_data in rules:
            rule = ComplianceRule(
                policy_document_id=policy.id,
                description=rule_data["description"],
                severity=rule_data["severity"],
                validation_logic=rule_data["validation_logic"],
                is_active=True
            )
            session.add(rule)
            session.flush()
            created_rules.append(rule)
            logger.info(f"Created rule: {rule.description}")
        
        # Get some records
        records = session.query(CompanyRecord).limit(10).all()
        
        # Create sample violations with risk scores
        for i, record in enumerate(records[:5]):
            rule = created_rules[i % len(created_rules)]
            
            violation = Violation(
                rule_id=rule.id,
                record_identifier=str(record.id),
                table_name="company_records",
                justification=f"This transaction violates the rule: {rule.description}. "
                             f"The transaction amount of ${record.amount} exceeds the threshold.",
                record_snapshot={
                    "id": str(record.id),
                    "transaction_id": record.transaction_id,
                    "amount": record.amount,
                    "transaction_type": record.transaction_type,
                    "from_account": record.from_account,
                    "to_account": record.to_account
                },
                severity=rule.severity,
                remediation_steps=[
                    {"step": 1, "description": "Review transaction details"},
                    {"step": 2, "description": "Verify customer identity"},
                    {"step": 3, "description": "Document findings"}
                ],
                # Add risk scores
                risk_score=75 + (i * 5),  # 75, 80, 85, 90, 95
                risk_level="High" if i < 2 else "Critical",
                risk_factors={
                    "severity_weight": 30,
                    "amount_factor": 20,
                    "frequency_factor": 15,
                    "historical_factor": 10
                }
            )
            session.add(violation)
            logger.info(f"Created violation for record {record.transaction_id}")
        
        session.commit()
        
        # Count results
        total_rules = session.query(ComplianceRule).count()
        total_violations = session.query(Violation).count()
        
        print(f"\n✅ Demo data created successfully!")
        print(f"   Rules: {total_rules}")
        print(f"   Violations: {total_violations}")
        print(f"\n🚀 Ready for demo!")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create demo data: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    create_demo_data()
