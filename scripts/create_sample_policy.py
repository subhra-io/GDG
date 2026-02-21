#!/usr/bin/env python3
"""Create sample compliance policy PDFs for testing.

This script generates realistic policy documents that can be used to test
the PolicySentinel rule extraction and compliance monitoring capabilities.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
from pathlib import Path
import argparse


def create_aml_policy():
    """Create a sample AML compliance policy PDF."""
    
    output_path = Path("sample_aml_policy.pdf")
    
    # Create PDF
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Justify',
        alignment=TA_JUSTIFY,
        fontSize=11,
        leading=14
    ))
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1a1a1a',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2c3e50',
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph("Anti-Money Laundering (AML) Compliance Policy", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Introduction
    intro = Paragraph(
        "This policy establishes the framework for detecting and preventing money laundering "
        "activities through systematic monitoring of financial transactions. All transactions "
        "must comply with the rules outlined in this document.",
        styles['Justify']
    )
    elements.append(intro)
    elements.append(Spacer(1, 0.3*inch))
    
    # Rule 1
    rule1_heading = Paragraph("Rule 1: High-Value Transaction Monitoring", heading_style)
    elements.append(rule1_heading)
    
    rule1_text = Paragraph(
        "<b>Requirement:</b> Any single transaction exceeding $10,000 must be flagged for review. "
        "This threshold applies to all transaction types including transfers, cash withdrawals, "
        "and payments. Transactions at or above this amount require additional documentation and "
        "verification of the source of funds. <b>Severity: High</b>",
        styles['Justify']
    )
    elements.append(rule1_text)
    elements.append(Spacer(1, 0.2*inch))
    
    # Rule 2
    rule2_heading = Paragraph("Rule 2: Suspicious Transaction Patterns", heading_style)
    elements.append(rule2_heading)
    
    rule2_text = Paragraph(
        "<b>Requirement:</b> Multiple transactions from the same account totaling more than $50,000 "
        "within a 24-hour period must be investigated. This pattern may indicate structuring or "
        "smurfing activities designed to evade reporting requirements. The compliance team must "
        "review the business justification for such transaction patterns. <b>Severity: Critical</b>",
        styles['Justify']
    )
    elements.append(rule2_text)
    elements.append(Spacer(1, 0.2*inch))
    
    # Rule 3
    rule3_heading = Paragraph("Rule 3: Cash Transaction Limits", heading_style)
    elements.append(rule3_heading)
    
    rule3_text = Paragraph(
        "<b>Requirement:</b> Cash withdrawals (CASH_OUT transactions) exceeding $5,000 require "
        "manager approval and customer identification verification. Large cash transactions pose "
        "higher money laundering risks and must be documented with the purpose of withdrawal. "
        "<b>Severity: Medium</b>",
        styles['Justify']
    )
    elements.append(rule3_text)
    elements.append(Spacer(1, 0.2*inch))
    
    # Rule 4
    rule4_heading = Paragraph("Rule 4: Rapid Movement of Funds", heading_style)
    elements.append(rule4_heading)
    
    rule4_text = Paragraph(
        "<b>Requirement:</b> Funds transferred into an account and then immediately transferred out "
        "(within 1 hour) in amounts exceeding $20,000 must be flagged as potentially suspicious. "
        "This behavior may indicate layering activities in money laundering schemes. "
        "<b>Severity: High</b>",
        styles['Justify']
    )
    elements.append(rule4_text)
    elements.append(Spacer(1, 0.3*inch))
    
    # Compliance section
    compliance_heading = Paragraph("Compliance Monitoring", heading_style)
    elements.append(compliance_heading)
    
    compliance_text = Paragraph(
        "All transactions must be monitored continuously against these rules. Violations must be "
        "documented with clear justifications and remediation steps. The compliance team shall "
        "maintain an audit trail of all flagged transactions and their resolution status. "
        "Regular reports must be generated showing compliance rates and violation trends.",
        styles['Justify']
    )
    elements.append(compliance_text)
    elements.append(Spacer(1, 0.2*inch))
    
    # Enforcement
    enforcement_heading = Paragraph("Enforcement and Penalties", heading_style)
    elements.append(enforcement_heading)
    
    enforcement_text = Paragraph(
        "Failure to comply with these rules may result in regulatory penalties, account suspension, "
        "or termination of banking relationships. All staff members are required to report suspicious "
        "activities immediately to the compliance department. Training on AML procedures is mandatory "
        "for all employees handling financial transactions.",
        styles['Justify']
    )
    elements.append(enforcement_text)
    
    # Build PDF
    doc.build(elements)
    
    print(f"Sample policy created: {output_path}")
    print("\nThis policy contains 4 testable rules:")
    print("1. Transactions > $10,000 (High severity)")
    print("2. Multiple transactions > $50,000 in 24h (Critical severity)")
    print("3. Cash withdrawals > $5,000 (Medium severity)")
    print("4. Rapid fund movement > $20,000 (High severity)")
    print("\nYou can upload this PDF to test the rule extraction!")


def create_gdpr_policy():
    """Create a GDPR data privacy compliance policy PDF."""
    
    output_path = Path("sample_gdpr_policy.pdf")
    
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Justify',
        alignment=TA_JUSTIFY,
        fontSize=11,
        leading=14
    ))
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1a1a1a',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2c3e50',
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph("General Data Protection Regulation (GDPR) Compliance Policy", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Introduction
    intro = Paragraph(
        "This policy establishes requirements for protecting personal data in accordance with GDPR. "
        "All data processing activities must comply with the principles and rules outlined herein.",
        styles['Justify']
    )
    elements.append(intro)
    elements.append(Spacer(1, 0.3*inch))
    
    # Rule 1
    rule1_heading = Paragraph("Rule 1: Data Retention Limits", heading_style)
    elements.append(rule1_heading)
    
    rule1_text = Paragraph(
        "<b>Requirement:</b> Personal data must not be retained for longer than 90 days after "
        "the purpose for which it was collected has been fulfilled, unless required by law. "
        "Records exceeding this retention period must be flagged for deletion. <b>Severity: High</b>",
        styles['Justify']
    )
    elements.append(rule1_text)
    elements.append(Spacer(1, 0.2*inch))
    
    # Rule 2
    rule2_heading = Paragraph("Rule 2: Consent Documentation", heading_style)
    elements.append(rule2_heading)
    
    rule2_text = Paragraph(
        "<b>Requirement:</b> All personal data records must have documented consent. "
        "Records without a valid consent_date field or with consent_status set to 'withdrawn' "
        "must be flagged for review and potential deletion. <b>Severity: Critical</b>",
        styles['Justify']
    )
    elements.append(rule2_text)
    elements.append(Spacer(1, 0.2*inch))
    
    # Rule 3
    rule3_heading = Paragraph("Rule 3: Data Minimization", heading_style)
    elements.append(rule3_heading)
    
    rule3_text = Paragraph(
        "<b>Requirement:</b> Records containing more than 10 personal data fields must be "
        "reviewed for data minimization compliance. Only data necessary for the stated purpose "
        "should be collected and retained. <b>Severity: Medium</b>",
        styles['Justify']
    )
    elements.append(rule3_text)
    
    doc.build(elements)
    
    print(f"GDPR policy created: {output_path}")
    print("\nThis policy contains 3 testable rules:")
    print("1. Data retention > 90 days (High severity)")
    print("2. Missing or withdrawn consent (Critical severity)")
    print("3. Excessive data collection > 10 fields (Medium severity)")


def create_sox_policy():
    """Create a SOX financial controls compliance policy PDF."""
    
    output_path = Path("sample_sox_policy.pdf")
    
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Justify',
        alignment=TA_JUSTIFY,
        fontSize=11,
        leading=14
    ))
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1a1a1a',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2c3e50',
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph("Sarbanes-Oxley (SOX) Financial Controls Policy", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Introduction
    intro = Paragraph(
        "This policy establishes internal controls for financial reporting accuracy and integrity "
        "in compliance with SOX requirements. All financial transactions must adhere to these controls.",
        styles['Justify']
    )
    elements.append(intro)
    elements.append(Spacer(1, 0.3*inch))
    
    # Rule 1
    rule1_heading = Paragraph("Rule 1: Dual Authorization Requirement", heading_style)
    elements.append(rule1_heading)
    
    rule1_text = Paragraph(
        "<b>Requirement:</b> All financial transactions exceeding $25,000 must have dual authorization. "
        "Records must contain both 'approver_1' and 'approver_2' fields with valid employee IDs. "
        "Transactions without dual approval must be flagged. <b>Severity: Critical</b>",
        styles['Justify']
    )
    elements.append(rule1_text)
    elements.append(Spacer(1, 0.2*inch))
    
    # Rule 2
    rule2_heading = Paragraph("Rule 2: Segregation of Duties", heading_style)
    elements.append(rule2_heading)
    
    rule2_text = Paragraph(
        "<b>Requirement:</b> The transaction initiator and approver must be different individuals. "
        "Records where 'created_by' equals 'approved_by' violate segregation of duties and must be "
        "flagged for review. <b>Severity: High</b>",
        styles['Justify']
    )
    elements.append(rule2_text)
    elements.append(Spacer(1, 0.2*inch))
    
    # Rule 3
    rule3_heading = Paragraph("Rule 3: Audit Trail Completeness", heading_style)
    elements.append(rule3_heading)
    
    rule3_text = Paragraph(
        "<b>Requirement:</b> All financial records must have complete audit trails including "
        "'created_at', 'created_by', 'modified_at', and 'modified_by' fields. Records with missing "
        "audit fields must be flagged. <b>Severity: High</b>",
        styles['Justify']
    )
    elements.append(rule3_text)
    
    doc.build(elements)
    
    print(f"SOX policy created: {output_path}")
    print("\nThis policy contains 3 testable rules:")
    print("1. Dual authorization for transactions > $25,000 (Critical severity)")
    print("2. Segregation of duties violation (High severity)")
    print("3. Incomplete audit trail (High severity)")


def main():
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(
        description="Generate sample compliance policy PDFs for testing"
    )
    parser.add_argument(
        "--type",
        choices=["aml", "gdpr", "sox", "all"],
        default="aml",
        help="Type of policy to generate (default: aml)"
    )
    
    args = parser.parse_args()
    
    print("=== PolicySentinel Sample Policy Generator ===\n")
    
    if args.type == "aml" or args.type == "all":
        create_aml_policy()
        print()
    
    if args.type == "gdpr" or args.type == "all":
        create_gdpr_policy()
        print()
    
    if args.type == "sox" or args.type == "all":
        create_sox_policy()
        print()
    
    print("\n=== Next Steps ===")
    print("1. Start the backend: uvicorn src.main:app --reload")
    print("2. Upload the generated PDF(s) via POST /api/v1/policies/upload")
    print("3. The system will extract rules automatically")
    print("4. Run compliance scans to detect violations")


if __name__ == "__main__":
    main()
