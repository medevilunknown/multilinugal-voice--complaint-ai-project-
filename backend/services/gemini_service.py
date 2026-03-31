import json
from pathlib import Path

import google.generativeai as genai

from config import settings
from utils.constants import COMPLAINT_TYPES, REQUIRED_COMPLAINT_FIELDS, SUPPORTED_LANGUAGES


class GeminiService:
    def __init__(self, api_key: str = None) -> None:
        self.api_key = api_key or settings.gemini_api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self._pick_model_name())

    @classmethod
    def create_with_key(cls, api_key: str):
        """Create a transient service instance for a specific user's API key."""
        return cls(api_key=api_key)


    def _pick_model_name(self) -> str:
        preferred = [
            "gemini-2.0-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
        ]
        try:
            available = [m.name.split("models/")[-1] for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
            for candidate in preferred:
                if candidate in available:
                    return candidate
            if available:
                return available[0]
        except Exception as e:
            print(f"Error picking model: {e}")
            pass
        return "gemini-1.5-flash-latest"

    def _generate_with_retry(self, prompt: str | list, retries: int = 3) -> str:
        import time
        for i in range(retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text or ""
            except Exception as e:
                err_str = str(e).lower()
                if ("429" in err_str or "rate_limit" in err_str or "quota" in err_str) and i < retries - 1:
                    time.sleep(2 ** i) # Exponential backoff
                    continue
                print(f"Gemini API Error: {e}")
                if "429" in err_str or "quota" in err_str:
                    return "__API_ERROR_429__"
                return "__API_ERROR__"
        return "__API_ERROR__"

    def _safe_json_parse(self, text: str) -> dict:
        import re
        text = text.strip()
        
        # Try to find a JSON object using regex if there's markdown or chatty text
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            text = match.group(0)
            
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}

    def detect_language(self, text: str) -> str:
        prompt = (
            "Detect the language of the user text from this list only: "
            f"{', '.join(SUPPORTED_LANGUAGES)}. "
            "Return only one language name, no extra words.\n\n"
            f"Text: {text}"
        )
        response_text = self._generate_with_retry(prompt)
        guess = (response_text or "English").strip()
        return guess if guess in SUPPORTED_LANGUAGES else "English"

    def translate_text(self, text: str, target_language: str) -> str:
        if not text.strip() or target_language.lower() == "english":
            return text
        prompt = (
            f"Translate the following text strictly to {target_language}. "
            "Return ONLY the translated text. Do not provide explanations, notes, or alternative versions.\n\n"
            f"Text: {text}"
        )
        response_text = self._generate_with_retry(prompt)
        return (response_text or "").strip()

    def to_english(self, text: str) -> str:
        return self.translate_text(text, "English")

    def generate_complaint_chat_reply(
        self,
        user_language: str,
        user_message: str,
        conversation_messages: list[dict],
        collected_fields: dict,
    ) -> dict:
        prompt = f"""You are a helpful cyber crime complaint assistant using voice.

Your job:
1. Extract ALL complaint details from the user's natural speech in one go
2. Do NOT ask about fields the user already mentioned
3. Acknowledge briefly what you understood, then ask for the NEXT missing field only
4. Be conversational and brief (voice-friendly, no long lists)
5. Always respond in: {user_language}
6. IMPORTANT: Do NOT ask the user to upload, share, or submit any documents, screenshots, or evidence. Document uploading is handled separately by the frontend. Focus ONLY on text fields.

Field extraction rules & mappings:
- Name -> `full_name`
- Phone/number -> `phone_number`
- Email -> `email`
- Money lost / amount -> `amount_lost`
- UPI -> `suspect_vpa`
- Suspect's phone -> `suspect_phone`
- When it happened -> `date_time` (If present, format as ISO YYYY-MM-DD'T'HH:MM)
- App/website used -> `platform`
- What happened -> `description` AND `complaint_type`

Required fields: {REQUIRED_COMPLAINT_FIELDS}
Optional: amount_lost, transaction_id, suspect_details, suspect_vpa, suspect_phone, suspect_bank_account, platform
Complaint types: {COMPLAINT_TYPES}

Example Input: "i am rohit my number is 76 and email is 67@gmail and i have issue with payemnt"
Example Output JSON:
{{
  "assistant_response": "Thanks Rohit, I have your email and phone noted. To help with the payment issue, can you tell me which platform or app you used?",
  "intent": "file_complaint",
  "field_updates": {{"full_name": "Rohit", "phone_number": "76", "email": "67@gmail", "description": "issue with payment", "complaint_type": "Financial Fraud"}},
  "next_required_field": "platform",
  "missing_fields": ["platform", "address", "date_time"]
}}

Conversation:
{json.dumps(conversation_messages[-8:], ensure_ascii=False)}

Already collected:
{json.dumps(collected_fields, ensure_ascii=False)}

User said: "{user_message}"

        Return ONLY the JSON payload, no conversational filler or markdown markers:
        """
        response_text = self._generate_with_retry(prompt)
        
        if response_text == "__API_ERROR_429__":
            return {
                "assistant_response": self.translate_text("The Google AI service is at capacity (Rate Limit Exceeded). Please wait a minute and try again.", user_language),
                "intent": "general",
                "field_updates": {},
                "next_required_field": None,
                "missing_fields": [],
            }
        elif response_text == "__API_ERROR__":
            return {
                "assistant_response": self.translate_text("There was an unexpected error connecting to the AI. Please try again.", user_language),
                "intent": "general",
                "field_updates": {},
                "next_required_field": None,
                "missing_fields": [],
            }
            
        payload = self._safe_json_parse(response_text or "")
        
        # If model failed to provide assistant_response in its JSON, ensure we have one
        if payload and "assistant_response" not in payload:
            payload["assistant_response"] = self.translate_text("What can I help you with?", user_language)
            
        if not payload:
            current_missing = [f for f in REQUIRED_COMPLAINT_FIELDS if f not in collected_fields]
            return {
                "assistant_response": self.translate_text("I'm sorry, I didn't quite catch that. Could you please repeat or elaborate?", user_language),
                "intent": "file_complaint" if collected_fields else "general",
                "field_updates": {},
                "next_required_field": current_missing[0] if current_missing else None,
                "missing_fields": current_missing,
            }
        return payload

    def analyze_evidence(self, file_path: str, mime_type: str) -> str:
        prompt = (
            "Extract all meaningful text and cyber-crime-relevant details from this file. "
            "Return plain text summary with names, accounts, UTR, links, timestamps, and suspicious indicators if present."
        )

        path = Path(file_path)
        if not path.exists():
            return ""

        uploaded = genai.upload_file(path=str(path), mime_type=mime_type)
        response = self.model.generate_content([prompt, uploaded])
        return (response.text or "").strip()

    def transcribe_audio(self, file_path: str, mime_type: str, language: str = "English") -> str:
        """Transcribe spoken audio/video to text using Gemini multimodal."""
        prompt = (
            f"Transcribe the spoken content in this audio/video file exactly as spoken in {language}. "
            "Return only the transcription text, nothing else. "
            "If the audio contains code-switching (mixing languages), transcribe both faithfully."
        )

        path = Path(file_path)
        if not path.exists():
            return ""

        uploaded = genai.upload_file(path=str(path), mime_type=mime_type)
        response = self.model.generate_content([prompt, uploaded])
        return (response.text or "").strip()


gemini_service = GeminiService()
