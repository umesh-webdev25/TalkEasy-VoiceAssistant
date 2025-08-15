import requests
import os
from fastapi import HTTPException

def generate_tts(text, voice_id="en-US-natalie", format="mp3", speed=100, pitch=0):
    api_key = os.getenv("MURF_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Murf API key not set.")
    url = "https://api.murf.ai/v1/speech/generate"
    payload = {
        "text": text,
        "voiceId": voice_id,
        "format": format,
        "speed": speed,
        "pitch": pitch
    }
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    data = response.json()
    audio_url = data.get("audioFile")
    if not audio_url:
        raise HTTPException(status_code=500, detail="No audio URL returned.")
    return audio_url
