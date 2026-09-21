import uuid
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


def generate_custom_id(prefix='id_'):
    return f"{prefix}{uuid.uuid4().hex[:12]}"


class User(models.Model):
    ROLE_CHOICES = [
        ('INVESTOR', 'Investor'),
        ('COMPLIANCE_OFFICER', 'Compliance Officer'),
        ('ANALYST', 'Analyst'),
        ('FUND_MANAGER', 'Fund Manager'),
    ]
    STATUS_CHOICES = [
        ('PENDING_VERIFICATION', 'Pending Verification'),
        ('VERIFIED', 'Verified'),
        ('KYC_SUBMITTED', 'KYC Submitted'),
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended'),
        ('DEACTIVATED', 'Deactivated'),
    ]

    id = models.CharField(max_length=64, primary_key=True, default=generate_custom_id)
    email = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=64, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.CharField(max_length=64)
    role = models.CharField(max_length=64, choices=ROLE_CHOICES, default='INVESTOR')
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default='PENDING_VERIFICATION')
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=255, blank=True, null=True)
    device_fingerprint = models.CharField(max_length=255, blank=True, null=True)
    last_login_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.full_name} ({self.email})"


class KYCRecord(models.Model):
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('AI_PROCESSING', 'AI Processing'),
        ('AUTO_APPROVED', 'Auto Approved'),
        ('ESCALATED', 'Escalated'),
        ('COMPLIANCE_APPROVED', 'Compliance Approved'),
        ('REJECTED', 'Rejected'),
    ]

    id = models.CharField(max_length=64, primary_key=True, default=generate_custom_id)
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='kyc_records')
    pan_number = models.CharField(max_length=255)
    aadhaar_number = models.CharField(max_length=255)
    address = models.TextField()
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default='SUBMITTED')
    ai_confidence_score = models.FloatField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    verified_by = models.CharField(max_length=64, blank=True, null=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    attempt_number = models.IntegerField(default=1)

    class Meta:
        db_table = 'kyc_records'
        indexes = [
            models.Index(fields=['user'], name='idx_kyc_records_user_id'),
        ]


class KYCDocument(models.Model):
    DOC_CHOICES = [
        ('PAN', 'PAN Card'),
        ('AADHAAR', 'Aadhaar Card'),
        ('ADDRESS_PROOF', 'Address Proof'),
        ('PHOTOGRAPH', 'Photograph'),
        ('BANK_STATEMENT', 'Bank Statement'),
    ]

    id = models.CharField(max_length=64, primary_key=True, default=generate_custom_id)
    kyc_record = models.ForeignKey(KYCRecord, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=64, choices=DOC_CHOICES)
    file_path = models.CharField(max_length=512)
    file_hash = models.CharField(max_length=255)
    file_size_bytes = models.IntegerField()
    mime_type = models.CharField(max_length=64)
    ocr_extracted_data = models.TextField(blank=True, null=True)
    ai_authenticity_score = models.FloatField(blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'kyc_documents'
        indexes = [
            models.Index(fields=['kyc_record'], name='idx_kyc_docs_record_id'),
        ]


class CFAApproval(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    ]

    id = models.CharField(max_length=64, primary_key=True, default=generate_custom_id)
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='cfa_approvals')
    kyc_record = models.ForeignKey(KYCRecord, on_delete=models.RESTRICT, related_name='cfa_approvals')
    cfa_approval_code = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default='PENDING')
    approved_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'cfa_approvals'


class Fund(models.Model):
    CATEGORY_CHOICES = [
        ('EQUITY', 'Equity'),
        ('DEBT', 'Debt'),
        ('HYBRID', 'Hybrid'),
        ('ELSS', 'ELSS'),
        ('INDEX', 'Index'),
        ('LIQUID', 'Liquid'),
        ('SECTORAL', 'Sectoral'),
    ]
    RISK_CHOICES = [
        ('LOW', 'Low'),
        ('MODERATE', 'Moderate'),
        ('HIGH', 'High'),
        ('VERY_HIGH', 'Very High'),
    ]

    id = models.CharField(max_length=64, primary_key=True, default=generate_custom_id)
    fund_code = models.CharField(max_length=64, unique=True)
    fund_name = models.CharField(max_length=255)
    fund_house = models.CharField(max_length=255)
    fund_manager_id = models.CharField(max_length=255)
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES)
    risk_level = models.CharField(max_length=64, choices=RISK_CHOICES)
    current_nav = models.FloatField()
    nav_updated_at = models.CharField(max_length=64)
    min_investment = models.FloatField()
    min_sip_amount = models.FloatField()
    expense_ratio = models.FloatField()
    exit_load_percent = models.FloatField(default=0.0)
    exit_load_period_days = models.IntegerField(default=0)
    inception_date = models.CharField(max_length=64)
    aum_crores = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'funds'

    def __str__(self):
        return f"{self.fund_name} ({self.fund_code})"


class Investment(models.Model):
    TYPE_CHOICES = [
        ('LUMPSUM', 'Lumpsum'),
        ('SIP', 'SIP'),
        ('STP', 'STP'),
        ('SWP', 'SWP'),
    ]

    id = models.CharField(max_length=64, primary_key=True, default=generate_custom_id)
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='investments')
    fund = models.ForeignKey(Fund, on_delete=models.RESTRICT, related_name='investments')
    fund_name = models.CharField(max_length=255)
    investment_type = models.CharField(max_length=64, choices=TYPE_CHOICES)
    amount = models.FloatField()
    frequency = models.CharField(max_length=64, blank=True, null=True)
    sip_date = models.IntegerField(blank=True, null=True)
    mandate_status = models.CharField(max_length=64, blank=True, null=True)
    start_date = models.CharField(max_length=64)
    end_date = models.CharField(max_length=64, blank=True, null=True)
    total_units = models.FloatField(default=0.0)
    current_value = models.FloatField(default=0.0)
    status = models.CharField(max_length=64, default='ACTIVE')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'investments'
        indexes = [
            models.Index(fields=['user'], name='idx_investments_user_id'),
            models.Index(fields=['fund'], name='idx_investments_fund_id'),
        ]


