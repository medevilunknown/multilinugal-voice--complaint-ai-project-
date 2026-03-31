from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from schemas.chat import ChatRequest, ChatResponse
from services.conversation_service import conversation_service
from services.gemini_service import gemini_service
from services.ollama_service import ollama_service
from services.translation_service import translation_service
from utils.constants import REQUIRED_COMPLAINT_FIELDS, SUPPORTED_LANGUAGES, UNKNOWN_INPUT_HINTS

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_with_assistant(request: Request, payload: ChatRequest, db: Session = Depends(get_db)):
    import asyncio

    session = conversation_service.get_or_create(db, payload.session_id)

    if not payload.language and not session.messages:
        supported = ", ".join(SUPPORTED_LANGUAGES)
        return ChatResponse(
            session_id=payload.session_id,
            detected_language="English",
            response=f"Please select your language. Supported languages: {supported}",
            intent="general",
            next_field=None,
            collected_fields={},
            missing_fields=REQUIRED_COMPLAINT_FIELDS,
        )

    language = payload.language or session.selected_language
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Unsupported language")

    conversation_service.add_message(db, session, role="user", content=payload.message)

    # LLM Selection Logic: Prefer Ollama if enabled and available, otherwise Gemini
    llm_payload = None
    use_ollama_requested = getattr(settings, "use_ollama", True)
    
    if use_ollama_requested and ollama_service.is_available():
        print(f"[chat] Routing to local Ollama ({ollama_service.model}) ...")
        try:
            llm_payload = await asyncio.wait_for(
                asyncio.to_thread(
                    ollama_service.generate_complaint_chat_reply,
                    language,
                    payload.message,
                    session.messages,
                    session.collected_fields or {},
                ),
                timeout=120,
            )
        except (asyncio.TimeoutError, Exception) as e:
            print(f"[chat] Ollama failed ({e}) — checking Gemini fallback")
            llm_payload = None

    if llm_payload is None:
        print("[chat] Routing to Google Gemini Cloud API ...")
        try:
            llm_payload = await asyncio.to_thread(
                gemini_service.generate_complaint_chat_reply,
                language,
                payload.message,
                session.messages,
                session.collected_fields or {},
            )
        except Exception as e:
            print(f"[chat] Gemini failed: {e}")
            assistant_text = "The AI service is currently unavailable. Please try again in a moment."
            if language != "English":
                assistant_text = translation_service.translate(assistant_text, language)
            
            return ChatResponse(
                session_id=payload.session_id,
                detected_language=language,
                response=assistant_text,
                intent="general",
                next_field=None,
                collected_fields=session.collected_fields,
                missing_fields=REQUIRED_COMPLAINT_FIELDS,
            )
            
    if llm_payload is None:
        return ChatResponse(
            session_id=payload.session_id,
            detected_language=language,
            response=translation_service.translate("The AI service is temporarily unavailable. Please try again.", language),
            intent="general",
            next_field=None,
            collected_fields=session.collected_fields,
            missing_fields=REQUIRED_COMPLAINT_FIELDS,
        )

    field_updates = llm_payload.get("field_updates", {})
    intent = llm_payload.get("intent")
    
    # Deterministically calculate missing fields in Python to prevent LLM memory amnesia
    merged_fields = {**(session.collected_fields or {}), **field_updates}
    computed_missing = [f for f in REQUIRED_COMPLAINT_FIELDS if not merged_fields.get(f)]
    missing_fields = computed_missing
    
    # Allow the LLM to dynamically pick the next logical question (even optional ones)
    llm_next_field = llm_payload.get("next_required_field")
    if llm_next_field and llm_next_field not in merged_fields:
        next_field = llm_next_field
    else:
        next_field = computed_missing[0] if computed_missing else None
    
    assistant_text = llm_payload.get("assistant_response")
    if not assistant_text:
        # Fallback to a simple localized prompt if the LLM failed to provide a response
        default_msg = "I didn't quite get that. Could you please provide more details?"
        if language == "English":
            assistant_text = default_msg
        else:
            assistant_text = translation_service.translate(default_msg, language)

    user_message_norm = payload.message.strip().lower()
    if user_message_norm in {"i don't know", "i dont know", "dont know", "not sure", "don't know"}:
        hint = UNKNOWN_INPUT_HINTS.get(next_field or "")
        if hint:
            translated_hint = translation_service.translate(hint, language)
            assistant_text = f"{assistant_text}\n\n{translated_hint}"

    conversation_service.add_message(db, session, role="assistant", content=assistant_text)
    conversation_service.update_after_chat(db, session, language, intent, field_updates)

    return ChatResponse(
        session_id=payload.session_id,
        detected_language=language,
        response=assistant_text,
        intent=intent,
        next_field=next_field,
        collected_fields=session.collected_fields,
        missing_fields=missing_fields,
    )

