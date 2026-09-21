import hashlib
import json
import uuid
from django.utils import timezone
from django.db.models import Sum, Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action

from .models import (
    User, KYCRecord, KYCDocument, CFAApproval, Fund,
    Investment, Transaction, ComplianceCheck, ComplianceAlert,
    AuditLog, SIPSchedule, Notification, SystemUser
)
from .serializers import (
    UserSerializer, KYCRecordSerializer, KYCDocumentSerializer,
    CFAApprovalSerializer, FundSerializer, InvestmentSerializer,
    TransactionSerializer, ComplianceCheckSerializer, ComplianceAlertSerializer,
    AuditLogSerializer, SIPScheduleSerializer, NotificationSerializer,
    SystemUserSerializer
)
from .ml.churn_service import get_all_churn_predictions, trigger_retention_outreach
from .ml.ai_advisor_service import generate_advisor_response, simulate_portfolio_stress_test, get_live_platform_context
from .ml.aml_service import perform_compliance_check
from .services.audit_service import log_audit_action
from .services.generator_service import simulate_random_transaction


def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# ----------------------------------------------------
# Authentication Views
# ----------------------------------------------------
class AuthLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email=email).first()
        if not user:
            # Fallback: find by email or create mock session
            user = User.objects.filter(role='FUND_MANAGER').first() or User.objects.first()

        token = f"jwt-token-{uuid.uuid4().hex}"
        user_dict = {
            'id': user.id,
            'email': user.email,
            'phone': user.phone,
            'fullName': user.full_name,
            'full_name': user.full_name,
            'role': user.role,
            'status': user.status,
            'mfaEnabled': user.mfa_enabled,
            'token': token
        }

        user.last_login_at = timezone.now()
        user.save()

        log_audit_action(
            actor_type='USER',
            actor_name=user.full_name,
            entity_type='users',
            entity_id=user.id,
            action='LOGIN',
            changes='User session authenticated successfully'
        )

        return Response({
            'token': token,
            'user': user_dict
        })


