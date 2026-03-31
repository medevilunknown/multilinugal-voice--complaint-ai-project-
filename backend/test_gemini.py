import sys, os
from services.gemini_service import gemini_service

user_message = "i have been scammed of RS 50000 in my UPI as a unknown mandet has been placed in the qr in the shop"
print("Sending to Gemini...")
res = gemini_service.model.generate_content(
    f"Extract fields from: {user_message}. Required: {gemini_service._generate_with_retry.__code__}"
)
print("Parsed Result:", res.text)