class Transaction(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=generate_custom_id)
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='transactions')
    investment = models.ForeignKey(Investment, on_delete=models.RESTRICT, related_name='transactions', blank=True, null=True)
    fund = models.ForeignKey(Fund, on_delete=models.RESTRICT, related_name='transactions', blank=True, null=True)
    fund_name = models.CharField(max_length=255)
    transaction_type = models.CharField(max_length=64)  # PURCHASE, REDEMPTION, SIP_AUTO, SWITCH_IN, SWITCH_OUT
    amount = models.FloatField()
    nav_applied = models.FloatField(blank=True, null=True)
    units = models.FloatField(blank=True, null=True)
    stamp_duty = models.FloatField(default=0.0)
    exit_load = models.FloatField(default=0.0)
    status = models.CharField(max_length=64, default='INITIATED')  # INITIATED, SETTLED, SUCCESS, FAILED
    payment_ref = models.CharField(max_length=255, blank=True, null=True)
    payment_mode = models.CharField(max_length=255, blank=True, null=True)
    settlement_date = models.CharField(max_length=64, blank=True, null=True)
    folio_number = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    settled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'transactions'
        indexes = [
            models.Index(fields=['user'], name='idx_transactions_user_id'),
            models.Index(fields=['investment'], name='idx_transactions_inv_id'),
        ]


class ComplianceCheck(models.Model):
    RESULT_CHOICES = [
        ('CLEAR', 'Clear'),
        ('SUSPICIOUS', 'Suspicious'),
        ('BLOCKED', 'Blocked'),
    ]

    id = models.CharField(max_length=64, primary_key=True, default=generate_custom_id)
    transaction = models.ForeignKey(Transaction, on_delete=models.RESTRICT, related_name='compliance_checks')
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='compliance_checks')
    check_type = models.CharField(max_length=255)
    risk_score = models.FloatField()
    result = models.CharField(max_length=64, choices=RESULT_CHOICES)
    details = models.TextField()
    checked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'compliance_checks'
        indexes = [
            models.Index(fields=['transaction'], name='idx_comp_checks_txn'),
        ]


class ComplianceAlert(models.Model):
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('UNDER_REVIEW', 'Under Review'),
        ('RESOLVED', 'Resolved'),
        ('STR_FILED', 'STR Filed'),
        ('DISMISSED', 'Dismissed'),
    ]

    id = models.CharField(max_length=64, primary_key=True, default=generate_custom_id)
    compliance_check = models.ForeignKey(ComplianceCheck, on_delete=models.RESTRICT, related_name='alerts', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='compliance_alerts', blank=True, null=True)
    alert_type = models.CharField(max_length=255)
    severity = models.CharField(max_length=64, choices=SEVERITY_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default='OPEN')
    assigned_to = models.CharField(max_length=64, blank=True, null=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'compliance_alerts'
        indexes = [
            models.Index(fields=['user'], name='idx_comp_alerts_user'),
        ]


class AuditLog(models.Model):
    ACTOR_TYPE_CHOICES = [
        ('USER', 'User'),
        ('SYSTEM', 'System'),
        ('AI_ENGINE', 'AI Engine'),
        ('CRON_JOB', 'Cron Job'),
    ]
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('READ', 'Read'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('VERIFY', 'Verify'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
    ]

    id = models.CharField(max_length=64, primary_key=True, default=generate_custom_id)
    actor_id = models.CharField(max_length=64, blank=True, null=True)
    actor_type = models.CharField(max_length=64, choices=ACTOR_TYPE_CHOICES)
    actor_name = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=255)
    entity_id = models.CharField(max_length=64)
    action = models.CharField(max_length=64, choices=ACTION_CHOICES)
    changes = models.TextField(blank=True, null=True)
    ip_address = models.CharField(max_length=64, default='127.0.0.1')
    user_agent = models.CharField(max_length=512, blank=True, null=True)
    session_id = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['actor_id'], name='idx_audit_logs_actor'),
        ]

    def delete(self, *args, **kwargs):
        # Enforce Write-Once-Read-Many (WORM) immutability at application level
        raise ValidationError("WORM Policy Violation: Audit log entries cannot be deleted.")


class SIPSchedule(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=generate_custom_id)
    investor_name = models.CharField(max_length=255)
    fund_name = models.CharField(max_length=255)
    amount = models.FloatField()
    date = models.IntegerField()
    status = models.CharField(max_length=64, default='ACTIVE')  # ACTIVE, PAUSED, CANCELLED
    next_debit = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sip_schedules'


class Notification(models.Model):
    CHANNEL_CHOICES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push'),
        ('IN_APP', 'In-App'),
    ]

    id = models.CharField(max_length=64, primary_key=True, default=generate_custom_id)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', blank=True, null=True)
    channel = models.CharField(max_length=64, choices=CHANNEL_CHOICES)
    type = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['user'], name='idx_notifications_user'),
        ]


class SystemUser(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=generate_custom_id)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    role = models.CharField(max_length=64)
    status = models.CharField(max_length=64, default='ACTIVE')

    class Meta:
        db_table = 'system_users'
