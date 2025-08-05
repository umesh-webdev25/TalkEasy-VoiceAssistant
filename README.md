# 30 Days of Voice Agents Challenge

## Day 1: Project Setup (FastAPI)

Welcome to the 30 Days of Voice Agents Challenge! This project will guide you through building sophisticated voice agents over the course of 30 days using FastAPI.

### 🎯 Day 1 Objectives

- ✅ Set up Python backend using FastAPI
- ✅ Create basic HTML frontend with Jinja2 templates
- ✅ Implement JavaScript for frontend functionality
- ✅ Establish server-client communication
- ✅ Create a foundation for future voice agent features

### 🏗️ Project Structure

```
30 Days of Voice Agents/
├── main.py                 # FastAPI backend server
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html         # Main HTML page (Jinja2 template)
├── static/
│   ├── app.js            # Frontend JavaScript
│   └── style.css         # CSS styles
└── README.md             # This file
```

### 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the FastAPI Server**
   ```bash
   python main.py
   ```

3. **Access the Application**
   Open your browser and navigate to: `http://127.0.0.1:8000`

### 🔧 Features

- **FastAPI Backend**: Modern, fast, and type-safe Python web framework
- **Jinja2 Templates**: Powerful templating engine for dynamic HTML
- **Static File Serving**: CSS and JavaScript files served automatically
- **API Endpoint**: Test endpoint for backend connectivity
- **Responsive Design**: Mobile-friendly interface
- **Real-time Status**: Backend connection monitoring

### 📡 API Endpoints

- `GET /` - Serves the main HTML page
- `GET /api/backend` - Test endpoint returning JSON response
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

---

## 🚀 Day 2 

Today I built my first RESTful Text-to-Speech (TTS) endpoint using FastAPI and Murf's API:

- ✅ Created `/tts/generate` endpoint in FastAPI backend
- ✅ Secured Murf API key using `.env` file
- ✅ Integrated Murf's REST TTS API to generate audio from text
- ✅ Endpoint returns a URL to the generated audio file

**How it works:**
- Send a POST request to `/tts/generate` with your text
- The server calls Murf's API and responds with an audio file URL
- Tested via FastAPI's interactive docs at `localhost:8000/docs`

**Sample FastAPI handler:**
```python
@app.post("/tts/generate")
async def generate_tts(request: TTSRequest):
    api_key = os.getenv("MURF_API_KEY")
    url = "https://api.murf.ai/v1/speech/generate"
    payload = {"text": request.text, "voiceId": "en-US-natalie", "format": "mp3"}
    headers = {"api-key": api_key, "Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    audio_url = data.get("audioFile")
    return {"audio_url": audio_url}
```


## 🚀 Day 3: Text-to-Speech Integration

Today I successfully integrated Murf AI's text-to-speech API into the voice agent system:

### ✅ Completed Tasks:
- **Enhanced Frontend**: Added text input field and submit button to the HTML page
- **Audio Player**: Integrated HTML5 `<audio>` element for seamless audio playback
- **API Integration**: Connected frontend to `/tts/generate` endpoint via POST requests
- **User Experience**: Added loading states and error handling for better UX
- **Auto-play Feature**: Generated audio automatically plays when received

### 🔧 Technical Implementation:
- **Frontend**: Updated `templates/index.html` with new form and audio player
- **JavaScript**: Enhanced `static/app.js` with TTS form handling and audio playback
- **API Communication**: Uses fetch API to send text to Murf AI and receive audio URLs
- **Error Handling**: Comprehensive error messages and fallback mechanisms

---

## 🚀 Day 4: Echo Bot - Voice Recording & Playback

Today I successfully built an Echo Bot that records your voice and plays it back to you:

### ✅ Completed Tasks:
- **Echo Bot Section**: Added new "Echo Bot" section under the TTS section with `<h1>` tag
- **MediaRecorder API**: Implemented browser's MediaRecorder API for audio recording
- **Recording Controls**: Created "Start Recording" and "Stop Recording" buttons
- **Audio Playback**: Integrated HTML `<audio>` element for playing recorded audio
- **Microphone Access**: Handled user permissions and browser compatibility
- **Real-time Feedback**: Added recording status messages and button state management

### 🔧 Technical Implementation:
- **Frontend**: Updated `templates/index.html` with Echo Bot section containing recording controls
- **JavaScript**: Enhanced `static/app.js` with complete MediaRecorder implementation
- **Audio Processing**: Records audio chunks and creates Blob for playback
- **User Experience**: Auto-plays recorded audio after stopping recording
- **Error Handling**: Graceful handling of microphone access denials and browser support

### 📱 Features:
- **One-click Recording**: Simple Start/Stop interface
- **Instant Playback**: Immediate audio playback after recording
- **Visual Feedback**: Clear status messages during recording
- **Cross-browser**: Works on modern browsers supporting MediaRecorder API

### 🎥 Demo Video:
- **LinkedIn Post**: Successfully posted working Echo Bot demo on LinkedIn
- **Video Location**: `screenshots/Day 04/30 Days of Voice Agents _ Day 04 - Google Chrome 2025-08-05 11-37-38.mp4`

---
