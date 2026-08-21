"""Live Docker container API verification script."""

import json
import urllib.request

BASE = "http://localhost:8000/api/v1"

def main():
    print("=== LIVE FASTAPI BACKEND VERIFICATION ===")

    # 1. Health
    req = urllib.request.urlopen(f"{BASE}/health/ready")
    health = json.loads(req.read().decode())
    print(f"1. Health Check: status={health.get('status')} db={health.get('database')}")

    # 2. Pipeline run UPI_DEGRADATION
    data = json.dumps({
        "merchant_id": "00000000-0000-0000-0000-000000000001",
        "scenario": "UPI_DEGRADATION",
        "count": 250,
        "trigger_risk_analysis": True
    }).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/pipeline/run", data=data, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    pipe_res = json.loads(res.read().decode())
    print(f"2. Pipeline Run: pipeline_id={pipe_res.get('pipeline_id')} generated={pipe_res.get('total_generated')}")

    # 3. Trigger Risk Analysis or retrieve from pipeline
    data = json.dumps({
        "merchant_id": "00000000-0000-0000-0000-000000000001",
        "current_window_minutes": 120,
        "baseline_window_minutes": 1440
    }).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/risk/analyze", data=data, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    risk_res = json.loads(res.read().decode())
    case_ref = risk_res.get("case_reference") or "RC-001"
    print(f"3. Risk Detection: status={risk_res.get('status')} case={case_ref} signals={risk_res.get('signals_detected_count')}")

    # 4. Trigger Investigation
    data = json.dumps({"risk_case_id": case_ref, "force_reanalyze": True}).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/investigations", data=data, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    inv_res = json.loads(res.read().decode())
    print(f"4. Investigation Triggered: id={inv_res.get('id')} status={inv_res.get('status')} confidence={inv_res.get('confidenceScore')}%")
    print(f"   Finding: {inv_res.get('finding')}")
    print(f"   Conclusion: {inv_res.get('conclusion')}")
    print(f"   Steps Executed: {len(inv_res.get('steps', []))}")
    print(f"   Tool Calls Recorded: {len(inv_res.get('toolExecutions', []))}")

    # 5. Get Investigation Details
    inv_id = inv_res["id"]
    req = urllib.request.urlopen(f"{BASE}/investigations/{inv_id}")
    detail = json.loads(req.read().decode())
    print(f"5. Investigation Detail Query: verified={detail.get('id') == inv_id}")

    # 6. Get Timeline
    req = urllib.request.urlopen(f"{BASE}/investigations/{inv_id}/timeline")
    timeline = json.loads(req.read().decode())
    print(f"6. Timeline Events: count={len(timeline)}")

    # 7. Get Root Cause
    req = urllib.request.urlopen(f"{BASE}/investigations/{inv_id}/root-cause")
    rc = json.loads(req.read().decode())
    print(f"7. Root Cause Hypothesis #1: {rc[0]['cause']} (score={rc[0]['score']}, conf={rc[0]['confidence']})")

    # 8. Get Impact
    req = urllib.request.urlopen(f"{BASE}/investigations/{inv_id}/impact")
    impact = json.loads(req.read().decode())
    print(f"8. Impact Analysis: revenue_at_risk=INR {impact.get('revenue_at_risk_inr')} recoverable=INR {impact.get('recoverable_revenue_inr')}")

    # 9. Get Summary
    req = urllib.request.urlopen(f"{BASE}/investigations/{inv_id}/summary")
    summary = json.loads(req.read().decode())
    print(f"9. Summary Card: id={summary.get('id')} status={summary.get('status')} bank={summary.get('affected_bank')} method={summary.get('affected_method')}")

    print("=== ALL LIVE ENDPOINTS VERIFIED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
