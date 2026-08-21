"""Unit tests for the Scenario Registry and configurations."""

from app.services.simulation.scenarios import (
    ScenarioRegistry,
    SCENARIO_DEFINITIONS,
    SCENARIO_METADATA,
)


def test_scenario_registry_list():
    """Verify all scenarios are listed with valid metadata."""
    scenarios = ScenarioRegistry.list_scenarios()
    assert len(scenarios) >= 5

    scenario_ids = [s.id for s in scenarios]
    assert "NORMAL_BASELINE" in scenario_ids
    assert "UPI_DEGRADATION" in scenario_ids
    assert "RECOVERY_AUTO_STOP" in scenario_ids


def test_scenario_registry_get_baseline():
    """Verify baseline scenario has ~94.2% success rate."""
    baseline = ScenarioRegistry.get_scenario("NORMAL_BASELINE")
    assert baseline.scenario_id == "NORMAL_BASELINE"
    assert baseline.target_success_rate == 0.942
    assert baseline.method_success_rates["UPI"] == 0.942
    assert baseline.method_success_rates["CARD"] >= 0.95


def test_scenario_registry_get_upi_degradation():
    """Verify UPI degradation scenario has elevated HDFC UPI failure configuration."""
    upi_deg = ScenarioRegistry.get_scenario("UPI_DEGRADATION")
    assert upi_deg.scenario_id == "UPI_DEGRADATION"
    assert upi_deg.target_success_rate == 0.817
    assert upi_deg.bank_success_rates["HDFC"] == 0.689
    assert upi_deg.primary_failure_error_code == "GATEWAY_TIMEOUT"


def test_scenario_fallback_unknown():
    """Verify unknown scenario falls back to baseline safely."""
    fallback = ScenarioRegistry.get_scenario("UNKNOWN_SCENARIO_XYZ")  # type: ignore
    assert fallback.scenario_id == "NORMAL_BASELINE"
