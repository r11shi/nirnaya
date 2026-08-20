"""Quick API smoke test."""
import httpx
import json
import sys

BASE = "http://localhost:8000"

def test_health():
    r = httpx.get(f"{BASE}/api/health")
    print(f"Health: {r.status_code}")
    print(json.dumps(r.json(), indent=2))
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    print("✓ Health passed\n")

def test_fraud_scam():
    r = httpx.post(f"{BASE}/api/fraud/analyze", json={
        "input_type": "text",
        "text": "URGENT: Dear SBI customer, your account will be blocked within 24 hours. Update KYC immediately at http://sbi-kyc-update.tk. Share OTP sent to your number. Call 9876543210.",
        "transaction_context": {
            "amount": 48000,
            "payee": "Unknown Merchant",
            "is_new_payee": True,
        }
    })
    print(f"Fraud (scam): {r.status_code}")
    data = r.json()
    print(json.dumps(data, indent=2, default=str))
    assert r.status_code == 200
    assert data["risk_level"] in ["HIGH", "SUSPICIOUS"]
    assert data["policy_action"] in ["PAUSE", "WARN"]
    assert len(data["explanation"]["evidence"]) > 0
    print(f"✓ Risk: {data['risk_score']}, Level: {data['risk_level']}, Action: {data['policy_action']}")
    print(f"  Signals active: {data['fraud_signals']}")
    print()
    return data["analysis_id"]

def test_fraud_legit():
    r = httpx.post(f"{BASE}/api/fraud/analyze", json={
        "input_type": "text",
        "text": "Your SBI account XX1234 has been credited with Rs.5000. Available balance: Rs.25000. If not done by you, call 1800XXXXX.",
    })
    print(f"Fraud (legit): {r.status_code}")
    data = r.json()
    assert r.status_code == 200
    print(f"✓ Risk: {data['risk_score']}, Level: {data['risk_level']}, Action: {data['policy_action']}")
    # Legitimate message should have LOW or UNCERTAIN risk
    print()

def test_feedback(analysis_id):
    r = httpx.post(f"{BASE}/api/fraud/feedback", json={
        "analysis_id": analysis_id,
        "action": "cancelled",
        "is_correct": True,
        "notes": "This was definitely a scam",
    })
    print(f"Feedback: {r.status_code}")
    print(json.dumps(r.json(), indent=2, default=str))
    assert r.status_code == 200
    print("✓ Feedback recorded\n")

def test_finance_upload():
    import os
    csv_path = os.path.join(os.path.dirname(__file__), "data", "sample_transactions.csv")
    with open(csv_path, "r") as f:
        csv_content = f.read()
    
    r = httpx.post(
        f"{BASE}/api/finance/transactions/upload",
        files={"file": ("transactions.csv", csv_content, "text/csv")},
        data={"user_id": "test-user-1"},
    )
    print(f"Upload: {r.status_code}")
    data = r.json()
    print(json.dumps(data, indent=2, default=str))
    assert r.status_code == 200
    assert data["imported"] > 0
    print(f"✓ Imported {data['imported']} transactions\n")

def test_spending():
    r = httpx.get(f"{BASE}/api/finance/spending/test-user-1")
    print(f"Spending: {r.status_code}")
    data = r.json()
    print(json.dumps(data, indent=2, default=str))
    assert r.status_code == 200
    assert data["total_expenses"] > 0
    print(f"✓ Income: ₹{data['total_income']:,.0f}, Expenses: ₹{data['total_expenses']:,.0f}, Surplus: ₹{data['monthly_surplus']:,.0f}/mo\n")

def test_goals():
    # Create goal
    r = httpx.post(f"{BASE}/api/finance/goals", json={
        "user_id": "test-user-1",
        "name": "Emergency Fund",
        "target_amount": 100000,
        "current_amount": 25000,
        "deadline": "2027-06-01T00:00:00Z",
    })
    print(f"Create goal: {r.status_code}")
    data = r.json()
    print(json.dumps(data, indent=2, default=str))
    assert r.status_code == 200
    goal_id = data["id"]
    print(f"✓ Goal created: {goal_id}\n")

    # Get goals
    r = httpx.get(f"{BASE}/api/finance/goals/test-user-1")
    assert r.status_code == 200
    print(f"✓ Goals listed: {len(r.json()['goals'])} goals\n")

    # Simulate
    r = httpx.post(f"{BASE}/api/finance/goals/{goal_id}/simulate", json={
        "user_id": "test-user-1",
        "scenario": {
            "reduce_category": "food",
            "reduce_by": 1000,
        }
    })
    print(f"Simulate: {r.status_code}")
    data = r.json()
    print(json.dumps(data, indent=2, default=str))
    assert r.status_code == 200
    print(f"✓ Simulation: Current months={data['current_months_to_goal']}, New months={data['new_months_to_goal']}")
    print(f"  Savings diff: ₹{data['savings_difference']:,.0f}/mo\n")


if __name__ == "__main__":
    print("=" * 60)
    print("NIRNAYA API SMOKE TEST")
    print("=" * 60)
    print()
    
    try:
        test_health()
        analysis_id = test_fraud_scam()
        test_fraud_legit()
        test_feedback(analysis_id)
        test_finance_upload()
        test_spending()
        test_goals()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
