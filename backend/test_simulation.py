import sys
import json
import asyncio

sys.path.insert(0, "/Users/rohitkunjam/Downloads/guardia-lingua-main 2/backend")

from services.ollama_service import ollama_service

user_message = "Hi, my name is Rohit and I need to urgently file a cybercrime report. I live in Bangalore and you can reach me on my phone at 57272727 or email me at rohit@gmail.com. Yesterday evening, around 2026-03-31T18:45, I was trying to buy some electronics from a local vendor who sent me a QR code on WhatsApp. I scanned it using Google Pay to transfer 5000 rupees, but it completely drained my account instead! I ended up losing exactly 45,000 rupees because a hidden mandate was somehow attached to that QR code. The scammer's UPI ID showed up as fakevendor@okicici on my bank statement, and the transaction ID was UTR9876543210. They stopped replying to my calls and blocked my number immediately after the money was deducted. This is a severe UPI fraud and I need help recovering my funds before the mandate triggers again."

print("Simulation Text:")
print(user_message)
print(f"\n--- Sending to Ollama ({ollama_service.model}) ---\n")

def test_ollama():
    try:
        res = ollama_service.generate_complaint_chat_reply(
            user_language="English",
            user_message=user_message,
            conversation_messages=[],
            collected_fields={}
        )
        print("AI Response JSON:\n")
        print(json.dumps(res, indent=2))
    except Exception as e:
        print(f"Error during simulation: {e}")

if __name__ == "__main__":
    if ollama_service.is_available():
        test_ollama()
    else:
        print("Ollama engine is off. Please run `ollama start` on your Mac.")
