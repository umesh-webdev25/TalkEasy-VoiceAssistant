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

### 🎨 Frontend Features
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

---
w