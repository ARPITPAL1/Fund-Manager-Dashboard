import os
import joblib
import pandas as pd
from datetime import datetime, timezone as dt_timezone
from django.utils import timezone
from ..models import User, Transaction, SIPSchedule, Notification, AuditLog
from ..services.audit_service import log_audit_action

# Global model cache
_CHURN_MODEL = None

def get_churn_model():
    global _CHURN_MODEL
    if _CHURN_MODEL is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(script_dir, "churn_model.pkl")
        if not os.path.exists(model_path):
            from .train_churn_model import train_and_save_model
            train_and_save_model()
        _CHURN_MODEL = joblib.load(model_path)
    return _CHURN_MODEL


def compute_investor_churn(user, user_txns, user_sips):
    """
    Extracts behavioral feature vector for an investor and performs ML inference:
    1. Recency (days since last transaction)
    2. Redemption Ratio (total redeemed / total invested)
    3. SIP Mandate Status (0=Active, 1=None, 2=Paused, 3=Cancelled)
    """
    now = timezone.now()
    
    # 1. Feature: Recency
    recency = 365
    if user_txns:
        latest_date = None
        for t in user_txns:
            t_date = t.settled_at or t.created_at
            if latest_date is None or t_date > latest_date:
                latest_date = t_date
        if latest_date:
            recency = max(1, (now - latest_date).days)
    
    # 2. Feature: Redemption Ratio
    total_invested = sum(t.amount for t in user_txns)
    total_redeemed = sum(t.amount for t in user_txns if t.transaction_type == 'REDEMPTION')
    redemption_ratio = round(total_redeemed / total_invested, 4) if total_invested > 0 else 0.0

    # 3. Feature: SIP Status
    sip_status = 1  # None
    if user_sips:
        has_cancelled = any(s.status == 'CANCELLED' for s in user_sips)
        has_paused = any(s.status == 'PAUSED' for s in user_sips)
        if has_cancelled:
            sip_status = 3
        elif has_paused:
            sip_status = 2
        else:
            sip_status = 0

    # ML Inference
    try:
        model = get_churn_model()
        df = pd.DataFrame([{
            "recency": recency,
            "redemption_ratio": redemption_ratio,
            "sip_status": sip_status
        }])
        prob = model.predict_proba(df)[0][1]
    except Exception as e:
        # Fallback heuristic calculation if model error
        prob = 0.15
        if sip_status == 3: prob += 0.5
        if redemption_ratio > 0.5: prob += 0.3
        if recency > 60: prob += 0.2

    # Score bounded between 5% and 95%
    score = int(min(95, max(5, round(prob * 100))))

    # Primary Driver Attribution
    if sip_status == 3:
        primary_driver = 'SIP Mandate Cancelled'
    elif sip_status == 2:
        primary_driver = 'SIP Mandate Paused'
    elif redemption_ratio > 0.5:
        primary_driver = 'High Redemption Volume'
    elif recency > 90:
        primary_driver = 'Activity Recency > 90 Days'
    elif recency > 60:
        primary_driver = 'Activity Recency > 60 Days'
    else:
        primary_driver = 'Stagnant Portfolio'

    risk_category = 'LOW'
    if score > 60:
        risk_category = 'HIGH'
    elif score >= 30:
        risk_category = 'MEDIUM'

    # Compute AUM from active investments or transactions
    user_investments = user.investments.filter(status='ACTIVE')
    aum = sum(inv.current_value or inv.amount for inv in user_investments)

    return {
        "userId": user.id,
        "fullName": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "status": user.status,
        "aum": aum,
        "churnRisk": score,
        "riskCategory": risk_category,
        "primaryDriver": primary_driver,
        "features": {
            "recency_days": recency,
            "redemption_ratio": redemption_ratio,
            "sip_status": sip_status
        }
    }


def get_all_churn_predictions():
    """
    Computes churn risk predictions for all investors using the ML Random Forest Classifier.
    """
    investors = User.objects.filter(role='INVESTOR').prefetch_related('investments')
    all_txns = list(Transaction.objects.all())
    all_sips = list(SIPSchedule.objects.all())

    # Map transactions and sips for fast lookup
    txns_by_user = {}
    for t in all_txns:
        txns_by_user.setdefault(t.user_id, []).append(t)

    sips_by_name = {}
    for s in all_sips:
        sips_by_name.setdefault(s.investor_name, []).append(s)

    predictions = []
    high_risk_count = 0

    for inv in investors:
        u_txns = txns_by_user.get(inv.id, [])
        u_sips = sips_by_name.get(inv.full_name, [])
        pred = compute_investor_churn(inv, u_txns, u_sips)
        if pred["riskCategory"] == "HIGH":
            high_risk_count += 1
        predictions.append(pred)

    # Sort descending by churn risk score
    predictions.sort(key=lambda x: x["churnRisk"], reverse=True)

    # Log to WORM audit ledger
    log_audit_action(
        actor_type='AI_ENGINE',
        actor_name='RandomForest-Churn-Engine-v2',
        entity_type='users',
        entity_id='all',
        action='UPDATE',
        changes=f"Evaluated {len(investors)} folios. Identified {high_risk_count} high-risk churn candidates."
    )

    return predictions


def trigger_retention_outreach(user_id):
    """
    Triggers automated retention campaign: 15bp fee waiver code RELATIONSHIP15 dispatched via email.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return False, "Investor folio not found."

    # Create immutable audit log
    log_audit_action(
        actor_type='USER',
        actor_name='Fund Manager',
        entity_type='users',
        entity_id=user.id,
        action='UPDATE',
        changes=f"Dispatched proactive client retention outreach campaign to {user.full_name}. Granted 15bp fee waiver on next allocation."
    )

    # Record notification
    Notification.objects.create(
        user=user,
        channel='EMAIL',
        type='REMARKETING',
        title='Exclusive Relationship Reward',
        body=f"Dear {user.full_name}, we value your partnership. Enjoy an exclusive 0.15% expense ratio fee waiver on your next scheme allocation. Apply code RELATIONSHIP15 at checkout."
    )

    return True, f"Retention outreach successfully triggered for {user.full_name}."
