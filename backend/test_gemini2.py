import os
os.environ["GEMINI_API_KEY"] = "fake" # it will use the real one from config.py because config.py uses pydantic settings from .env!
import sys
sys.path.insert(0, "/Users/rohitkunjam/Downloads/guardia-lingua-main 2/backend")

from services.gemini_service import gemini_service

user_message = "i have been scammed of RS 50000 in my UPI as a unknown mandet has been placed in the qr in the shop"

print(f"Testing message: {user_message}")

prompt = f"""You are a helpful cyber crime complaint assistant using voice.

Your job:
1. Extract ALL complaint details from the user's natural speech in one go
2. Do NOT ask about fields the user already mentioned
3. Acknowledge briefly what you understood, then ask for the NEXT missing field only
4. Be conversational and brief (voice-friendly, no long lists)
5. Always respond in: English
6. IMPORTANT: Do NOT ask the user to upload, share, or submit any documents, screenshots, or evidence. Document uploading is handled separately by the frontend. Focus ONLY on text fields.

Field extraction rules & mappings:
- Name -> `full_name`
- Phone/number -> `phone_number`
- Email -> `email`
- Money lost / amount -> `amount_lost`
- UPI -> `suspect_vpa`
- Suspect's phone -> `suspect_phone`
- When it happened -> `date_time` (MUST be in strict ISO format YYYY-MM-DDTHH:MM)
- App/website used -> `platform`
- What happened -> `description` AND `complaint_type`

Example Output JSON:
{{
  "assistant_response": "Thanks Rohit, I have your email and phone noted. To help with the payment issue, can you tell me which platform or app you used?",
  "intent": "file_complaint",
  "field_updates": {{"full_name": "Rohit", "phone_number": "76", "email": "67@gmail", "description": "issue with payment", "complaint_type": "Financial Fraud"}},
  "next_required_field": "platform",
  "missing_fields": ["platform", "address", "date_time"]
}}

User said: "{user_message}"

        Return ONLY the JSON payload, no conversational filler or markdown markers:
"""

print("Sending to Gemini...")
resp = gemini_service._generate_with_retry(prompt)
print("RAW RESPONSE:")
print("---")
print(resp)
print("---")

print("\nPARSED:")
print(gemini_service._safe_json_parse(resp))
