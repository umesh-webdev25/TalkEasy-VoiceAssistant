from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
import os
import uuid
from typing import Dict
from dotenv import load_dotenv
import uvicorn
import assemblyai as aai
import google.generativeai as genai

load_dotenv()

app = FastAPI(title="30 Days of Voice Agents - FastAPI")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class TTSRequest(BaseModel):
    text: str

class LLMQueryRequest(BaseModel):
    text: str
    max_tokens: int = 1000
    temperature: float = 0.7

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
  
@app.get("/api/backend")
async def get_backend_message():
    return {"message": "🚀 This message is coming from FastAPI backend!", "status": "success"}

@app.post("/tts/generate")
async def generate_tts(request: TTSRequest):
    api_key = os.getenv("MURF_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Murf API key not set.")
    url = "https://api.murf.ai/v1/speech/generate"
    payload = {
        "text": request.text,
        "voiceId": "en-US-natalie",  
        "format": "mp3"
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
    return {"audio_url": audio_url}

@app.post("/upload-audio")
async def upload_audio_file(audio: UploadFile = File(...)) -> Dict:
    """
    Upload audio file endpoint for Day 5 task.
    Receives audio file, saves to uploads folder, returns file metadata.
    """
    try:
        # Validate file type
        allowed_types = ['audio/wav', 'audio/mp3', 'audio/webm', 'audio/ogg', 'audio/m4a', 'audio/wave']
        if audio.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Generate unique filename
        file_extension = audio.filename.split('.')[-1] if '.' in audio.filename else 'webm'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        
        return {
            "success": True,
            "filename": unique_filename,
            "original_filename": audio.filename,
            "content_type": audio.content_type,
            "size": file_size,
            "message": "Audio file uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AssemblyAI Configuration
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not ASSEMBLYAI_API_KEY:
    raise RuntimeError("ASSEMBLYAI_API_KEY environment variable is not set")

aai.settings.api_key = ASSEMBLYAI_API_KEY

@app.post("/transcribe/file")
async def transcribe_audio_file(audio: UploadFile = File(...)) -> Dict:
    """
    Transcribe audio file endpoint for Day 6 task.
    Accepts an audio file and returns the transcription using AssemblyAI.
    """
    try:
        # Validate file type
        allowed_types = [
            'audio/wav', 'audio/mp3', 'audio/webm', 'audio/ogg', 
            'audio/m4a', 'audio/wave', 'audio/mp4', 'audio/flac'
        ]
        if audio.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Read audio file content
        audio_content = await audio.read()
        
        # Initialize AssemblyAI transcriber
        transcriber = aai.Transcriber()
        
        # Transcribe the audio
        transcript = transcriber.transcribe(audio_content)
        
        if transcript.status == aai.TranscriptStatus.error:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {transcript.error}"
            )
        
        return {
            "success": True,
            "transcription": transcript.text,
            "confidence": transcript.confidence,
            "audio_duration": transcript.audio_duration,
            "words": [
                {
                    "text": word.text,
                    "start": word.start,
                    "end": word.end,
                    "confidence": word.confidence
                }
                for word in transcript.words
            ] if hasattr(transcript, 'words') else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tts/echo")
async def tts_echo(audio: UploadFile = File(...)) -> Dict:
    """
    Echo bot with Murf voice synthesis.
    Accepts audio file, transcribes it using AssemblyAI, 
    then generates audio using Murf TTS with the same text.
    """
    try:
        # Validate file type
        allowed_types = [
            'audio/wav', 'audio/mp3', 'audio/webm', 'audio/ogg', 
            'audio/m4a', 'audio/wave', 'audio/mp4', 'audio/flac'
        ]
        if audio.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Read audio file content
        audio_content = await audio.read()
        
        # Initialize AssemblyAI transcriber
        transcriber = aai.Transcriber()
        
        # Transcribe the audio
        transcript = transcriber.transcribe(audio_content)
        
        if transcript.status == aai.TranscriptStatus.error:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {transcript.error}"
            )
        
        transcription_text = transcript.text
        
        # Generate audio using Murf TTS
        api_key = os.getenv("MURF_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Murf API key not set")
        
        url = "https://api.murf.ai/v1/speech/generate"
        payload = {
            "text": transcription_text,
            "voiceId": "en-US-natalie",  # You can change this voice
            "format": "mp3",
            "speed": 100,
            "pitch": 0
        }
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Murf TTS failed: {response.text}"
            )
        
        data = response.json()
        audio_url = data.get("audioFile")
        
        if not audio_url:
            raise HTTPException(
                status_code=500,
                detail="No audio URL returned from Murf"
            )
        
        return {
            "success": True,
            "audio_url": audio_url,
            "transcription": transcription_text,
            "confidence": transcript.confidence,
            "audio_duration": transcript.audio_duration
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️  Warning: GEMINI_API_KEY environment variable is not set")
    print("Please add GEMINI_API_KEY=your_api_key to your .env file")
else:
    genai.configure(api_key=GEMINI_API_KEY)

@app.post("/llm/query")
async def llm_query(request: LLMQueryRequest) -> Dict:
    """
    Query Google's Gemini API with text input.
    Accepts text and returns AI-generated response.
    """
    try:
        # Check if Gemini API key is configured
        if not GEMINI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Gemini API key not configured. Please set GEMINI_API_KEY environment variable."
            )
        
        # Validate input
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text input cannot be empty"
            )
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Configure generation parameters
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        # Generate response
        response = model.generate_content(
            request.text,
            generation_config=generation_config
        )
        
        # Extract response text
        if not response.text:
            raise HTTPException(
                status_code=500,
                detail="No response generated from Gemini API"
            )
        
        return {
            "success": True,
            "query": request.text,
            "response": response.text,
            "model": "gemini-1.5-flash",
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else None,
                "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else None,
                "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else None
            }
        }
        
    except Exception as e:
        # Handle specific Gemini API errors
        if "API key" in str(e) or "authentication" in str(e).lower():
            raise HTTPException(
                status_code=401,
                detail="Invalid Gemini API key"
            )
        elif "quota" in str(e).lower() or "limit" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail="Gemini API quota exceeded"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Gemini API error: {str(e)}"
            )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
