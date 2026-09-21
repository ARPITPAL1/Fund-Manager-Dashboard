import json
from django.test import TestCase, Client
from django.utils import timezone
from .models import User, Fund, Investment, Transaction, ComplianceAlert, SIPSchedule
from .ml.churn_service import compute_investor_churn, get_all_churn_predictions
from .ml.ai_advisor_service import generate_advisor_response, simulate_portfolio_stress_test


class FinTrendPlatformTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            email='test.investor@example.com',
            phone='+91 9898989898',
            password_hash='hash123',
            full_name='Test Investor',
            date_of_birth='1990-01-01',
            role='INVESTOR',
            status='ACTIVE'
        )

        self.fund = Fund.objects.create(
            fund_code='TEST-EQ-001',
            fund_name='Test Equity Growth Fund',
            fund_house='Test AMC',
            fund_manager_id='FM-01',
            category='EQUITY',
            risk_level='HIGH',
            current_nav=100.0,
            nav_updated_at='2026-06-01',
            min_investment=5000.0,
            min_sip_amount=1000.0,
            expense_ratio=0.75,
            inception_date='2020-01-01',
            aum_crores=500.0
        )

        self.sip = SIPSchedule.objects.create(
            investor_name=self.user.full_name,
            fund_name=self.fund.fund_name,
            amount=10000.0,
            date=5,
            status='CANCELLED',
            next_debit='N/A'
        )

        self.txn = Transaction.objects.create(
            user=self.user,
            fund=self.fund,
            fund_name=self.fund.fund_name,
            transaction_type='REDEMPTION',
            amount=200000.0,
            nav_applied=100.0,
            units=2000.0,
            status='SETTLED',
            created_at=timezone.now()
        )

    def test_fund_catalog_api(self):
        response = self.client.get('/api/funds/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['fund_code'], 'TEST-EQ-001')

    def test_ml_churn_prediction_logic(self):
        pred = compute_investor_churn(self.user, [self.txn], [self.sip])
        self.assertIn('churnRisk', pred)
        self.assertIn('riskCategory', pred)
        self.assertIn('primaryDriver', pred)
        self.assertEqual(pred['riskCategory'], 'HIGH')
        self.assertEqual(pred['primaryDriver'], 'SIP Mandate Cancelled')

    def test_churn_api_endpoint(self):
        response = self.client.get('/api/analytics/churn-predictions/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)

    def test_fi_ai_advisor_and_stress_test(self):
        res = generate_advisor_response('Hello FiNAI, what is our allocation?')
        self.assertIn('answer', res)
        self.assertIn('metrics', res)

        stress_res = simulate_portfolio_stress_test(10.0)
        self.assertIn('proposed_portfolio_drawdown', stress_res)
        self.assertIn('benchmark_drawdown', stress_res)

    def test_ai_chat_api(self):
        response = self.client.post(
            '/api/ai/chat/',
            data=json.dumps({'message': 'Explain allocation'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('answer', data)

    def test_rag_semantic_search(self):
        from .ml.rag_engine import get_rag_engine
        rag = get_rag_engine()
        results = rag.retrieve("What is the lock-in period for ELSS mutual funds?", top_k=2)
        self.assertGreaterEqual(len(results), 1)
        self.assertIn('SEBI-CAT-2026', [r['doc_id'] for r in results])
        self.assertIn('3-year lock-in', results[0]['text'])

    def test_rag_api_endpoints(self):
        # 1. Documents list
        resp = self.client.get('/api/ai/rag/documents/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreaterEqual(data['total_documents'], 4)
        self.assertGreaterEqual(data['total_chunks'], 10)

        # 2. Semantic query
        resp = self.client.post(
            '/api/ai/rag/query/',
            data=json.dumps({'query': 'SEBI categorization large cap rules'}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('retrieved_chunks', data)
        self.assertIn('citations', data)

