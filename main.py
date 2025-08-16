from fastapi import FastAPI, HTTPException, Request, UploadFile, File, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uuid
from typing import Dict, List
from dotenv import load_dotenv
import uvicorn
import logging
import assemblyai as aai
import google.generativeai as genai
from pydantic import BaseModel
import requests
from chat_history import chat_store
from error_handler import APIErrorHandler, RetryHandler, ErrorSimulator

# Load environment variables
load_dotenv()

app = FastAPI(title="30 Days of Voice Agents - FastAPI")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Request models
class TTSRequest(BaseModel):
    text: str

class LLMQueryRequest(BaseModel):
    text: str
    max_tokens: int = 1000
    temperature: float = 0.7

# Configure AssemblyAI
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
if not ASSEMBLYAI_API_KEY:
    raise RuntimeError("ASSEMBLYAI_API_KEY environment variable is not set")
aai.settings.api_key = ASSEMBLYAI_API_KEY

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("⚠️ Warning: GEMINI_API_KEY environment variable is not set")
    print("Please add GEMINI_API_KEY=your_api_key to your .env file")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
  
@app.get("/api/backend")
async def get_backend_message():
    return {"message": "🚀 This message is coming from FastAPI backend!", "status": "success"}

@app.post("/tts/generate")
async def generate_tts_endpoint(request: TTSRequest):
    try:
        api_key = os.getenv("MURF_API_KEY")
        if not api_key:
            raise Exception("Murf API key not set.")
        
        text_to_speak = request.text[:2800]  # Truncate if too long
        audio_url = generate_tts(text_to_speak)
        
        return {
            "success": True,
            "audio_url": audio_url,
            "message": "TTS generated successfully"
        }
    except Exception as e:
        error_info = APIErrorHandler.handle_api_error(e, "Murf TTS")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": True,
                "message": error_info["message"],
                "fallback_text": "I'm having trouble connecting right now",
                "audio_url": None
            }
        )

@app.post("/upload-audio")
async def upload_audio_file(audio: UploadFile = File(...)) -> Dict:
    """
    Upload audio file endpoint.
    Receives audio file, saves to uploads folder, returns file metadata.
    """
    try:
        allowed_types = ['audio/wav', 'audio/mp3', 'audio/webm', 'audio/ogg', 'audio/m4a', 'audio/wave']
        if audio.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        file_extension = audio.filename.split('.')[-1] if '.' in audio.filename else 'webm'
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
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

