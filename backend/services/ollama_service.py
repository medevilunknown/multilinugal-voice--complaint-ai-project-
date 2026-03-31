"""
Ollama-based LLM service for voice-mode AI chat responses.
Uses a local Ollama instance (llama2) as a drop-in alternative to Gemini.
"""

import json
import requests

from config import settings
from utils.constants import COMPLAINT_TYPES, REQUIRED_COMPLAINT_FIELDS, SUPPORTED_LANGUAGES


OLLAMA_BASE_URL = settings.ollama_base_url
# Prefer the user's configured model first
OLLAMA_MODEL_PREFERENCE = [settings.ollama_model, "llama3", "mistral", "llama2", "phi3:mini", "phi3", "phi", "codellama"]



class OllamaService:
    def __init__(self) -> None:
        self.base_url = OLLAMA_BASE_URL
        self.model = self._pick_model()

    def _pick_model(self) -> str:
        """Return the fastest available model from the preference list."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            resp.raise_for_status()
            available = [m["name"] for m in resp.json().get("models", [])]
            print(f"[ollama] Available models: {available}")
            for preferred in OLLAMA_MODEL_PREFERENCE:
                for avail in available:
                    if preferred in avail:
                        print(f"[ollama] Selected model: {avail}")
                        return avail
            return available[0] if available else "llama2"
        except Exception:
            return "llama2"

    def _generate(self, prompt: str, retries: int = 2) -> str:
        import time
        for i in range(retries):
            try:
                resp = requests.post(
                    f"{self.base_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                    timeout=180,  # 3 minutes — CPU inference can be slow
                )
                resp.raise_for_status()
                return resp.json().get("response", "")
            except Exception as e:
                err_str = str(e).lower()
                if i < retries - 1 and "timeout" not in err_str:
                    time.sleep(1)
                    continue
                print(f"Ollama API Error: {e}")
                return ""
        return ""

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
        except json.JSONDecodeError:
            return {}

    def is_available(self) -> bool:
        """Check if Ollama is running and the model is available."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            return any(self.model in m for m in models)
        except Exception:
            return False

    def detect_language(self, text: str) -> str:
        prompt = (
            "Detect the language of the user text from this list only: "
            f"{', '.join(SUPPORTED_LANGUAGES)}. "
            "Return only one language name, no extra words.\n\n"
            f"Text: {text}"
        )
        guess = (self._generate(prompt) or "English").strip()
        return guess if guess in SUPPORTED_LANGUAGES else "English"

    def translate_text(self, text: str, target_language: str) -> str:
        if not text.strip() or target_language.lower() == "english":
            return text
        prompt = (
            f"Translate the following text strictly to {target_language}. "
            "Return ONLY the translated text. Do not provide explanations, notes, or alternative versions.\n\n"
            f"Text: {text}"
        )
        return (self._generate(prompt) or "").strip()

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
6. IMPORTANT: Do NOT ask the user to upload, share, or submit any documents. Focus ONLY on text fields.
7. CRITICAL: If the user provides a very short answer (e.g. just a number, email, or city), it is the answer to the previously asked question. You MUST extract it and return valid JSON. Do NOT output conversational text outside the JSON.
8. DYNAMIC LOGIC: You have access to both Required and Optional fields. Use your intelligence to dynamically choose the most logical NEXT question. For example, if it's financial fraud, aggressively ask for `amount_lost`, `transaction_id`, and `suspect_vpa`. If it's a social media hack, ask for `platform`. Do not just follow a rigid sequence.
9. Output the exact name of the field you are asking for in `next_required_field`.

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

Example Input: "My name is John, phone 9998887777, email john@ex.com. Details: I lost 500 dollars on Facebook yesterday 2026-03-31T15:00. The scammer's UPI was badguy@upi and transaction UTR123."
Example Output JSON:
{{
  "assistant_response": "Thanks John. I have recorded the details of the Facebook fraud and the money lost. Could you provide your physical address?",
  "intent": "file_complaint",
  "field_updates": {{"full_name": "John", "phone_number": "9998887777", "email": "john@ex.com", "amount_lost": "500", "platform": "Facebook", "date_time": "2026-03-31T15:00", "suspect_vpa": "badguy@upi", "transaction_id": "UTR123", "description": "Lost 500 dollars to a scammer", "complaint_type": "Social Media Fraud"}},
  "next_required_field": "address",
  "missing_fields": ["address"]
}}

Conversation:
{json.dumps(conversation_messages[-8:], ensure_ascii=False)}

Already collected:
{json.dumps(collected_fields, ensure_ascii=False)}

User said: "{user_message}"

        Return ONLY the JSON payload, no conversational filler or markdown markers:
        """
        response_text = self._generate(prompt)
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

    def transcribe_audio(self, file_path: str, mime_type: str) -> str:
        """Ollama doesn't support audio natively — return empty."""
        return ""


ollama_service = OllamaService()
