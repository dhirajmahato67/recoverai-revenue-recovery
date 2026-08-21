"""Unit tests for Phase 6 AI Provider abstraction and factory."""

import pytest
from app.core.config import Settings
from app.services.ai.providers.base import AIProvider, AIProviderResult
from app.services.ai.providers.factory import get_ai_provider
from app.services.ai.providers.mock_provider import MockProvider
from app.services.ai.providers.openai_provider import OpenAIProvider


@pytest.mark.asyncio
async def test_mock_provider_deterministic_generation():
    """Test that MockProvider generates structured, evidence-grounded text from context."""
    provider = MockProvider(model="test-mock-v1")
    assert provider.provider_name == "mock"

    context = {
        "case": {"investigation_id": "INV-00000000", "case_reference": "RC-001"},
        "metrics": {
            "total_transactions": 1251,
            "overall_success_rate": 81.85,
            "upi_success_rate": 72.09,
            "hdfc_upi_success_rate": 64.77,
            "primary_affected_bank": "HDFC",
            "primary_affected_payment_method": "UPI",
            "dominant_error_code": "GATEWAY_TIMEOUT",
            "dominant_error_count": 74,
        },
        "impact": {
            "revenue_at_risk_inr": "1,219,544.00",
            "recoverable_revenue_inr": "304,886.00",
        },
        "root_cause": {
            "primary_cause": "Upstream HDFC UPI gateway timeout & latency degradation",
            "confidence": 0.83,
        },
        "evidence_ids": ["EVID-TX-001", "EVID-PM-UPI", "EVID-BANK-HDFC", "EVID-ERR-TIMEOUT"],
        "recommendation": {
            "action_type": "PAYMENT_RETRY",
            "eligible_transactions": 438,
            "stopping_condition": "Failure rate exceeds 30%",
        },
    }

    # 1. Query root cause
    res_rc = await provider.generate_response(
        system_prompt="Test system prompt",
        user_prompt="Why did UPI payments fail?",
        context=context,
    )
    assert isinstance(res_rc, AIProviderResult)
    assert "HDFC" in res_rc.text
    assert "64.77%" in res_rc.text
    assert "GATEWAY_TIMEOUT" in res_rc.text
    assert res_rc.provider == "mock"

    # 2. Query revenue at risk
    res_rev = await provider.generate_response(
        system_prompt="Test system prompt",
        user_prompt="How much revenue is at risk?",
        context=context,
    )
    assert "1,219,544.00" in res_rev.text
    assert "304,886.00" in res_rev.text

    # 3. Query recovery execution guardrail
    res_rec = await provider.generate_response(
        system_prompt="Test system prompt",
        user_prompt="How much money did we recover?",
        context=context,
    )
    assert "No recovery has been executed yet" in res_rec.text


def test_ai_provider_factory():
    """Test that factory returns appropriate provider according to settings."""
    cfg_mock = Settings(AI_PROVIDER="mock")
    p1 = get_ai_provider(cfg_mock)
    assert isinstance(p1, MockProvider)

    cfg_openai = Settings(AI_PROVIDER="openai", AI_API_KEY="sk-test-key-12345")
    p2 = get_ai_provider(cfg_openai)
    assert isinstance(p2, OpenAIProvider)
    assert p2.api_key == "sk-test-key-12345"

    # When OpenAI is selected without API key, gracefully fallback to MockProvider
    cfg_openai_nokey = Settings(AI_PROVIDER="openai", AI_API_KEY=None)
    p3 = get_ai_provider(cfg_openai_nokey)
    assert isinstance(p3, MockProvider)
