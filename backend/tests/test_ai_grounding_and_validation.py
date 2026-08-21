"""Unit tests for AI intent classification, evidence grounding, and response validation."""

import pytest
from app.services.ai.prompt_engine import PromptEngine
from app.services.ai.validator import ResponseValidator


def test_intent_classification():
    """Verify prompt classifier maps operator questions to correct semantic intents."""
    assert PromptEngine.classify_intent("Why did UPI fail?") == "ROOT_CAUSE"
    assert PromptEngine.classify_intent("What caused the incident?") == "ROOT_CAUSE"
    assert PromptEngine.classify_intent("How much revenue is at risk?") == "IMPACT"
    assert PromptEngine.classify_intent("What is the recoverable amount?") == "IMPACT"
    assert PromptEngine.classify_intent("Show me the evidence supporting this") == "EVIDENCE"
    assert PromptEngine.classify_intent("Compare UPI vs Card performance") == "COMPARISON"
    assert PromptEngine.classify_intent("What is the chronological timeline?") == "TIMELINE"
    assert PromptEngine.classify_intent("Give me an executive summary") == "SUMMARY"
    assert PromptEngine.classify_intent("What should we do next?") == "RECOMMENDATION"
    assert PromptEngine.classify_intent("How confident are you about HDFC?") == "UNCERTAINTY"


def test_evidence_reference_extraction():
    """Verify appropriate evidence IDs are selected according to intent."""
    context = {
        "evidence": [
            {"evidence_id": "EVID-TX-001"},
            {"evidence_id": "EVID-PM-UPI"},
            {"evidence_id": "EVID-BANK-HDFC"},
            {"evidence_id": "EVID-ERR-TIMEOUT"},
        ]
    }

    refs_rc = PromptEngine.extract_evidence_references("ROOT_CAUSE", context)
    assert len(refs_rc) == 4
    assert "EVID-BANK-HDFC" in refs_rc

    refs_pm = PromptEngine.extract_evidence_references("COMPARISON", context)
    assert "EVID-PM-UPI" in refs_pm or "EVID-BANK-HDFC" in refs_pm


def test_response_validator_validates_evidence_and_action_safety():
    """Test that validator filters non-existent evidence IDs and enforces action safety."""
    context = {
        "evidence_ids": ["EVID-TX-001", "EVID-PM-UPI", "EVID-BANK-HDFC"],
        "recommendation": {
            "action_type": "PAYMENT_RETRY",
            "eligible_transactions": 438,
            "stopping_condition": "Failure rate exceeds 30%",
        },
        "impact": {"recoverable_revenue_inr": "304,886.00"},
        "root_cause": {"confidence": 0.83},
    }

    # Pass a valid ID and a fake fabricated ID
    candidate_refs = ["EVID-BANK-HDFC", "EVID-FABRICATED-FAKE-999"]
    raw_text = "HDFC UPI experienced gateway timeouts."

    text, status, verified_refs, actions, warnings = ResponseValidator.validate_and_enrich(
        raw_text=raw_text,
        intent="RECOMMENDATION",
        context=context,
        candidate_evidence_refs=candidate_refs,
    )

    # Fabricated ID must be filtered out
    assert "EVID-BANK-HDFC" in verified_refs
    assert "EVID-FABRICATED-FAKE-999" not in verified_refs
    assert status == "VERIFIED"

    # Action safety check
    assert len(actions) == 1
    action = actions[0]
    assert action.action == "PAYMENT_RETRY"
    assert action.requires_approval is True
    assert action.can_execute is False
    assert "INR 304,886.00" in action.expected_impact


def test_response_validator_detects_unexecuted_recovery_hallucination():
    """Test that claims of past recovery executions trigger a warning and status change."""
    context = {
        "evidence_ids": ["EVID-TX-001"],
        "recommendation": {},
        "impact": {},
        "root_cause": {},
    }

    hallucinated_text = "We have already recovered INR 50,000 across 25 retried transactions."

    text, status, verified_refs, actions, warnings = ResponseValidator.validate_and_enrich(
        raw_text=hallucinated_text,
        intent="IMPACT",
        context=context,
        candidate_evidence_refs=["EVID-TX-001"],
    )

    assert status == "PARTIAL"
    assert len(warnings) > 0
    assert any("diagnostic only" in w for w in warnings)
