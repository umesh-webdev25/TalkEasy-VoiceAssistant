# 30 Days of AI Voice Agents 🤖🎙️

A comprehensive 30-day journey building sophisticated voice agents using FastAPI, Murf AI, Google Gemini, and AssemblyAI. This project demonstrates the evolution from basic text-to-speech to a full conversational AI assistant with persistent memory.

## 🌟 Features

### Core Capabilities
- **Voice-to-Voice Conversations**: Speak naturally and receive AI responses in Murf AI's natural voice
- **Persistent Chat History**: AI remembers previous conversations across sessions
- **Real-time Transcription**: Convert speech to text using AssemblyAI
- **Intelligent Responses**: Powered by Google Gemini API
- **Modern UI**: Glass-morphism design with smooth animations
- **Error Handling**: Graceful fallbacks when APIs are unavailable

### Technical Features
- **FastAPI Backend**: Modern, async Python web framework
- **Session Management**: Unique conversation sessions via URL parameters
- **Audio Processing**: Record, upload, and process audio files
- **Multi-API Integration**: Seamless integration with multiple AI services
- **Responsive Design**: Works on desktop and mobile devices

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI (Python)
- **AI Services**:
  - Google Gemini API (LLM)
  - Murf AI (Text-to-Speech)
  - AssemblyAI (Speech-to-Text)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Templates**: Jinja2
- **Styling**: Modern CSS with glass-morphism effects

### Project Structure
```
30-days-ai-voice-agents/
├── main.py                 # FastAPI backend server
├── chat_history.py         # Conversation history management
├── error_handler.py        # Error handling utilities
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html       # Main HTML template
├── static/
│   ├── app.js           # Frontend JavaScript
│   └── style.css        # CSS styles
├── uploads/              # Temporary audio file storage
├── media/               # Demo videos and screenshots
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd 30-days-ai-voice-agents
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```bash
   # Required API Keys
   MURF_API_KEY=your_murf_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
   ```

4. **Run the FastAPI server**
   ```bash
   python main.py
   ```
   Or with uvicorn:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the application**
   Open your browser and navigate to: `http://localhost:8000`

## 📖 Usage Guide

### Starting a Conversation
1. Open the application in your browser
2. Click the microphone button to start recording
3. Speak your question or message
4. Release the button to stop recording
5. The AI will process your voice and respond in Murf AI's voice

### Session Management
- **New Session**: Visit `http://localhost:8000` for a new conversation
- **Continue Session**: Use `http://localhost:8000/?session_id=your-session-id` to continue previous conversations
- **Share Sessions**: Share session URLs to continue conversations across devices

### API Endpoints

#### Core Endpoints
- `GET /` - Main application interface
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

#### Voice Agent Endpoints
- `POST /agent/chat/{session_id}` - Main chat endpoint with audio input
- `GET /agent/chat/{session_id}/history` - Retrieve conversation history
- `DELETE /agent/chat/{session_id}` - Clear conversation history

#### Legacy Endpoints (for reference)
- `POST /tts/generate` - Generate TTS from text
- `POST /tts/echo` - Echo bot with Murf AI voice
- `POST /llm/query` - Query LLM with text or audio
- `POST /transcribe/file` - Transcribe audio file

## 🔧 Configuration

### Environment Variables
All required API keys should be set in your `.env` file:

```bash
# Required - Get from respective service websites
MURF_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
ASSEMBLYAI_API_KEY=your_key_here

# Optional - Server configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### API Key Sources
- **Murf AI**: https://murf.ai/
- **Google Gemini**: https://makersuite.google.com/app/apikey
- **AssemblyAI**: https://www.assemblyai.com/

## 🎯 Development Journey

The project evolved through 12 days of development:

| Day | Feature | Description |
|-----|---------|-------------|
| 1-2 | Foundation | FastAPI setup, basic TTS with Murf AI |
| 3-4 | Frontend | HTML interface, voice recording/playback |
| 5-6 | Audio Processing | File upload, transcription with AssemblyAI |
| 7-8 | AI Integration | Echo bot, Google Gemini API integration |
| 9-10 | Conversational AI | Voice-to-voice conversations, chat history |
| 11-12 | Polish | Error handling, UI revamp, glass-morphism design |

## 🐛 Troubleshooting

### Common Issues

**1. API Key Errors**
- Ensure all API keys are correctly set in `.env`
- Check API key validity and quota limits
- Verify network connectivity to external services

**2. Microphone Access**
- Ensure browser has microphone permissions
- Check if HTTPS is required for microphone access
- Try using `http://localhost` instead of `http://127.0.0.1`

**3. Audio Playback Issues**
- Check browser console for JavaScript errors
- Ensure audio format compatibility (MP3/WAV)
- Verify CORS settings for audio<thinking>
The user has requested to create a `README.md` file for the project, detailing the project description, technologies used, architecture, features, and instructions on running the code and API server. The `DailyTasks.md` file provides a comprehensive overview of the project, including objectives, project structure, features, and API endpoints.

Since there are only a few files in the current working directory, I will proceed to read the `DailyTasks.md` file to gather the necessary information for the `README.md`. This will help me understand the project better and create a comprehensive plan for the README file.
</thinking>

