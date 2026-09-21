from rest_framework import serializers
from .models import (
    User, KYCRecord, KYCDocument, CFAApproval, Fund,
    Investment, Transaction, ComplianceCheck, ComplianceAlert,
    AuditLog, SIPSchedule, Notification, SystemUser
)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'full_name', 'date_of_birth',
            'role', 'status', 'mfa_enabled', 'mfa_secret',
            'device_fingerprint', 'last_login_at', 'created_at', 'updated_at',
            'password'
        ]
        extra_kwargs = {
            'password_hash': {'write_only': True}
        }


class KYCRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCRecord
        fields = '__all__'


class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = '__all__'


class CFAApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CFAApproval
        fields = '__all__'


class FundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fund
        fields = '__all__'


class InvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class ComplianceCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceCheck
        fields = '__all__'


class ComplianceAlertSerializer(serializers.ModelSerializer):
    userName = serializers.SerializerMethodField()
    panNumber = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceAlert
        fields = [
            'id', 'compliance_check', 'user', 'alert_type', 'severity',
            'description', 'status', 'assigned_to', 'resolved_at',
            'resolution_notes', 'created_at', 'userName', 'panNumber'
        ]

    def get_userName(self, obj):
        return obj.user.full_name if obj.user else 'Unknown User'

    def get_panNumber(self, obj):
        if obj.user:
            kyc = obj.user.kyc_records.first()
            return kyc.pan_number if kyc else 'N/A'
        return 'N/A'


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'


class SIPScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SIPSchedule
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class SystemUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemUser
        fields = '__all__'
