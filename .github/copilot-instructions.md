# TalkEasy Voice Assistant - AI Agent Guide

## Architecture Overview
This is a real-time voice assistant with streaming capabilities, built on FastAPI + modern web frontend. The core flow: **WebSocket audio streaming → AssemblyAI transcription → Google Gemini LLM → Murf AI TTS → real-time audio playback**.

### Key Components
- **`main.py`**: FastAPI app with WebSocket endpoints for real-time audio streaming and REST APIs for file-based chat
- **`services/`**: Modular service layer for STT, LLM, TTS, database, and streaming
- **`models/schemas.py`**: Pydantic models defining all API contracts and error types
- **`static/app.js`**: Complex frontend handling WebSocket audio streaming, real-time transcription, and audio playback
- **`templates/`**: Jinja2 templates with authentication and main app interfaces

### Service Dependencies
Services auto-initialize with graceful fallbacks:
```python
# Pattern: Always check service availability before use
if not llm_service:
    return fallback_response_with_error_type(ErrorType.LLM_ERROR)
```

## Critical Patterns

### WebSocket Streaming Architecture
Real-time audio processing uses `/ws/audio-stream` with these message types:
- `audio_chunk_received` - Binary audio data from frontend
- `final_transcript` - Triggers LLM processing
- `llm_streaming_chunk` - Text streaming to frontend
- `tts_audio_chunk` - Base64 audio chunks for playback

**Session Management**: Sessions persist across WebSocket connections via `session_id` parameter.

### Service Error Handling
All services use `ErrorType` enum for consistent error responses:
```python
# Always wrap external API calls
try:
    result = await external_service.call()
except Exception as e:
    return VoiceChatResponse(error_type=ErrorType.API_ERROR, ...)
```

### Database Patterns
MongoDB with in-memory fallback:
```python
# Standard pattern for DB operations
if database_service and database_service.is_connected():
    result = await database_service.operation()
else:
    # In-memory fallback
    result = self.in_memory_store.get(key, default)
```

### LLM Integration
- **Web Search**: Auto-triggered by query patterns (`"search for"`, `"what is"`, etc.)
- **Personas**: Dynamic persona switching affects response style
- **Streaming**: Uses `generate_streaming_response()` for real-time text generation
- **Context**: Chat history automatically included in prompts

### Authentication System
JWT-based auth with MongoDB persistence and demo fallback users. Protected routes use dependency injection pattern.

## Development Workflows

### Environment Setup
```bash
# Required environment variables
GEMINI_API_KEY=your_key
ASSEMBLYAI_API_KEY=your_key  
MURF_API_KEY=your_key
MONGODB_URL=mongodb://...

# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Workflow
- Test individual services via `/docs` Swagger UI
- Use `/auth/test` endpoint for auth system validation
- Check `/api/backend` for service health status
- WebSocket testing requires frontend or WebSocket client

### Debugging Audio Issues
1. Check browser console for WebSocket connection errors
2. Verify microphone permissions and HTTPS requirements
3. Use streaming status logs in frontend for real-time debugging
4. Audio playback uses Web Audio API - check browser compatibility

## Project-Specific Conventions

### API Response Structure
All endpoints return consistent schemas defined in `models/schemas.py`. Always include:
- `success: bool`
- `message: str` 
- Appropriate error_type for failures

### File Organization
- **Services**: One class per external API (STT, LLM, TTS)
- **Streaming Services**: Separate classes for WebSocket-based services
- **Models**: Pydantic schemas for all request/response types
- **Utils**: Constants, logging, and helper functions

### Frontend Integration
- Session management via URL parameters (`?session_id=...`)
- Real-time status updates through WebSocket messages
- Audio processing uses modern Web APIs (MediaRecorder, AudioContext)
- Glass-morphism UI with responsive design

### Session Handling
Sessions are UUID-based and persist conversation history. Use `get_chat_history()` before LLM calls to maintain context across interactions.

### AI Service Integration
When adding new AI services, follow the pattern:
1. Create service class in `services/`
2. Add initialization in `main.py:initialize_services()`
3. Define Pydantic schemas for requests/responses
4. Implement graceful fallbacks for service failures

This architecture prioritizes real-time performance, graceful degradation, and modular service integration.