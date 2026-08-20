import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

async def test_fraud_agent():
    await init_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        print("Sending legitimate message...")
        response = await ac.post("/api/fraud/analyze", json={
            "user_id": "test_user",
            "input_type": "text",
            "text": "Your salary of Rs. 50,000 has been credited. Balance is 75,000.",
            "transaction_context": {}
        })
        print("Status:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            print(f"Risk: {data['risk_score']} | Level: {data['risk_level']}")
            print(f"Explanation: {data['explanation']['summary']}")
        else:
            print("Error:", response.text)
            
        print("\nSending scam message...")
        response = await ac.post("/api/fraud/analyze", json={
            "user_id": "test_user",
            "input_type": "text",
            "text": "Dear customer, your bank account will be blocked. Click here http://kyc-update.com to update urgently.",
            "transaction_context": {}
        })
        print("Status:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            print(f"Risk: {data['risk_score']} | Level: {data['risk_level']}")
            print(f"Explanation: {data['explanation']['summary']}")
            print(f"Raw Scores: {data['raw_scores']}")
        else:
            print("Error:", response.text)

if __name__ == "__main__":
    asyncio.run(test_fraud_agent())