@app.post("/transcribe/file")
async def transcribe_audio_file(audio: UploadFile = File(...)) -> Dict:
    """
    Transcribe audio file endpoint.
    Accepts an audio file and returns the transcription using AssemblyAI.
    """
    try:
        allowed_types = [
            'audio/wav', 'audio/mp3', 'audio/webm', 'audio/ogg', 
            'audio/m4a', 'audio/wave', 'audio/mp4', 'audio/flac'
        ]
        if audio.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        audio_content = await audio.read()
        transcript = transcribe_audio(audio_content)

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
    Echo bot with voice synthesis.
    Accepts audio file, transcribes it, then generates audio with the same text.
    """
    try:
        allowed_types = [
            'audio/wav', 'audio/mp3', 'audio/webm', 'audio/ogg', 
            'audio/m4a', 'audio/wave', 'audio/mp4', 'audio/flac'
        ]
        if audio.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        audio_content = await audio.read()
        transcript = transcribe_audio(audio_content)
        transcription_text = transcript.text

        audio_url = generate_tts(transcription_text)

        return {
            "success": True,
            "audio_url": audio_url,
            "transcription": transcription_text,
            "confidence": transcript.confidence,
            "audio_duration": transcript.audio_duration
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/llm/query")
async def llm_query(request: LLMQueryRequest) -> Dict:
    """
    Query Google's Gemini API with text input.
    Accepts text and returns AI-generated response.
    """
    try:
        if not GEMINI_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Gemini API key not configured."
            )
        
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="Text input cannot be empty"
            )
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        response = model.generate_content(
            request.text,
            generation_config=generation_config
        )
        
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
        if "API key" in str(e) or "authentication" in str(e).lower():
            raise HTTPException(status_code=401, detail="Invalid Gemini API key")
        elif "quota" in str(e).lower() or "limit" in str(e).lower():
            raise HTTPException(status_code=429, detail="Gemini API quota exceeded")
        else:
            raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

@app.post("/llm/query-audio")
async def llm_query_audio(audio: UploadFile = File(...)) -> Dict:
    try:
        if not GEMINI_API_KEY:
            raise Exception("Gemini API key not configured.")
        
        allowed_types = [
            'audio/wav', 'audio/mp3', 'audio/webm', 'audio/ogg', 
            'audio/m4a', 'audio/wave', 'audio/mp4', 'audio/flac'
        ]
        if audio.content_type not in allowed_types:
            raise Exception(f"Invalid file type. Allowed types: {', '.join(allowed_types)}")
        
        audio_content = await audio.read()
        transcript = transcribe_audio(audio_content)
        transcription_text = transcript.text
        
        if not transcription_text or not transcription_text.strip():
            raise Exception("No speech detected in audio")
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Please provide a concise response to: {transcription_text}. Keep your response under 2800 characters."
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=1000,
            temperature=0.7
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        if not response.text:
            raise Exception("No response generated from Gemini API")
        
        llm_response = response.text
        text_to_speak = llm_response[:2800]  # Truncate if too long
        audio_url = generate_tts(text_to_speak)
        
        return {
            "success": True,
            "transcription": transcription_text,
            "llm_response": llm_response,
            "audio_url": audio_url,
            "model": "gemini-1.5-flash",
            "tts_voice": "en-US-natalie",
            "response_length": len(llm_response)
        }
    except Exception as e:
        logger.error("LLM query audio error: %s", str(e))
        error_info = APIErrorHandler.handle_api_error(e, "LLM Audio Query")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": True,
                "message": error_info["message"],
                "fallback_text": "I'm having trouble connecting right now",
                "audio_url": None
            }
        )

@app.post("/agent/chat/{session_id}")
async def agent_chat(session_id: str, audio: UploadFile = File(...)) -> Dict:
    """
    Chat endpoint with history.
    Accepts audio file, transcribes it, processes with LLM using chat history,
    and returns audio response. Stores conversation in session history.
    """
    try:
        if not GEMINI_API_KEY:
            raise Exception("Gemini API key not configured.")
        
        allowed_types = [
            'audio/wav', 'audio/mp3', 'audio/webm', 'audio/ogg', 
            'audio/m4a', 'audio/wave', 'audio/mp4', 'audio/flac'
        ]
        if audio.content_type not in allowed_types:
            raise Exception(f"Invalid file type. Allowed types: {', '.join(allowed_types)}")
        
        audio_content = await audio.read()
        transcript = transcribe_audio(audio_content)
        transcription_text = transcript.text
        
        if not transcription_text or not transcription_text.strip():
            raise Exception("No speech detected in audio")
        
        chat_store.add_message(session_id, "user", transcription_text)
        chat_history = chat_store.get_session_messages(session_id)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if chat_history:
            conversation_context = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in chat_history[-10:]
            ])
            prompt = f"""You are a helpful AI assistant. Here's the conversation history:

{conversation_context}

Please provide a natural, conversational response to the user's latest message: {transcription_text}

Keep your response concise and under 2800 characters."""
        else:
            prompt = f"Please provide a concise response to: {transcription_text}. Keep your response under 2800 characters."
        
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=1000,
            temperature=0.7
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        if not response.text:
            raise Exception("No response generated from Gemini API")
        
        llm_response = response.text
        chat_store.add_message(session_id, "assistant", llm_response)
        
        text_to_speak = llm_response[:2800]
        audio_url = generate_tts(text_to_speak)
        conversation_history = chat_store.get_session_history(session_id)
        
        return {
            "success": True,
            "transcription": transcription_text,
            "llm_response": llm_response,
            "audio_url": audio_url,
            "model": "gemini-1.5-flash",
            "tts_voice": "en-US-natalie",
            "response_length": len(llm_response),
            "session_id": session_id,
            "conversation_history": conversation_history,
            "message_count": len(conversation_history)
        }
    except Exception as e:
        error_info = APIErrorHandler.handle_api_error(e, "Agent Chat")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": True,
                "message": error_info["message"],
                "fallback_text": "I'm having trouble connecting right now",
                "audio_url": None
            }
        )

@app.get("/agent/chat/{session_id}/history")
async def get_chat_history(session_id: str) -> Dict:
    """
    Get chat history for a specific session.
    """
    try:
        history = chat_store.get_session_history(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "messages": history,
            "message_count": len(history)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )

@app.delete("/agent/chat/{session_id}")
async def clear_chat_history(session_id: str) -> Dict:
    """
    Clear chat history for a specific session.
    """
    try:
        chat_store.clear_session(session_id)
        return {
            "success": True,
            "session_id": session_id,
            "message": "Chat history cleared successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing chat history: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)