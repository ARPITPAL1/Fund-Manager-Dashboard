import hashlib
import uuid
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from analytics_api.models import (
    User, KYCRecord, KYCDocument, CFAApproval, Fund,
    Investment, Transaction, ComplianceCheck, ComplianceAlert,
    AuditLog, SIPSchedule, Notification, SystemUser
)
from analytics_api.ml.train_churn_model import train_and_save_model
from analytics_api.ml.aml_service import perform_compliance_check


def hash_pw(pwd):
    return hashlib.sha256(pwd.encode('utf-8')).hexdigest()


class Command(BaseCommand):
    help = 'Seeds initial mutual fund, investor, transaction, and SIP data into SQL database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Training Random Forest Churn Prediction ML Model..."))
        train_and_save_model()

        self.stdout.write(self.style.NOTICE("Seeding comprehensive financial platform dataset..."))

        # 1. System Users / Admins
        admin_user, _ = User.objects.get_or_create(
            email='admin@fintrend.com',
            defaults={
                'phone': '+91 9876543210',
                'password_hash': hash_pw('Admin@12345'),
                'full_name': 'Chief Investment Officer',
                'date_of_birth': '1982-05-14',
                'role': 'FUND_MANAGER',
                'status': 'ACTIVE',
                'mfa_enabled': True
            }
        )

        compliance_officer, _ = User.objects.get_or_create(
            email='compliance@fintrend.com',
            defaults={
                'phone': '+91 9876543211',
                'password_hash': hash_pw('Compliance@12345'),
                'full_name': 'Senior Compliance Officer',
                'date_of_birth': '1985-09-20',
                'role': 'COMPLIANCE_OFFICER',
                'status': 'ACTIVE'
            }
        )

        # 2. Fund Schemes Catalog
        funds_data = [
            {
                'fund_code': 'FV-BC-001',
                'fund_name': 'FinVista Bluechip Large Cap Fund',
                'fund_house': 'FinVista Asset Management',
                'fund_manager_id': 'FM-01',
                'category': 'EQUITY',
                'risk_level': 'VERY_HIGH',
                'current_nav': 78.45,
                'nav_updated_at': timezone.now().strftime('%Y-%m-%d'),
                'min_investment': 5000.0,
                'min_sip_amount': 1000.0,
                'expense_ratio': 0.72,
                'exit_load_percent': 1.0,
                'exit_load_period_days': 365,
                'inception_date': '2015-03-10',
                'aum_crores': 2450.80
            },
            {
                'fund_code': 'APX-MC-002',
                'fund_name': 'Apex Midcap Opportunities Fund',
                'fund_house': 'Apex Capital AMC',
                'fund_manager_id': 'FM-02',
                'category': 'EQUITY',
                'risk_level': 'VERY_HIGH',
                'current_nav': 112.30,
                'nav_updated_at': timezone.now().strftime('%Y-%m-%d'),
                'min_investment': 5000.0,
                'min_sip_amount': 1000.0,
                'expense_ratio': 0.85,
                'exit_load_percent': 1.0,
                'exit_load_period_days': 365,
                'inception_date': '2017-08-22',
                'aum_crores': 1890.40
            },
            {
                'fund_code': 'PRM-HY-003',
                'fund_name': 'Premier Dynamic Balanced Hybrid Fund',
                'fund_house': 'Premier Mutual Fund',
                'fund_manager_id': 'FM-01',
                'category': 'HYBRID',
                'risk_level': 'MODERATE',
                'current_nav': 45.60,
                'nav_updated_at': timezone.now().strftime('%Y-%m-%d'),
                'min_investment': 5000.0,
                'min_sip_amount': 500.0,
                'expense_ratio': 0.65,
                'exit_load_percent': 1.0,
                'exit_load_period_days': 180,
                'inception_date': '2016-11-05',
                'aum_crores': 1240.20
            },
            {
                'fund_code': 'STB-DB-004',
                'fund_name': 'Stability Corporate Bond Debt Fund',
                'fund_house': 'Stability Fund House',
                'fund_manager_id': 'FM-03',
                'category': 'DEBT',
                'risk_level': 'LOW',
                'current_nav': 24.15,
                'nav_updated_at': timezone.now().strftime('%Y-%m-%d'),
                'min_investment': 10000.0,
                'min_sip_amount': 1000.0,
                'expense_ratio': 0.38,
                'exit_load_percent': 0.0,
                'exit_load_period_days': 0,
                'inception_date': '2014-01-15',
                'aum_crores': 3100.50
            },
            {
                'fund_code': 'TAX-EL-005',
                'fund_name': 'TaxAdvantage ELSS Tax Saver Fund',
                'fund_house': 'FinVista Asset Management',
                'fund_manager_id': 'FM-02',
                'category': 'ELSS',
                'risk_level': 'VERY_HIGH',
                'current_nav': 96.80,
                'nav_updated_at': timezone.now().strftime('%Y-%m-%d'),
                'min_investment': 500.0,
                'min_sip_amount': 500.0,
                'expense_ratio': 0.78,
                'exit_load_percent': 0.0,
                'exit_load_period_days': 1095,
                'inception_date': '2018-04-01',
                'aum_crores': 850.15
            }
        ]

        created_funds = []
        for f_data in funds_data:
            fund_obj, _ = Fund.objects.update_or_create(
                fund_code=f_data['fund_code'],
                defaults=f_data
            )
            created_funds.append(fund_obj)

        # 3. Investors & KYC
        investor_profiles = [
            ('Aarav Mehta', 'aarav.mehta@example.com', '+91 9811122334', 'ABCDE1234F', '123456789012', 'Mumbai, Maharashtra'),
            ('Diya Sharma', 'diya.sharma@example.com', '+91 9822233445', 'BCDEF2345G', '234567890123', 'Bengaluru, Karnataka'),
            ('Rohan Verma', 'rohan.verma@example.com', '+91 9833344556', 'CDEFG3456H', '345678901234', 'New Delhi, Delhi'),
            ('Ananya Iyer', 'ananya.iyer@example.com', '+91 9844455667', 'DEFGH4567I', '456789012345', 'Chennai, Tamil Nadu'),
            ('Vikram Patel', 'vikram.patel@example.com', '+91 9855566778', 'EFGHI5678J', '567890123456', 'Ahmedabad, Gujarat'),
            ('Neha Reddy', 'neha.reddy@example.com', '+91 9866677889', 'FGHIJ6789K', '678901234567', 'Hyderabad, Telangana'),
            ('Siddharth Joshi', 'siddharth.joshi@example.com', '+91 9877788990', 'GHIJK7890L', '789012345678', 'Pune, Maharashtra'),
            ('Pooja Nair', 'pooja.nair@example.com', '+91 9888899001', 'HIJKL8901M', '890123456789', 'Kochi, Kerala'),
            ('Kabir Singhania', 'kabir.singhania@hni.com', '+91 9899900112', 'IJKLM9012N', '901234567890', 'South Mumbai, Maharashtra'),
            ('Ishita Deshmukh', 'ishita.deshmukh@example.com', '+91 9800011223', 'JKLMN0123O', '012345678901', 'Nagpur, Maharashtra'),
        ]

        created_investors = []
        now = timezone.now()

        for name, email, phone, pan, aadhaar, addr in investor_profiles:
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    'phone': phone,
                    'password_hash': hash_pw('Investor@12345'),
                    'full_name': name,
                    'date_of_birth': '1992-07-18',
                    'role': 'INVESTOR',
                    'status': 'ACTIVE',
                    'created_at': now - timedelta(days=random.randint(60, 400))
                }
            )
            created_investors.append(user)

            kyc, _ = KYCRecord.objects.get_or_create(
                user=user,
                defaults={
                    'pan_number': pan,
                    'aadhaar_number': aadhaar,
                    'address': addr,
                    'status': 'AUTO_APPROVED',
                    'ai_confidence_score': 0.98,
                    'verified_at': now
                }
            )

        # 4. Investments, SIP Schedules, and Historical Transactions
        for idx, user in enumerate(created_investors):
            chosen_fund = created_funds[idx % len(created_funds)]
            
            # SIP Mandates
            sip_status = 'ACTIVE'
            if idx == 4: # Vikram Patel cancelled SIP
                sip_status = 'CANCELLED'
            elif idx == 6: # Siddharth paused SIP
                sip_status = 'PAUSED'

            sip = SIPSchedule.objects.create(
                investor_name=user.full_name,
                fund_name=chosen_fund.fund_name,
                amount=15000.0 if 'HNI' not in user.email else 150000.0,
                date=5 + (idx * 2) % 20,
                status=sip_status,
                next_debit='2026-10-10' if sip_status == 'ACTIVE' else 'N/A'
            )

            # Investment Holdings
            inv_amount = 250000.0 if 'HNI' not in user.email else 50000000.0
            units = round(inv_amount / chosen_fund.current_nav, 4)
            inv = Investment.objects.create(
                user=user,
                fund=chosen_fund,
                fund_name=chosen_fund.fund_name,
                investment_type='SIP' if sip_status == 'ACTIVE' else 'LUMPSUM',
                amount=inv_amount,
                frequency='MONTHLY',
                sip_date=sip.date,
                mandate_status=sip_status,
                start_date='2025-06-01',
                total_units=units,
                current_value=inv_amount * 1.18, # +18% gain
                status='ACTIVE'
            )

            # Historical Transactions
            # A) Initial purchase
            t1 = Transaction.objects.create(
                user=user,
                investment=inv,
                fund=chosen_fund,
                fund_name=chosen_fund.fund_name,
                transaction_type='PURCHASE',
                amount=inv_amount,
                nav_applied=chosen_fund.current_nav,
                units=units,
                status='SETTLED',
                payment_ref=f"TXN-{uuid.uuid4().hex[:8].upper()}",
                settlement_date='2025-06-02',
                folio_number=f"FOLIO-{user.id[-6:]}",
                created_at=now - timedelta(days=120),
                settled_at=now - timedelta(days=119)
            )
            perform_compliance_check(t1, user)

            # B) Additional SIP debits or redemptions
            if idx == 8: # Kabir Singhania HNI with a massive transaction triggering AML
                t_aml = Transaction.objects.create(
                    user=user,
                    investment=inv,
                    fund=chosen_fund,
                    fund_name=chosen_fund.fund_name,
                    transaction_type='PURCHASE',
                    amount=350000000.0, # ₹35 Cr
                    nav_applied=chosen_fund.current_nav,
                    units=350000000.0 / chosen_fund.current_nav,
                    status='SETTLED',
                    payment_ref=f"TXN-{uuid.uuid4().hex[:8].upper()}",
                    settlement_date='2026-06-15',
                    folio_number=f"FOLIO-{user.id[-6:]}",
                    created_at=now - timedelta(days=15),
                    settled_at=now - timedelta(days=14)
                )
                perform_compliance_check(t_aml, user)
            
            if idx in [4, 6]: # Churn candidates with redemptions
                t_red = Transaction.objects.create(
                    user=user,
                    investment=inv,
                    fund=chosen_fund,
                    fund_name=chosen_fund.fund_name,
                    transaction_type='REDEMPTION',
                    amount=inv_amount * 0.75,
                    nav_applied=chosen_fund.current_nav,
                    units=units * 0.75,
                    status='SETTLED',
                    payment_ref=f"TXN-{uuid.uuid4().hex[:8].upper()}",
                    settlement_date='2026-07-01',
                    folio_number=f"FOLIO-{user.id[-6:]}",
                    created_at=now - timedelta(days=95),
                    settled_at=now - timedelta(days=94)
                )
                perform_compliance_check(t_red, user)

        # 5. System Users
        sys_users = [
            ('Rajesh Sharma', 'rajesh.sharma@fintrend.com', 'Senior Portfolio Manager', 'ACTIVE'),
            ('Kavita Sen', 'kavita.sen@fintrend.com', 'Lead Risk Analyst', 'ACTIVE'),
            ('Suresh Menon', 'suresh.menon@fintrend.com', 'Chief Compliance Officer', 'ACTIVE'),
        ]
        for s_name, s_email, s_role, s_st in sys_users:
            SystemUser.objects.get_or_create(
                email=s_email,
                defaults={'full_name': s_name, 'role': s_role, 'status': s_st}
            )

        self.stdout.write(self.style.SUCCESS("FinTrend Database seeded successfully with Funds, KYC folios, SIP mandates, and AML checks!"))
