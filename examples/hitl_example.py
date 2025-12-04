"""
HITL (Human-in-the-Loop) Example with Amorce SDK

This example shows how an agent can request human approval before
executing a transaction. The approval can happen via ANY channel:
SMS, voice call, chat, email, etc.

The LLM interprets the human's natural language response.
"""

import os
import time
from dotenv import load_dotenv
import google.generativeai as genai

from amorce import AmorceClient, IdentityManager, EnvVarProvider

load_dotenv()

# Setup
identity = IdentityManager(EnvVarProvider("AGENT_PRIVATE_KEY"))
client = AmorceClient(
    identity=identity,
    orchestrator_url=os.getenv("ORCHESTRATOR_URL", "http://localhost:8080"),
    agent_id=identity.agent_id
)

# Setup LLM for response interpretation
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash-exp')


def interpret_human_response(response: str) -> str:
    """Use LLM to interpret natural language response."""
    prompt = f"""
    A human was asked to approve a transaction and responded: "{response}"
    
    Are they approving or rejecting?
    Reply with ONLY: APPROVE or REJECT
    """
    
    result = model.generate_content(prompt).text.strip()
    
    if "APPROVE" in result.upper():
        return "approve"
    else:
        return "reject"


def send_sms(to: str, message: str):
    """Send SMS notification (mock - integrate Twilio in production)."""
    print(f"\n📱 SMS to {to}:")
    print(f"   {message}\n")


def wait_for_sms_reply() -> str:
    """Wait for SMS reply (mock - integrate Twilio in production)."""
    return input("👤 Human responds via SMS: ")


def main():
    print("🤖 Agent: Restaurant Booking Demo with HITL\n")
    
    # Step 1: Agent negotiates with restaurant
    print("1️⃣ Contacting Le Petit Bistro...")
    
    restaurant_response = client.transact(
        service_contract={"service_id": "restaurant_api"},
        payload={"action": "check_availability", "guests": 4, "time": "19:00"}
    )
    
    offer = restaurant_response.get("result", {}).get("content", "Table available at 7pm")
    print(f"   Restaurant: {offer}\n")
    
    # Step 2: Request human approval
    print("2️⃣ Requesting human approval...")
    
    approval_id = client.request_approval(
        transaction_id=restaurant_response.get("transaction_id", "tx_demo"),
        summary="Book table for 4 at Le Petit Bistro, 7pm tomorrow",
        details={
            "restaurant": "Le Petit Bistro",
            "guests": 4,
            "time": "19:00",
            "date": "tomorrow",
            "offer": offer
        },
        timeout_seconds=300  # 5 minutes
    )
    
    print(f"   ✅ Approval request created: {approval_id}\n")
    
    # Step 3: Notify human (via ANY channel)
    print("3️⃣ Sending notification to human...")
    
    send_sms(
        to="+1234567890",
        message=f"Your agent needs approval: {offer}. Reply YES to approve or NO to cancel."
    )
    
    # Step 4: Get human response
    human_response = wait_for_sms_reply()
    
    # Step 5: LLM interprets response
    print("\n4️⃣ Interpreting response...")
    decision = interpret_human_response(human_response)
    print(f"   LLM interpretation: {decision.upper()}\n")
    
    # Step 6: Submit decision to protocol
    print("5️⃣ Submitting decision to Amorce...")
    
    client.submit_approval(
        approval_id=approval_id,
        decision=decision,
        approved_by="user@example.com",
        comments=f"Original response: {human_response}"
    )
    
    # Step 7: Verify approval status
    approval_status = client.check_approval(approval_id)
    print(f"   Approval status: {approval_status['status'].upper()}\n")
    
    # Step 8: Proceed if approved
    if approval_status['status'] == 'approved':
        print("6️⃣ Human approved! Confirming booking...")
        
        confirmation = client.transact(
            service_contract={"service_id": "restaurant_api"},
            payload={"action": "confirm", "booking_id": "demo_123"}
        )
        
        print(f"   ✅ Booking confirmed!\n")
        print(f"📊 Final Status: {confirmation.get('status')}")
    else:
        print("❌ Booking cancelled by human.\n")


if __name__ == "__main__":
    main()
