import assemblyai as aai
from fastapi import HTTPException

aai.settings.api_key = None  # Set this in main.py or via env

def transcribe_audio(audio_content):
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_content)
    if transcript.status == aai.TranscriptStatus.error:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {transcript.error}")
    return transcript
