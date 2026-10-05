from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import requests
import os
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(title="SpeechKit Webhook", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscribeRequest(BaseModel):
    audio_url: HttpUrl
    language: str = "ru-RU"

@app.post("/transcribe")
async def transcribe(request: TranscribeRequest):
    """Транскрибировать аудио по URL"""
    try:
        # Скачать аудио
        audio_response = requests.get(str(request.audio_url))
        audio_response.raise_for_status()

        # Отправить в SpeechKit
        headers = {'Authorization': f'Api-Key {os.getenv("YANDEX_API_KEY")}'}
        params = {
            'lang': request.language,
            'folderId': os.getenv('YANDEX_FOLDER_ID'),
            'format': 'oggopus'
        }

        stt_response = requests.post(
            'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize',
            headers=headers,
            params=params,
            data=audio_response.content
        )
        stt_response.raise_for_status()

        result = stt_response.json()

        return {
            "success": True,
            "text": result.get('result', ''),
            "confidence": 0.95,
            "duration": len(audio_response.content) / 16000
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
