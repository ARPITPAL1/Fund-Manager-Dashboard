from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AuthLoginView, AuthRegisterView, AuthSessionView, AuthLogoutView,
    InvestorListView, FundViewSet, InvestmentViewSet, SIPScheduleViewSet,
    TransactionViewSet, ComplianceAlertListView, ComplianceResolveView,
    ChurnPredictionsView, TriggerOutreachView, AUMGrowthView, HeatmapAnalyticsView,
    AIChatView, AIStressTestView, AIRagQueryView, AIRagDocumentsView,
    AuditLogViewSet, SystemUserViewSet, SystemUsersListView,
    SystemSettingsAiThresholdView, SystemSettingsResetView
)

router = DefaultRouter()
router.register(r'funds', FundViewSet, basename='fund')
router.register(r'investments', InvestmentViewSet, basename='investment')
router.register(r'sip-schedules', SIPScheduleViewSet, basename='sip-schedule')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'users', SystemUserViewSet, basename='system-user')

urlpatterns = [
    # Authentication endpoints
    path('auth/login', AuthLoginView.as_view(), name='auth-login'),
    path('auth/login/', AuthLoginView.as_view()),
    path('auth/register', AuthRegisterView.as_view(), name='auth-register'),
    path('auth/register/', AuthRegisterView.as_view()),
    path('auth/session', AuthSessionView.as_view(), name='auth-session'),
    path('auth/session/', AuthSessionView.as_view()),
    path('auth/logout', AuthLogoutView.as_view(), name='auth-logout'),
    path('auth/logout/', AuthLogoutView.as_view()),
    path('auth/me', AuthSessionView.as_view()),
    path('auth/me/', AuthSessionView.as_view()),

    # Investors
    path('investors', InvestorListView.as_view(), name='investors-list'),
    path('investors/', InvestorListView.as_view()),

    # Compliance & AML
    path('compliance/alerts', ComplianceAlertListView.as_view(), name='compliance-alerts'),
    path('compliance/alerts/', ComplianceAlertListView.as_view()),
    path('compliance/resolve', ComplianceResolveView.as_view(), name='compliance-resolve'),
    path('compliance/resolve/', ComplianceResolveView.as_view()),

    # AI & ML Analytics
    path('analytics/churn-prediction', ChurnPredictionsView.as_view(), name='churn-prediction-alt'),
    path('analytics/churn-prediction/', ChurnPredictionsView.as_view()),
    path('analytics/churn-predictions', ChurnPredictionsView.as_view(), name='churn-predictions'),
    path('analytics/churn-predictions/', ChurnPredictionsView.as_view()),
    path('analytics/outreach', TriggerOutreachView.as_view(), name='trigger-outreach-alt'),
    path('analytics/outreach/', TriggerOutreachView.as_view()),
    path('analytics/trigger-outreach', TriggerOutreachView.as_view(), name='trigger-outreach'),
    path('analytics/trigger-outreach/', TriggerOutreachView.as_view()),
    path('analytics/aum-growth', AUMGrowthView.as_view(), name='aum-growth'),
    path('analytics/aum-growth/', AUMGrowthView.as_view()),
    path('analytics/heatmap', HeatmapAnalyticsView.as_view(), name='heatmap-analytics'),
    path('analytics/heatmap/', HeatmapAnalyticsView.as_view()),

    # FiNAI AI Advisor & Vector RAG
    path('ai/chat', AIChatView.as_view(), name='ai-chat'),
    path('ai/chat/', AIChatView.as_view()),
    path('ai/stress-test', AIStressTestView.as_view(), name='ai-stress-test'),
    path('ai/stress-test/', AIStressTestView.as_view()),
    path('ai/rag/query', AIRagQueryView.as_view(), name='ai-rag-query'),
    path('ai/rag/query/', AIRagQueryView.as_view()),
    path('ai/rag/documents', AIRagDocumentsView.as_view(), name='ai-rag-documents'),
    path('ai/rag/documents/', AIRagDocumentsView.as_view()),

    # System Settings & Users
    path('settings/ai-threshold', SystemSettingsAiThresholdView.as_view(), name='settings-threshold'),
    path('settings/ai-threshold/', SystemSettingsAiThresholdView.as_view()),
    path('settings/reset', SystemSettingsResetView.as_view(), name='settings-reset'),
    path('settings/reset/', SystemSettingsResetView.as_view()),
    path('users/system', SystemUsersListView.as_view(), name='system-users-list'),
    path('users/system/', SystemUsersListView.as_view()),

    # ViewSet Router URLs
    path('', include(router.urls)),
]
