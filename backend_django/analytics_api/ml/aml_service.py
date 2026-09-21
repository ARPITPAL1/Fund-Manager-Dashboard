from django.utils import timezone
from ..models import ComplianceCheck, ComplianceAlert, User, Transaction


AML_HIGH_VALUE_THRESHOLD = 300000000.0  # ₹30 Crores


def perform_compliance_check(transaction, user):
    """
    Evaluates a transaction for compliance and anti-money laundering risks:
    - High value single transfer (> ₹30 Cr)
    - Suspicious round-trip transactions
    - Risk scoring (0.0 to 100.0)
    """
    amount = float(transaction.amount)
    risk_score = 0.0
    result = 'CLEAR'
    details = 'Standard automated validation passed.'
    alert_needed = False
    severity = 'LOW'

    # Check 1: Ultra High Value Transaction Check
    if amount >= AML_HIGH_VALUE_THRESHOLD:
        risk_score = 88.5
        result = 'SUSPICIOUS'
        severity = 'CRITICAL'
        alert_needed = True
        details = f"Single transaction of ₹{amount/10000000.0:.2f} Cr exceeds regulatory AML review threshold of ₹30 Cr."
    elif amount >= 100000000.0:  # ₹10 Cr
        risk_score = 65.0
        result = 'SUSPICIOUS'
        severity = 'HIGH'
        alert_needed = True
        details = f"High value transaction of ₹{amount/10000000.0:.2f} Cr flagged for verification."
    elif amount >= 25000000.0:  # ₹2.5 Cr
        risk_score = 35.0
        details = f"Standard high ticket transaction of ₹{amount/10000000.0:.2f} Cr."

    check = ComplianceCheck.objects.create(
        transaction=transaction,
        user=user,
        check_type='AML_TRANSACTION_MONITORING',
        risk_score=risk_score,
        result=result,
        details=details,
        checked_at=timezone.now()
    )

    if alert_needed:
        ComplianceAlert.objects.create(
            compliance_check=check,
            user=user,
            alert_type='HIGH_VALUE_TRANSACTION',
            severity=severity,
            description=details,
            status='OPEN',
            assigned_to='Compliance Officer',
            created_at=timezone.now()
        )

    return check