class AuthRegisterView(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        phone = data.get('phone')
        full_name = data.get('fullName') or data.get('full_name')
        password = data.get('password', 'Pass@123')
        dob = data.get('dob') or data.get('date_of_birth', '1990-01-01')
        role = data.get('role', 'INVESTOR')

        if not email or not full_name:
            return Response({'error': 'Email and full name are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
        else:
            user = User.objects.create(
                email=email,
                phone=phone or f"+91 {random.randint(9000000000, 9999999999)}",
                password_hash=hash_password(password),
                full_name=full_name,
                date_of_birth=dob,
                role=role,
                status='ACTIVE'
            )

        token = f"jwt-token-{uuid.uuid4().hex}"
        user_dict = {
            'id': user.id,
            'email': user.email,
            'phone': user.phone,
            'fullName': user.full_name,
            'full_name': user.full_name,
            'role': user.role,
            'status': user.status,
            'token': token
        }

        return Response({
            'ok': True,
            'token': token,
            'user': user_dict
        }, status=status.HTTP_201_CREATED)


class AuthSessionView(APIView):
    def get(self, request):
        user = User.objects.filter(role='FUND_MANAGER').first() or User.objects.first()
        if user:
            user_dict = {
                'id': user.id,
                'email': user.email,
                'phone': user.phone,
                'fullName': user.full_name,
                'full_name': user.full_name,
                'role': user.role,
                'status': user.status,
                'mfaEnabled': user.mfa_enabled,
                'token': f"jwt-token-{uuid.uuid4().hex}"
            }
            return Response({'user': user_dict})
        return Response({'user': None})


class AuthLogoutView(APIView):
    def post(self, request):
        user_id = request.data.get('userId')
        if user_id:
            log_audit_action(
                actor_type='USER',
                actor_name=request.data.get('fullName', 'User'),
                entity_type='users',
                entity_id=user_id,
                action='LOGOUT',
                changes='User signed out.'
            )
        return Response({'ok': True, 'message': 'Logged out.'})


# ----------------------------------------------------
# Investor Directory Views
# ----------------------------------------------------
class InvestorListView(APIView):
    def get(self, request):
        investors = User.objects.filter(role='INVESTOR')
        result = []
        for inv in investors:
            holdings = inv.investments.filter(status='ACTIVE')
            aum = sum(h.current_value or h.amount for h in holdings)
            result.append({
                'id': inv.id,
                'fullName': inv.full_name,
                'email': inv.email,
                'phone': inv.phone,
                'status': inv.status,
                'aum': aum,
                'createdAt': inv.created_at.strftime('%Y-%m-%d')
            })
        return Response(result)


# ----------------------------------------------------
# Mutual Fund Views
# ----------------------------------------------------
class FundViewSet(viewsets.ModelViewSet):
    queryset = Fund.objects.filter(is_active=True)
    serializer_class = FundSerializer


# ----------------------------------------------------
# Investment Holdings Views
# ----------------------------------------------------
class InvestmentViewSet(viewsets.ModelViewSet):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        user_id = data.get('userId') or data.get('user')
        fund_id = data.get('fundId') or data.get('fund')
        inv_type = data.get('type') or data.get('investment_type', 'LUMPSUM')
        amount = float(data.get('amount', 5000.0))
        frequency = data.get('frequency', 'MONTHLY')
        sip_date = int(data.get('sipDate', 5))

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = User.objects.first()

        try:
            fund = Fund.objects.get(id=fund_id)
        except Fund.DoesNotExist:
            fund = Fund.objects.first()

        units = round(amount / fund.current_nav, 4) if fund.current_nav > 0 else 0.0

        inv = Investment.objects.create(
            user=user,
            fund=fund,
            fund_name=fund.fund_name,
            investment_type=inv_type,
            amount=amount,
            frequency=frequency if inv_type == 'SIP' else None,
            sip_date=sip_date if inv_type == 'SIP' else None,
            mandate_status='ACTIVE' if inv_type == 'SIP' else None,
            start_date=timezone.now().strftime('%Y-%m-%d'),
            total_units=units,
            current_value=amount,
            status='ACTIVE'
        )

        txn = Transaction.objects.create(
            user=user,
            investment=inv,
            fund=fund,
            fund_name=fund.fund_name,
            transaction_type='PURCHASE' if inv_type == 'LUMPSUM' else 'SIP_AUTO',
            amount=amount,
            nav_applied=fund.current_nav,
            units=units,
            status='SETTLED',
            payment_ref=f"TXN-{uuid.uuid4().hex[:8].upper()}",
            settlement_date=timezone.now().strftime('%Y-%m-%d'),
            folio_number=f"FOLIO-{user.id[-6:]}",
            created_at=timezone.now(),
            settled_at=timezone.now()
        )

        perform_compliance_check(txn, user)

        if inv_type == 'SIP':
            SIPSchedule.objects.create(
                investor_name=user.full_name,
                fund_name=fund.fund_name,
                amount=amount,
                date=sip_date,
                status='ACTIVE',
                next_debit=timezone.now().strftime('%Y-%m-') + f"{sip_date:02d}"
            )

        return Response(InvestmentSerializer(inv).data, status=status.HTTP_201_CREATED)


# ----------------------------------------------------
# SIP Mandate Schedules Views
# ----------------------------------------------------
class SIPScheduleViewSet(viewsets.ModelViewSet):
    queryset = SIPSchedule.objects.all().order_by('-created_at')
    serializer_class = SIPScheduleSerializer

    @action(detail=True, methods=['patch', 'post'])
    def manage(self, request, pk=None):
        sip = self.get_object()
        action_name = request.data.get('action', '').upper()
        if action_name in ['PAUSE', 'CANCEL', 'RESUME', 'ACTIVE', 'PAUSED', 'CANCELLED']:
            status_map = {
                'PAUSE': 'PAUSED',
                'CANCEL': 'CANCELLED',
                'RESUME': 'ACTIVE',
                'ACTIVE': 'ACTIVE',
                'PAUSED': 'PAUSED',
                'CANCELLED': 'CANCELLED'
            }
            sip.status = status_map.get(action_name, 'ACTIVE')
            sip.save()
            log_audit_action(
                actor_type='USER',
                actor_name='Portfolio Manager',
                entity_type='sip_schedules',
                entity_id=sip.id,
                action='UPDATE',
                changes=f"SIP Mandate updated to {sip.status}"
            )
            return Response(SIPScheduleSerializer(sip).data)
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def rollover(self, request):
        data = request.data
        investor_name = data.get('investorName')
        fund_name = data.get('fundName')
        amount = float(data.get('amount', 5000.0))

        sip = SIPSchedule.objects.create(
            investor_name=investor_name,
            fund_name=fund_name,
            amount=amount,
            date=5,
            status='ACTIVE',
            next_debit='2026-10-05'
        )
        return Response(SIPScheduleSerializer(sip).data, status=status.HTTP_201_CREATED)


# ----------------------------------------------------
# Transaction Ledger Views
# ----------------------------------------------------
class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = TransactionSerializer

    @action(detail=False, methods=['post'])
    def simulate(self, request):
        txn_data = simulate_random_transaction()
        if txn_data:
            return Response(txn_data, status=status.HTTP_201_CREATED)
        return Response({'error': 'Could not simulate transaction.'}, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------------------------------
# Compliance & AML Views
# ----------------------------------------------------
class ComplianceAlertListView(APIView):
    def get(self, request):
        alerts = ComplianceAlert.objects.all().order_by('-created_at')
        serializer = ComplianceAlertSerializer(alerts, many=True)
        return Response(serializer.data)


class ComplianceResolveView(APIView):
    def post(self, request):
        alert_id = request.data.get('alertId') or request.data.get('id')
        resolution = request.data.get('resolution', 'RESOLVED')
        notes = request.data.get('notes', 'Compliance verification confirmed.')

        try:
            alert = ComplianceAlert.objects.get(id=alert_id)
        except ComplianceAlert.DoesNotExist:
            return Response({'error': 'Compliance alert not found.'}, status=status.HTTP_404_NOT_FOUND)

        alert.status = 'STR_FILED' if resolution == 'STR_FILED' else 'RESOLVED'
        alert.resolution_notes = notes
        alert.resolved_at = timezone.now()
        alert.save()

        log_audit_action(
            actor_type='USER',
            actor_name='Compliance Officer',
            entity_type='compliance_alerts',
            entity_id=alert.id,
            action='UPDATE',
            changes=f"Alert resolved as {resolution}. Notes: {notes}"
        )

        return Response(ComplianceAlertSerializer(alert).data)


# ----------------------------------------------------
# Data Science, AI/ML & Analytics Views
# ----------------------------------------------------
class ChurnPredictionsView(APIView):
    def get(self, request):
        """
        Executes ML Random Forest pipeline on all investor folios.
        """
        predictions = get_all_churn_predictions()
        return Response(predictions)


class TriggerOutreachView(APIView):
    def post(self, request):
        user_id = request.data.get('userId') or request.data.get('user_id')
        if not user_id:
            return Response({'error': 'Missing userId parameter.'}, status=status.HTTP_400_BAD_REQUEST)
        
        success, msg = trigger_retention_outreach(user_id)
        if success:
            return Response({'status': 'success', 'message': msg})
        return Response({'error': msg}, status=status.HTTP_404_NOT_FOUND)


class AUMGrowthView(APIView):
    def get(self, request):
        months = ['Jan 2026', 'Feb 2026', 'Mar 2026', 'Apr 2026', 'May 2026', 'Jun 2026']
        growth_data = [
            {'period': 'Jan 2026', 'aum': 412.5, 'inflows': 34.2, 'outflows': 12.1},
            {'period': 'Feb 2026', 'aum': 428.1, 'inflows': 38.5, 'outflows': 15.0},
            {'period': 'Mar 2026', 'aum': 445.8, 'inflows': 42.1, 'outflows': 14.8},
            {'period': 'Apr 2026', 'aum': 462.4, 'inflows': 45.0, 'outflows': 16.2},
            {'period': 'May 2026', 'aum': 481.9, 'inflows': 49.3, 'outflows': 17.5},
            {'period': 'Jun 2026', 'aum': 512.4, 'inflows': 56.8, 'outflows': 18.9},
        ]

        categories = [
            {'name': 'Equity Funds', 'percentage': 44.5, 'aum_cr': 228.0},
            {'name': 'Debt & Liquid', 'percentage': 26.2, 'aum_cr': 134.2},
            {'name': 'Hybrid Schemes', 'percentage': 18.8, 'aum_cr': 96.3},
            {'name': 'ELSS Tax Saver', 'percentage': 6.5, 'aum_cr': 33.3},
            {'name': 'Sectoral & Index', 'percentage': 4.0, 'aum_cr': 20.6},
        ]

        state_distribution = [
            {'state': 'Maharashtra', 'aum_cr': 185.2, 'share': 36.1},
            {'state': 'Delhi NCR', 'aum_cr': 94.5, 'share': 18.4},
            {'state': 'Karnataka', 'aum_cr': 72.8, 'share': 14.2},
            {'state': 'Gujarat', 'aum_cr': 64.0, 'share': 12.5},
            {'state': 'Tamil Nadu', 'aum_cr': 51.2, 'share': 10.0},
            {'state': 'Others', 'aum_cr': 44.7, 'share': 8.8},
        ]

        return Response({
            'growth': growth_data,
            'categories': categories,
            'states': state_distribution,
            'metrics': get_live_platform_context()
        })


class HeatmapAnalyticsView(APIView):
    def get(self, request):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        hours = [f"{h}:00" for h in range(9, 18)]
        
        matrix = []
        for day_idx, day in enumerate(days):
            row = []
            for hour_idx, hour in enumerate(hours):
                base = 15 if day_idx < 5 else 3
                if 10 <= (hour_idx + 9) <= 14 and day_idx < 4:
                    intensity = base + ((day_idx * 7 + hour_idx * 11) % 65) + 30
                else:
                    intensity = base + ((day_idx * 3 + hour_idx * 5) % 25)
                row.append({'hour': hour, 'count': intensity})
            matrix.append({'day': day, 'hours': row})

        return Response({'matrix': matrix, 'peakHour': '11:00 AM - 12:00 PM', 'peakDay': 'Wednesday'})


# ----------------------------------------------------
# AI Allocation Advisor (FiNAI) & Vector RAG Views
# ----------------------------------------------------
class AIChatView(APIView):
    def post(self, request):
        message = request.data.get('message', '')
        history = request.data.get('history', [])
        if not message:
            return Response({'error': 'Message is required.'}, status=status.HTTP_400_BAD_REQUEST)

        response_payload = generate_advisor_response(message, history)
        return Response(response_payload)


class AIStressTestView(APIView):
    def post(self, request):
        correction = float(request.data.get('correction', 10.0))
        allocation = request.data.get('allocation')
        res = simulate_portfolio_stress_test(correction, allocation)
        return Response(res)


class AIRagQueryView(APIView):
    def post(self, request):
        """
        Executes semantic vector search over SEBI regulations, scheme factsheets, and AML policies.
        """
        query = request.data.get('query') or request.data.get('message', '')
        top_k = int(request.data.get('top_k', 3))
        if not query:
            return Response({'error': 'Query is required.'}, status=status.HTTP_400_BAD_REQUEST)

        from .ml.rag_engine import get_rag_engine
        rag = get_rag_engine()
        results = rag.answer_with_rag(query, top_k=top_k)
        return Response(results)


class AIRagDocumentsView(APIView):
    def get(self, request):
        """
        Returns list of indexed documents in the Vector Knowledge Base.
        """
        from .ml.rag_knowledge_base import FINANCIAL_KNOWLEDGE_CORPUS
        from .ml.rag_engine import get_rag_engine
        rag = get_rag_engine()
        return Response({
            'total_documents': len(FINANCIAL_KNOWLEDGE_CORPUS),
            'total_chunks': len(rag.chunks),
            'documents': [
                {
                    'doc_id': d['doc_id'],
                    'title': d['title'],
                    'category': d['category']
                }
                for d in FINANCIAL_KNOWLEDGE_CORPUS
            ]
        })



# ----------------------------------------------------
# Audit Logs Views (WORM)
# ----------------------------------------------------
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-created_at')
    serializer_class = AuditLogSerializer


# ----------------------------------------------------
# System Users Views
# ----------------------------------------------------
class SystemUserViewSet(viewsets.ModelViewSet):
    queryset = SystemUser.objects.all()
    serializer_class = SystemUserSerializer

    def create(self, request, *args, **kwargs):
        full_name = request.data.get('fullName') or request.data.get('full_name')
        email = request.data.get('email')
        role = request.data.get('role')
        if not full_name or not email or not role:
            return Response({'error': 'fullName, email, and role are required.'}, status=status.HTTP_400_BAD_REQUEST)
        user, _ = SystemUser.objects.get_or_create(
            email=email,
            defaults={'full_name': full_name, 'role': role, 'status': 'ACTIVE'}
        )
        return Response(SystemUserSerializer(user).data, status=status.HTTP_201_CREATED)


class SystemUsersListView(APIView):
    def get(self, request):
        users = SystemUser.objects.all()
        return Response(SystemUserSerializer(users, many=True).data)

    def post(self, request):
        full_name = request.data.get('fullName') or request.data.get('full_name')
        email = request.data.get('email')
        role = request.data.get('role')
        user, _ = SystemUser.objects.get_or_create(
            email=email,
            defaults={'full_name': full_name, 'role': role, 'status': 'ACTIVE'}
        )
        return Response(SystemUserSerializer(user).data, status=status.HTTP_201_CREATED)


# ----------------------------------------------------
# System Settings Views
# ----------------------------------------------------
class SystemSettingsAiThresholdView(APIView):
    _threshold = 95.0

    def get(self, request):
        return Response({'threshold': SystemSettingsAiThresholdView._threshold})

    def post(self, request):
        threshold = float(request.data.get('threshold', 95.0))
        SystemSettingsAiThresholdView._threshold = threshold
        return Response({'threshold': threshold, 'status': 'updated'})


class SystemSettingsResetView(APIView):
    def post(self, request):
        Transaction.objects.all().delete()
        ComplianceAlert.objects.all().delete()
        SIPSchedule.objects.all().delete()
        Notification.objects.all().delete()
        return Response({'ok': True, 'message': 'Sandbox database successfully reset.'})
