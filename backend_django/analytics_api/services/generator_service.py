import random
import uuid
from django.utils import timezone
from ..models import User, Fund, Investment, Transaction, ComplianceCheck, ComplianceAlert
from ..ml.aml_service import perform_compliance_check


def simulate_random_transaction():
    """
    Generates a realistic simulated investment or redemption transaction and runs AML checks.
    """
    investors = list(User.objects.filter(role='INVESTOR'))
    funds = list(Fund.objects.filter(is_active=True))
    
    if not investors or not funds:
        return None

    user = random.choice(investors)
    fund = random.choice(funds)

    txn_types = ['PURCHASE', 'SIP_AUTO', 'REDEMPTION', 'SWITCH_IN']
    weights = [0.55, 0.30, 0.12, 0.03]
    txn_type = random.choices(txn_types, weights=weights)[0]

    # Generate amounts: common retail (₹5,000 - ₹50,000) or occasional HNI (>₹1 Cr, or rare >₹30 Cr)
    rand_val = random.random()
    if rand_val < 0.85:
        amount = random.randint(5000, 250000)
    elif rand_val < 0.98:
        amount = random.randint(1000000, 50000000) # ₹10L - ₹5 Cr
    else:
        amount = random.randint(310000000, 450000000) # ₹31 Cr - ₹45 Cr (triggers AML)

    nav = fund.current_nav
    units = round(amount / nav, 4) if nav > 0 else 0.0

    # Ensure an investment object exists
    inv, created = Investment.objects.get_or_create(
        user=user,
        fund=fund,
        defaults={
            'fund_name': fund.fund_name,
            'investment_type': 'SIP' if txn_type == 'SIP_AUTO' else 'LUMPSUM',
            'amount': amount,
            'frequency': 'MONTHLY' if txn_type == 'SIP_AUTO' else None,
            'start_date': timezone.now().strftime('%Y-%m-%d'),
            'total_units': units,
            'current_value': amount,
            'status': 'ACTIVE'
        }
    )
    if not created:
        if txn_type in ['PURCHASE', 'SIP_AUTO', 'SWITCH_IN']:
            inv.total_units += units
            inv.current_value += amount
        elif txn_type == 'REDEMPTION':
            inv.total_units = max(0.0, inv.total_units - units)
            inv.current_value = max(0.0, inv.current_value - amount)
        inv.save()

    txn = Transaction.objects.create(
        user=user,
        investment=inv,
        fund=fund,
        fund_name=fund.fund_name,
        transaction_type=txn_type,
        amount=amount,
        nav_applied=nav,
        units=units,
        status='SETTLED',
        payment_ref=f"PAY-{uuid.uuid4().hex[:8].upper()}",
        payment_mode='UPI' if amount < 100000 else 'NEFT/RTGS',
        settlement_date=timezone.now().strftime('%Y-%m-%d'),
        folio_number=f"FOLIO-{user.id[-6:]}",
        created_at=timezone.now(),
        settled_at=timezone.now()
    )

    # Perform automated AML check
    check = perform_compliance_check(txn, user)

    return {
        "id": txn.id,
        "userName": user.full_name,
        "fundName": fund.fund_name,
        "transactionType": txn_type,
        "amount": amount,
        "status": txn.status,
        "created_at": txn.created_at.isoformat(),
        "complianceResult": check.result if check else 'CLEAR'
    }
