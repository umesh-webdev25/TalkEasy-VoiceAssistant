from fastapi import FastAPI, Request, UploadFile, File, Path, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import uuid
import uvicorn
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv

from models.schemas import (
    VoiceChatResponse, 
    ChatHistoryResponse, 
    BackendStatusResponse,
    APIKeyConfig,
    ErrorType
)
from services.stt_service import STTService
from services.llm_service import LLMService
from services.tts_service import TTSService
from services.database_service import DatabaseService
from services.assemblyai_streaming_service import AssemblyAIStreamingService
from services.murf_websocket_service import MurfWebSocketService
from services.web_search_service import web_search_service
from services.skills_manager import skills_manager
from utils.logging_config import setup_logging, get_logger
from utils.constants import get_fallback_message

# Load environment variables
load_dotenv()
setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TalkEasy - AI Voice Assistant",
    version="1.0.0"
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
stt_service: STTService = None
llm_service: LLMService = None
tts_service: TTSService = None
database_service: DatabaseService = None
assemblyai_streaming_service: AssemblyAIStreamingService = None
murf_websocket_service: MurfWebSocketService = None


def initialize_services(config: APIKeyConfig = None) -> APIKeyConfig:
    """Initialize all services with API keys from the provided config or environment variables"""
    if config is None:
        config = APIKeyConfig(
            personas=["default", "pirate", "developer", "cowboy", "robot"],
            selected_persona=os.getenv("AGENT_PERSONA", "default"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            assemblyai_api_key=os.getenv("ASSEMBLYAI_API_KEY"),
            murf_api_key=os.getenv("MURF_API_KEY"),
            murf_voice_id=os.getenv("MURF_VOICE_ID", "en-IN-aarav"),
            mongodb_url=os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        )
    
    global stt_service, llm_service, tts_service, database_service, assemblyai_streaming_service, murf_websocket_service
    if config.are_keys_valid:
        stt_service = STTService(config.assemblyai_api_key)
        llm_service = LLMService(config.gemini_api_key, persona=config.selected_persona)
        tts_service = TTSService(config.murf_api_key, config.murf_voice_id)
        assemblyai_streaming_service = AssemblyAIStreamingService(config.assemblyai_api_key)
        murf_websocket_service = MurfWebSocketService(config.murf_api_key, config.murf_voice_id)
        logger.info(f"✅ All AI services initialized successfully. Persona: {config.selected_persona or 'Default helpful assistant'}")
    else:
        missing_keys = config.validate_keys()
        logger.error(f"❌ Missing API keys: {missing_keys}")
    database_service = DatabaseService(config.mongodb_url)
    
    return config


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting Voice Agent application...")
    
    config = initialize_services()
    if database_service:
        try:
            db_connected = await database_service.connect()
            if db_connected:
                logger.info("✅ Database service connected successfully")
            else:
                logger.warning("⚠️ Database service running in fallback mode")
        except Exception as e:
            logger.error(f"❌ Database service initialization error: {e}")
    else:
        logger.error("❌ Database service not initialized")
    
    logger.info("✅ Application startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("🛑 Shutting down Voice Agent application...")
    
    if database_service:
        await database_service.close()
    
    logger.info("✅ Application shutdown completed")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main application page"""
    session_id = request.query_params.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "session_id": session_id
    })


@app.get("/api/backend", response_model=BackendStatusResponse)
async def get_backend_status():
    """Get backend status"""
    try:
        db_connected = database_service.is_connected() if database_service else False
        db_test_result = await database_service.test_connection() if database_service else False
        
        return BackendStatusResponse(
            status="healthy",
            services={
                "stt": stt_service is not None,
                "llm": llm_service is not None,
                "tts": tts_service is not None,
                "database": database_service is not None,
                "database_connected": db_connected,
                "database_test": db_test_result,
                "assemblyai_streaming": assemblyai_streaming_service is not None,
                "murf_websocket": murf_websocket_service is not None
            },
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error getting backend status: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/agent/chat/all")
async def get_all_chat_histories():
    """Get all chat histories across all sessions"""
    try:
        histories = await database_service.get_all_chat_histories()
        return {
            "success": True,
            "total_sessions": len(histories),
            "chat_histories": histories
        }
    except Exception as e:
        logger.error(f"Error getting all chat histories: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/agent/chat/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history_endpoint(session_id: str = Path(..., description="Session ID")):
    """Get chat history for a session"""
    try:
        chat_history = await database_service.get_chat_history(session_id)
        return ChatHistoryResponse(
            success=True,
            session_id=session_id,
            messages=chat_history,
            message_count=len(chat_history)
        )
    except Exception as e:
        logger.error(f"Error getting chat history for session {session_id}: {str(e)}")
        return ChatHistoryResponse(
            success=False,
            session_id=session_id,
            messages=[],
            message_count=0
        )

@app.delete("/agent/chat/{session_id}/history")
async def clear_session_history(session_id: str = Path(..., description="Session ID")):
    """Clear chat history for a specific session"""
    try:
        success = await database_service.clear_session_history(session_id)
        if success:
            logger.info(f"Chat history cleared for session: {session_id}")
            return {"success": True, "message": f"Chat history cleared for session {session_id}"}
        else:
                return {"success": False, "message": f"Failed to clear chat history for session {session_id}"}
    except Exception as e:
        logger.error(f"Error clearing session history for {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/config")
async def update_configuration(config: APIKeyConfig):
    """Update API key configuration"""
    try:
        # Reinitialize services with the new configuration
        initialize_services(config)
        
        return {
            "success": True,
            "message": "Configuration updated successfully",
            "services_initialized": {
                "stt": stt_service is not None,
                "llm": llm_service is not None,
                "tts": tts_service is not None,
                "database": database_service is not None,
                "assemblyai_streaming": assemblyai_streaming_service is not None,
                "murf_websocket": murf_websocket_service is not None
            }
        }
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")


@app.post("/api/persona/switch")
async def switch_persona(request: Request):
    """Switch the AI persona"""
    try:
        # Parse the JSON body
        body = await request.json()
        persona = body.get("persona")
        
        if not persona:
            raise HTTPException(status_code=400, detail="Persona not provided")
        
        if llm_service:
            llm_service.set_persona(persona)
            return {
                "success": True,
                "message": f"Persona switched to {persona}",
                "persona": persona
            }
        else:
            raise HTTPException(status_code=500, detail="LLM service not initialized")
    except Exception as e:
        logger.error(f"Error switching persona: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to switch persona: {str(e)}")


@app.post("/agent/chat/{session_id}", response_model=VoiceChatResponse)
async def chat_with_agent(
    session_id: str = Path(..., description="Session ID"),
    audio: UploadFile = File(..., description="Audio file for voice input")
):
    """Chat with the voice agent using audio input"""
    transcribed_text = ""
    response_text = ""
    audio_url = None
    temp_audio_path = None
    
    try:
        # Validate services availability
        config = initialize_services()
        if not config.are_keys_valid:
            missing_keys = config.validate_keys()
            error_message = get_fallback_message(ErrorType.API_KEYS_MISSING)
            fallback_audio = await tts_service.generate_fallback_audio(error_message) if tts_service else None
            return VoiceChatResponse(
                success=False,
                message=error_message,
                transcription="",
                llm_response=error_message,
                audio_url=fallback_audio,
                session_id=session_id,
                error_type=ErrorType.API_KEYS_MISSING
            )
        
        # Process audio file
        audio_content = await audio.read()
        temp_audio_path = f"temp_audio_{session_id}_{uuid.uuid4().hex}.wav"
        
        with open(temp_audio_path, "wb") as temp_file:
            temp_file.write(audio_content)
        
        # Transcribe audio
        transcribed_text = await stt_service.transcribe_audio(temp_audio_path)
        
        # Generate LLM response with chat history
        if not database_service:
            chat_history = []
            user_save_success = False
            assistant_save_success = False
        else:
            chat_history = await database_service.get_chat_history(session_id)
            
            # Save user message to chat history
            user_save_success = await database_service.add_message_to_history(session_id, "user", transcribed_text)
        
        response_text = await llm_service.generate_response(transcribed_text, chat_history)
        
        if database_service:
            # Save assistant response to chat history
            assistant_save_success = await database_service.add_message_to_history(session_id, "assistant", response_text)
        
        # Generate TTS audio
        audio_url = await tts_service.generate_audio(response_text, session_id)
        
        return VoiceChatResponse(
            success=True,
            message="Voice chat processed successfully",
            transcription=transcribed_text,
            llm_response=response_text,
            audio_url=audio_url,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"Error in chat_with_agent for session {session_id}: {str(e)}")
        
        # Generate appropriate error response based on the stage where error occurred
        if not transcribed_text:
            error_type = ErrorType.STT_ERROR
            error_message = get_fallback_message(ErrorType.STT_ERROR)
        elif not response_text:
            error_type = ErrorType.LLM_ERROR
            error_message = get_fallback_message(ErrorType.LLM_ERROR)
        elif not audio_url:
            error_type = ErrorType.TTS_ERROR
            error_message = get_fallback_message(ErrorType.TTS_ERROR)
        else:
            error_type = ErrorType.GENERAL_ERROR
            error_message = get_fallback_message(ErrorType.GENERAL_ERROR)
        
        fallback_audio = await tts_service.generate_fallback_audio(error_message) if tts_service else None
        
        return VoiceChatResponse(
            success=False,
            message=error_message,
            transcription=transcribed_text,
            llm_response=response_text or error_message,
            audio_url=fallback_audio,
            session_id=session_id,
            error_type=error_type
        )
    
    finally:
        # Clean up temporary file
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_audio_path}: {str(e)}")
        

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    def is_connected(self, websocket: WebSocket) -> bool:
        """Check if a WebSocket is still in active connections"""
        return websocket in self.active_connections

    async def send_personal_message(self, message: str, websocket: WebSocket):
        if self.is_connected(websocket):
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error sending personal message: {e}")
                self.disconnect(websocket)
        else:
            logger.debug("Attempted to send message to disconnected WebSocket")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                self.disconnect(connection)


manager = ConnectionManager()

# Global locks to prevent concurrent LLM streaming for the same session
session_locks = {}

# Global function to handle LLM streaming (moved outside WebSocket handler to prevent duplicates)
async def handle_llm_streaming(user_message: str, session_id: str, websocket: WebSocket):
    """Handle LLM streaming response and send to Murf WebSocket for TTS"""
    
    # Prevent concurrent streaming for the same session
    if session_id not in session_locks:
        session_locks[session_id] = asyncio.Lock()
    
    async with session_locks[session_id]:
        # Initialize variables at function scope
        accumulated_response = ""
        audio_chunk_count = 0
        total_audio_size = 0
        
        try:
            # Get chat history
            try:
                if not database_service:
                    chat_history = []
                else:
                    chat_history = await database_service.get_chat_history(session_id)
                    # Save user message to chat history
                    save_success = await database_service.add_message_to_history(session_id, "user", user_message)
            except Exception as e:
                logger.error(f"Chat history error: {str(e)}")
                chat_history = []
            
            # Send LLM streaming start notification
            start_message = {
                "type": "llm_streaming_start",
                "message": "LLM is generating response...",
                "user_message": user_message,
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(json.dumps(start_message), websocket)
            
            # Connect to Murf WebSocket
            try:
                await murf_websocket_service.connect()
                
                # Create async generator for LLM streaming
                async def llm_text_stream():
                    nonlocal accumulated_response
                    chunk_count = 0
                    async for chunk in llm_service.generate_streaming_response(user_message, chat_history):
                        if chunk:
                            chunk_count += 1
                            accumulated_response += chunk
                            
                            # Send chunk to client
                            chunk_message = {
                                "type": "llm_streaming_chunk",
                                "chunk": chunk,
                                "accumulated_length": len(accumulated_response),
                                "timestamp": datetime.now().isoformat()
                            }
                            await manager.send_personal_message(json.dumps(chunk_message), websocket)
                            
                            yield chunk
                    
                    if not accumulated_response.strip():
                        logger.error(f"❌ Empty accumulated response for: '{user_message}'")
                        raise Exception("Empty response from LLM stream")
                
                # Send LLM stream to Murf and receive base64 audio
                tts_start_message = {
                    "type": "tts_streaming_start", 
                    "message": "Starting TTS streaming with Murf WebSocket...",
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(json.dumps(tts_start_message), websocket)
                
                # Stream LLM text to Murf and get base64 audio back
                async for audio_response in murf_websocket_service.stream_text_to_audio(llm_text_stream()):
                    if audio_response["type"] == "audio_chunk":
                        audio_chunk_count += 1
                        total_audio_size += audio_response["chunk_size"]
                        
                        # Send audio data to client
                        audio_message = {
                            "type": "tts_audio_chunk",
                            "audio_base64": audio_response["audio_base64"],
                            "chunk_number": audio_response["chunk_number"],
                            "chunk_size": audio_response["chunk_size"],
                            "total_size": audio_response["total_size"],
                            "is_final": audio_response["is_final"],
                            "timestamp": audio_response["timestamp"]
                        }
                        await manager.send_personal_message(json.dumps(audio_message), websocket)
                        
                        # Check if this is the final chunk
                        if audio_response["is_final"]:
                            break
                    
                    elif audio_response["type"] == "status":
                        # Send status updates to client
                        status_message = {
                            "type": "tts_status",
                            "data": audio_response["data"],
                            "timestamp": audio_response["timestamp"]
                        }
                        await manager.send_personal_message(json.dumps(status_message), websocket)
                
            except Exception as e:
                logger.error(f"Error with Murf WebSocket streaming: {str(e)}")
                error_message = {
                    "type": "tts_streaming_error",
                    "message": f"Error with Murf WebSocket: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                await manager.send_personal_message(json.dumps(error_message), websocket)
            
            finally:
                # Disconnect from Murf WebSocket
                try:
                    await murf_websocket_service.disconnect()
                except Exception as e:
                    logger.error(f"Error disconnecting from Murf WebSocket: {str(e)}")
            
            # Save to chat history
            try:
                if database_service:
                    save_success = await database_service.add_message_to_history(session_id, "assistant", accumulated_response)
            except Exception as e:
                logger.error(f"Failed to save assistant response to history: {str(e)}")
            
            # Send completion notification
            complete_message = {
                "type": "llm_streaming_complete",
                "message": "LLM response and TTS streaming completed",
                "complete_response": accumulated_response,
                "total_length": len(accumulated_response),
                "audio_chunks_received": audio_chunk_count,
                "total_audio_size": total_audio_size,
                "session_id": session_id,  # Include session_id in response
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(json.dumps(complete_message), websocket)
            
        except Exception as e:
            logger.error(f"Error in LLM streaming: {str(e)}")
            error_message = {
                "type": "llm_streaming_error",
                "message": f"Error generating LLM response: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            await manager.send_personal_message(json.dumps(error_message), websocket)
        
        finally:
            pass  # Session lock is automatically released


@app.websocket("/ws/audio-stream")
async def audio_stream_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Try to get session_id from query parameters first
    query_params = dict(websocket.query_params)
    session_id = query_params.get('session_id')
    
    if not session_id:
        session_id = str(uuid.uuid4())
    
    audio_filename = f"streamed_audio_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    audio_filepath = os.path.join("streamed_audio", audio_filename)
    os.makedirs("streamed_audio", exist_ok=True)
    is_websocket_active = True
    last_processed_transcript = ""  # Track last processed transcript to prevent duplicates
    last_processing_time = 0  # Track when we last processed a transcript
    
    async def transcription_callback(transcript_data):
        nonlocal last_processed_transcript, last_processing_time
        try:
            if is_websocket_active and manager.is_connected(websocket):
                await manager.send_personal_message(json.dumps(transcript_data), websocket)
                # Only show final transcriptions and trigger LLM streaming
                if transcript_data.get("type") == "final_transcript":
                    await manager.send_personal_message(json.dumps(transcript_data), websocket)
                    final_text = transcript_data.get('text', '').strip()
                    
                    # Normalize text for comparison
                    normalized_current = final_text.lower().strip('.,!?;: ')
                    normalized_last = last_processed_transcript.lower().strip('.,!?;: ')
                    
                    # Add cooldown period (minimum 2 seconds between processing)
                    current_time = datetime.now().timestamp()
                    time_since_last = current_time - last_processing_time
                    
                    # Prevent duplicate processing
                    if (final_text and 
                        normalized_current != normalized_last and 
                        len(normalized_current) > 0 and 
                        time_since_last >= 2.0 and
                        llm_service):
                        
                        last_processed_transcript = final_text
                        last_processing_time = current_time
                        await handle_llm_streaming(final_text, session_id, websocket)
                        
        except Exception as e:
            logger.error(f"Error sending transcription: {e}")

    try:
        if assemblyai_streaming_service:
            assemblyai_streaming_service.set_transcription_callback(transcription_callback)
            async def safe_websocket_callback(msg):
                if is_websocket_active and manager.is_connected(websocket):
                    return await manager.send_personal_message(json.dumps(msg), websocket)
                return None
            
            await assemblyai_streaming_service.start_streaming_transcription(
                websocket_callback=safe_websocket_callback
            )
        
        welcome_message = {
            "type": "audio_stream_ready",
            "message": "Audio streaming endpoint ready with AssemblyAI transcription. Send binary audio data.",
            "session_id": session_id,
            "audio_filename": audio_filename,
            "transcription_enabled": assemblyai_streaming_service is not None,
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_personal_message(json.dumps(welcome_message), websocket)
        
        chunk_count = 0
        total_bytes = 0
        
        while True:
            try:
                message = await websocket.receive()
                
                if "text" in message:
                    text_data = message["text"]
                    
                    # Try to parse as JSON first (for session_id message)
                    try:
                        command_data = json.loads(text_data)
                        if isinstance(command_data, dict) and command_data.get("type") == "session_id":
                            # Update session_id if provided from frontend
                            new_session_id = command_data.get("session_id")
                            if new_session_id and new_session_id != session_id:
                                logger.info(f"Updating session_id from {session_id} to {new_session_id}")
                                session_id = new_session_id
                                # Update audio filename with new session ID
                                audio_filename = f"streamed_audio_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
                                audio_filepath = os.path.join("streamed_audio", audio_filename)
                            continue
                    except json.JSONDecodeError:
                        # Not JSON, treat as regular command
                        pass
                    
                    command = text_data
                    
                    if command == "start_streaming":
                        response = {
                            "type": "command_response",
                            "message": "Ready to receive audio chunks with real-time transcription",
                            "status": "streaming_ready"
                        }
                        await manager.send_personal_message(json.dumps(response), websocket)
                        
                    elif command == "stop_streaming":
                        response = {
                            "type": "command_response",
                            "message": "Stopping audio stream",
                            "status": "streaming_stopped"
                        }
                        await manager.send_personal_message(json.dumps(response), websocket)
                        
                        if assemblyai_streaming_service:
                            async def safe_stop_callback(msg):
                                if manager.is_connected(websocket):
                                    return await manager.send_personal_message(json.dumps(msg), websocket)
                                return None
                        break
                
                elif "bytes" in message:
                    audio_chunk = message["bytes"]
                    chunk_count += 1
                    total_bytes += len(audio_chunk)
                    
                    # Send to AssemblyAI for transcription if available
                    if assemblyai_streaming_service and is_websocket_active:
                        await assemblyai_streaming_service.send_audio_chunk(audio_chunk)
                    
                    # Send chunk confirmation to client
                    if chunk_count % 10 == 0:  # Send every 10th chunk to avoid spam
                        chunk_response = {
                            "type": "audio_chunk_received",
                            "chunk_number": chunk_count,
                            "total_bytes": total_bytes,
                            "timestamp": datetime.now().isoformat()
                        }
                        await manager.send_personal_message(json.dumps(chunk_response), websocket)

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error processing audio chunk: {e}")
                break

        # Send final response before closing
        final_response = {
            "type": "audio_stream_complete",
            "message": f"Audio stream completed. Total chunks: {chunk_count}, Total bytes: {total_bytes}",
            "session_id": session_id,
            "audio_filename": audio_filename,
            "total_chunks": chunk_count,
            "total_bytes": total_bytes,
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_personal_message(json.dumps(final_response), websocket)

    except WebSocketDisconnect:
        is_websocket_active = False
        manager.disconnect(websocket)
    except Exception as e:
        is_websocket_active = False
        logger.error(f"Audio streaming WebSocket error: {e}")
        manager.disconnect(websocket)
    finally:
        is_websocket_active = False
        if assemblyai_streaming_service:
            await assemblyai_streaming_service.stop_streaming_transcription()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)