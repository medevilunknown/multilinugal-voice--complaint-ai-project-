import mimetypes

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from schemas.ai import (
    DetectLanguageRequest,
    DetectLanguageResponse,
    TextToSpeechRequest,
    TextToSpeechResponse,
    TranslateRequest,
    TranslateResponse,
)
from services.gemini_service import gemini_service
from services.translation_service import translation_service


router = APIRouter(prefix="/ai", tags=["AI Utilities"])


@router.post("/detect-language", response_model=DetectLanguageResponse)
def detect_language(payload: DetectLanguageRequest):
    language = translation_service.detect_language(payload.text)
    return DetectLanguageResponse(language=language)


@router.post("/translate", response_model=TranslateResponse)
def translate(payload: TranslateRequest):
    translated = translation_service.translate(payload.text, payload.target_language)
    return TranslateResponse(translated_text=translated)


@router.post("/speech-to-text")
def speech_to_text(file: UploadFile = File(...), language: str = Form("English")):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid audio/video file")

    temp_bytes = file.file.read()
    if not temp_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    # Gemini accepts multimodal file parts. Save temp and analyze.
    suffix = file.filename.split(".")[-1].lower()
    temp_path = f"/tmp/cyberguard_stt.{suffix}"
    with open(temp_path, "wb") as out:
        out.write(temp_bytes)

    # Convert video to audio before sending to Gemini to avoid size limits
    if suffix in ["mp4", "mov", "avi", "mkv"]:
        from moviepy.editor import VideoFileClip
        import logging
        try:
            audio_path = "/tmp/cyberguard_stt.mp3"
            clip = VideoFileClip(temp_path)
            clip.audio.write_audiofile(audio_path, logger=None)
            temp_path = audio_path
            mime_type = "audio/mpeg"
        except Exception as e:
            logging.error(f"Failed to extract audio using moviepy: {e}")
            mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
    else:
        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

    text = gemini_service.transcribe_audio(temp_path, mime_type, language)

    return {"transcript": text}


@router.post("/text-to-speech", response_model=TextToSpeechResponse)
def text_to_speech(payload: TextToSpeechRequest):
    localized = translation_service.translate(payload.text, payload.language)
    return TextToSpeechResponse(text_for_speech=localized, language=payload.language)
