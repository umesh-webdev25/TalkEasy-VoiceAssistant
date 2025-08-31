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
## 🚀 Day 5: Send Audio to the Server

Today I enhanced the Echo Bot by adding audio upload functionality:

### ✅ Completed Tasks:
- **New API Endpoint**: Created `/upload-audio` POST endpoint in FastAPI backend to receive and save audio files to the `uploads` folder
- **Frontend Upload**: Updated `static/app.js` to upload recorded audio to the server when recording stops
- **UI Status**: Added real-time upload status messages in the UI to inform users of upload progress and results
- **File Validation**: Backend validates audio file types and returns metadata (filename, content type, size) upon successful upload

### 🔧 Technical Implementation:
- **Backend**: Implemented file upload handling using FastAPI's `UploadFile` and saved files with unique UUID filenames
- **Frontend**: Used `fetch` API with `FormData` to send audio blobs to the backend
- **User Experience**: Displayed upload progress and success/failure messages dynamically in the UI

### 📁 Uploads Folder:
- Audio files are temporarily saved in the `uploads` directory for further processing or playback

---

## 🚀 Day 6: Transcribe Voice

Today I added the ability to transcribe uploaded audio using AssemblyAI:

### ✅ Completed Tasks:
- **Transcription Endpoint**: Created `/transcribe/file` POST endpoint in FastAPI backend to accept audio files and return transcribed text using AssemblyAI.
- **File Validation**: Backend validates audio file types and handles errors gracefully.
- **Frontend Integration**: Added JavaScript to send recorded audio to `/transcribe/file` and display the transcription and confidence in the UI.

### 🔧 Technical Implementation:
- **Backend**: Used AssemblyAI's Python SDK to transcribe audio files and return transcription, confidence, and word-level details.
- **Frontend**: Added a function to upload audio and display the transcription result in the Echo Bot section.

### 📱 Features:
- **One-click Transcription**: Record and transcribe your voice in the browser.
- **Visual Feedback**: Shows transcription and confidence score in the UI.

---
## 🚀 Day 7: Echo Bot with Murf AI Voice

Today I upgraded the Echo Bot to repeat back what you said, but in a Murf AI voice:

### ✅ Completed Tasks:
- **Echo Endpoint**: Created `/tts/echo` POST endpoint in FastAPI backend.
- **Transcribe & Synthesize**: The endpoint transcribes the uploaded audio using AssemblyAI, then sends the transcription to Murf's TTS API to generate new audio in a Murf voice.
- **Frontend Update**: The Echo Bot now sends the recorded audio to `/tts/echo` and plays back the Murf-generated audio in the UI's `<audio>` element.
- **Transcription Display**: Shows what you said and the confidence score before playing the Murf audio.

### 🔧 Technical Implementation:
- **Backend**: Combined AssemblyAI transcription and Murf TTS in a single endpoint. Returns the Murf audio URL, transcription, and confidence.
- **Frontend**: Updated JavaScript to use `/tts/echo` and play the Murf audio, replacing the old echo playback.

### 📱 Features:
- **AI-Powered Echo**: Hear your own words repeated back in a Murf AI voice.
- **Seamless Experience**: One-click recording, instant Murf playback, and transcription display.

---

## 🚀 Day 8: LLM Query Endpoint with Google Gemini API

Today I integrated Google's Gemini API to create a powerful LLM query endpoint:

### ✅ Completed Tasks:
- **LLM Query Endpoint**: Created `/llm/query` POST endpoint in FastAPI backend
- **Google Gemini Integration**: Integrated Google's Gemini API using the `google-generativeai` Python library
- **Request Validation**: Added `LLMQueryRequest` Pydantic model for proper input validation
- **Flexible Parameters**: Supports configurable max_tokens and temperature settings
- **Comprehensive Error Handling**: Handles API key issues, quota limits, and empty inputs gracefully

### 🔧 Technical Implementation:
- **Backend**: Added Gemini API configuration and query endpoint with proper error handling
- **API Model**: Uses `gemini-1.5-flash` model for text generation
- **Environment**: Requires `GEMINI_API_KEY` in .env file
- **Response Format**: Returns AI-generated response with model info and usage statistics

### 📱 Features:
- **Text-to-AI**: Send any text query and receive AI-generated responses
- **Configurable**: Adjust max_tokens and temperature for different use cases
- **Error Handling**: Clear error messages for API issues
- **Ready for Integration**: Can be easily connected to frontend components

### 🚀 Usage:
```bash
# Test the endpoint
curl -X POST http://localhost:8000/llm/query \
  -H "Content-Type: application/json" \
  -d '{"text": "What are the benefits of voice AI?", "max_tokens": 500}'
```

### 🔑 Setup:
Add your Gemini API key to `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

---

## 🗣️ Day 9: Full Conversation Mode - When the LLM Speaks Back! 🎧🤖

Today my AI Voice Agent officially went full conversation mode—you speak, it listens, thinks, and then talks back in a Murf AI voice! 🔥

### ✅ Completed Tasks:
- **Enhanced LLM Endpoint**: Updated `/llm/query` endpoint to accept audio input directly
- **Voice Transcription**: Integrated AssemblyAI to transcribe recorded voice input
- **AI Intelligence**: Sends transcription to Google's Gemini API for intelligent, context-aware responses
- **Voice Response**: Converts the LLM's text response into natural Murf AI speech
- **Audio Playback**: Plays the AI response in the UI's `<audio>` element for true back-and-forth interaction
- **Character Limit Handling**: Managed Murf's 3000 character limit by ensuring responses stay concise and snappy

### 🔧 Technical Implementation:
- **Backend**: Enhanced `/llm/query` endpoint to accept both text and audio file uploads
- **Audio Processing**: Uses AssemblyAI to transcribe uploaded audio files before sending to Gemini
- **AI Integration**: Leverages Google Gemini API for intelligent, context-aware responses
- **TTS Integration**: Converts AI responses to Murf AI voice using existing TTS infrastructure
- **Frontend**: Updated JavaScript to handle audio recording, upload, and playback seamlessly

### 📱 Features:
- **Voice-to-Voice**: Speak naturally and hear AI responses in Murf's natural voice
- **Context-Aware**: Gemini API provides intelligent responses based on your voice input
- **Seamless Flow**: Record → Transcribe → AI Process → Voice Response → Playback
- **Real-time Feedback**: Shows transcription and AI response before audio playback
- **Character Optimization**: Automatically keeps responses within Murf's limits

### 🎙️ Conversation Flow:
1. **Record**: Click to record your voice message
2. **Process**: Audio is transcribed and sent to Gemini AI
3. **Respond**: AI generates intelligent response based on your query
4. **Speak**: Response converted to Murf AI voice and played back
5. **Continue**: Natural back-and-forth conversation continues

### 🚀 Usage:
```bash
# Test with text (existing functionality)
curl -X POST http://localhost:8000/llm/query \
  -H "Content-Type: application/json" \
  -d '{"text": "What are the benefits of voice AI?"}'

# Test with audio file (new functionality)
curl -X POST http://localhost:8000/llm/query \
  -F "audio=@your_audio_file.wav"
```

### 💡 Experience:
Now it feels like talking to an actual assistant—not just pressing buttons! The voice agent can understand context, provide intelligent responses, and speak back naturally in a high-quality Murf AI voice.

### 🎥 Demo Video:
- **LinkedIn Post**: Successfully posted working conversation mode demo
- **Video Location**: `media/Day 09/2025-08-10 12-57-18.mp4`

--

## 🗣️ Day 10: Chat History - The AI That Remembers Everything! 🧠💬

Today I built the ultimate conversational AI with **persistent chat history** - your AI assistant now remembers every conversation, creating a truly intelligent, context-aware experience!

### ✅ Completed Tasks:
- **Chat History Datastore**: Implemented in-memory datastore for storing conversation history by session_id
- **Enhanced Agent Endpoint**: Created `/agent/chat/{session_id}` endpoint that accepts audio input and maintains conversation context
- **Session Management**: Added session_id parameter to URL for persistent conversations
- **Conversation Context**: AI now uses previous messages as context for more intelligent responses
- **History Viewer**: Added real-time chat history display with refresh and clear functionality
- **Auto-recording**: Recording automatically starts after AI response finishes

### 🔧 Technical Implementation:

**Backend Architecture:**
- **Datastore**: `chat_history.py` with in-memory storage using `ChatHistoryStore` class
- **Session-based**: Each conversation stored with unique session_id
- **Message Format**: Stores role (user/assistant), content, and timestamp
- **Context Integration**: AI responses include conversation history for context-aware answers

**API Endpoints:**
- `POST /agent/chat/{session_id}` - Main chat endpoint with history
- `GET /agent/chat/{session_id}/history` - Retrieve conversation history
- `DELETE /agent/chat/{session_id}` - Clear conversation history

**Frontend Features:**
- **URL Session Management**: Session ID stored in URL parameters
- **Real-time History**: Live chat history display with message styling
- **Auto-refresh**: History updates after each conversation
- **Controls**: Refresh and clear history buttons
- **Visual Feedback**: Styled message bubbles for user/assistant messages

### 📱 Features:
- **Persistent Conversations**: AI remembers previous interactions
- **Context-Aware Responses**: Responses consider entire conversation history
- **Session Management**: Unique sessions for different conversations
- **Visual History**: Real-time conversation display
- **One-click Controls**: Easy history management

### 🎙️ Conversation Flow:
1. **Start**: URL automatically includes session_id
2. **Record**: Speak your question
3. **Process**: Audio → STT → LLM with history → TTS
4. **Respond**: AI provides context-aware response
5. **Store**: Both user and AI messages saved to history
6. **Display**: Real-time conversation history shown
7. **Continue**: Auto-starts recording for next question

### 🚀 Usage:
```bash
# Start a conversation
curl -X POST http://localhost:8000/agent/chat/your-session-id \
  -F "audio=@your_audio_file.wav"

# Get conversation history
curl http://localhost:8000/agent/chat/your-session-id/history

# Clear history
curl -X DELETE http://localhost:8000/agent/chat/your-session-id
```

### 💡 Experience:
Now you have a **true conversational AI** that remembers everything! Each interaction builds on previous conversations, creating more intelligent and contextually relevant responses. The AI doesn't just respond - it **remembers** and **learns** from your ongoing dialogue.

### 🎥 Demo Video:
- **LinkedIn Post**: Successfully posted working chat history demo
- **Video Location**: `media/Day 10/2025-08-11 11-40-48.mp4`

### 🔗 Session URLs:
- Access with session: `http://localhost:8000/?session_id=your-session-id`
- Share session URLs to continue conversations across devices
- Each URL maintains its own conversation history

# Day 11 of 30 Days of AI Voice Agents

## Error Handling Improvements

- Added robust try-except error handling on the server side for Speech-to-Text (STT), Large Language Model (LLM), and Text-to-Speech (TTS) API calls.
- Server returns fallback audio responses and clear error messages when APIs fail.
- Client-side JavaScript enhanced to detect error responses and play a fallback audio message using the SpeechSynthesis API.
- Fallback audio message: "I'm having trouble connecting right now" is played when API errors occur.

## How to Test Error Handling

1. Temporarily comment out or remove API keys (`MURF_API_KEY`, `GEMINI_API_KEY`, `ASSEMBLYAI_API_KEY`) in your `.env` file or environment variables.
2. Restart the FastAPI server.
3. Interact with the voice agent by speaking or submitting text.
4. When an API error occurs, verify that the bot responds with the fallback audio message.
5. Check the console logs for error messages and confirm the fallback behavior.

## Notes

- The fallback audio uses the browser's SpeechSynthesis API for immediate audio feedback.
- This ensures a graceful degradation of service when external APIs are unavailable or misconfigured.

---
## 🚀 Day 12: UI Revamp

Today I revamped the UI to improve user experience and streamline the interface:

### ✅ Completed Tasks:
- Removed the initial Text-to-Speech section and Echo Bot content.
- Kept only the conversational agent UI section.
- Combined the "Start Recording" and "Stop Recording" buttons into a single toggle button that changes status and functionality.
- Hid the audio player; audio now auto-plays as soon as it is loaded.
- Added modern glass-morphism styling with smooth animations.
- Updated the record button to be more prominent with pulse animation during recording.
- Improved overall layout and responsiveness for better usability.

### 🔧 Technical Implementation:
- Updated `templates/index.html` to remove unnecessary sections and implement the new UI structure.
- Enhanced `static/style.css` with new styles for glass-morphism design and animated record button.
- Refactored `static/app.js` to handle single toggle recording button, status updates, and auto-play of AI response audio.

### 🎥 Demo Video:
- UI changes can be tested by running the app locally and interacting with the voice assistant.

### 🚀 Usage:
```bash
uvicorn main:app --reload
```

Open your browser and navigate to `http://localhost:8000` to see the updated UI in action.

---

## 🚀 Day 13: Documentation @Developer

Today I created comprehensive documentation for the project to help developers understand and contribute to the voice agent system:

### ✅ Completed Tasks:
- **README.md Creation**: Wrote a comprehensive README.md file in the root directory covering:
  - Project overview and 30-day development journey
  - Complete feature list and technical capabilities
  - Architecture details and tech stack documentation
  - Step-by-step installation and setup instructions
  - Usage guide with practical examples
  - Environment variables and API key configuration
  - API endpoint documentation with usage examples
  - Troubleshooting guide for common issues
- **Documentation Structure**: Organized content logically with clear sections for easy navigation
- **Developer-Friendly**: Included practical examples, code snippets, and clear instructions
- **Production Ready**: Comprehensive guide suitable for open-source contribution

### 🔧 Technical Implementation:
- **README.md**: Created detailed documentation file with:
  - Project description and objectives
  - Technology stack and architecture overview
  - Installation guide with prerequisites
  - Configuration instructions
  - API documentation
  - Development journey summary
  - Troubleshooting section

### 📱 Features:
- **Complete Documentation**: Everything a developer needs to understand and run the project
- **Step-by-Step Guide**: Clear instructions from setup to deployment
- **API Reference**: All endpoints documented with examples
- **Troubleshooting**: Solutions for common issues
- **Open Source Ready**: Professional documentation suitable for GitHub

### 🚀 Usage:
The README.md file is now ready for:
- New developers to understand the project scope
- Contributors to set up the development environment
- Users to run the voice agent locally
- Open source community to contribute to the project

### 📁 File Location:
- **README.md**: Located in the root directory of the project
- **Access**: Open README.md in any text editor or view on GitHub

---

## 🚀 Day 14: Refactor, Clean Up, and GitHub Upload

Today I refactored the codebase to make it more readable, maintainable, and production-ready, and prepared it for open-source release:

### ✅ Completed Tasks:
- **Code Refactor**: Moved third-party logic (STT, TTS, LLM) into `/services` modules and imported them in endpoint handlers.
- **Schemas**: Defined Pydantic models for request and response types in `/schemas` and used them in all endpoints.
- **Logging**: Added logging throughout the codebase for better traceability and debugging.
- **Cleanup**: Removed unused imports, variables, duplicate code, and unnecessary files.
- **Error Handling**: Centralized error handling using `error_handler.py` for consistent API responses.
- **Documentation**: Ensured `README.md` is up to date and developer-friendly.
- **Ready for GitHub**: Project is organized, documented, and ready for public release.

### 🚀 Next Steps:
- Upload the code to GitHub (if not done yet)
- Make the repository public
- Share the repo link on LinkedIn to showcase progress

### 💡 Experience:
The project is now clean, modular, and easy to maintain. All features are documented, and the codebase is ready for collaboration and open-source contribution.

### Day 15 

⚡ Day 15 of 30 – Murf AI Voice Agent Challenge ⚡
✅ Halfway milestone reached! 🎉

Today’s task was all about WebSockets 🔌. I set up a /ws endpoint on the server to establish a persistent connection between client and server.

Once connected, I tested it with Postman — sending messages to the server and receiving echoed responses back in real-time. 🔄⚡

This is a big step toward making our conversational agent faster, more interactive, and real-time ready. 🚀

Excited for the second half of this challenge! 💪

### Day 16

🎤 Day 16 of 30 – Murf AI Voice Agent Challenge 🎤
Today was all about Streaming Audio with WebSockets 🔊⚡

✨ On the client:
I updated the recording logic to send audio chunks over a websocket connection at regular intervals (instead of accumulating them).

✨ On the server:
Built a /ws handler to receive the binary audio data and save it into a file.
No transcription, LLM, or TTS today — just focusing on getting the raw audio streaming + saving flow working. 📝

This lays the foundation for real-time voice conversations, and I’m super excited about what comes next 🚀

### Day 17

🗣️ Day 17 of 30 – Murf AI Voice Agent Challenge 🗣️

Today was all about WebSockets + AssemblyAI 🎧

✨ Yesterday I streamed audio data from the client to the server using WebSockets.
✨ Today, I integrated AssemblyAI’s Python SDK to transcribe that streaming audio in real-time.

The transcription is being printed directly on the server console 🖥️ (and can also be shown in the UI).

A key step here was ensuring the audio data was in the correct format — 16kHz, 16-bit, mono PCM — as expected by AssemblyAI’s streaming API. ⚡

Super excited to see the bot now listening and transcribing speech live — a big milestone toward building a fully conversational AI agent 🚀

### Day 18 

🎙️ 30 Days of AI Voice Agents | Day 18: Turn Detection 🎙️

Today I explored turn detection with AssemblyAI’s Streaming API 🗣️➡️💻

✨ Turn detection allows the system to identify when the user stops speaking.
✨ Once detected, the server sends a WebSocket message back to the client indicating the end of the turn.
✨ At this point, the final transcription is displayed in the UI 🖥️, giving a clean conversational experience.

This is a powerful feature — it helps build natural, real-time dialogues where the AI knows when it’s your turn vs. when it should respond. 🔄

One more step closer to a fully conversational AI agent 🚀

### Day 19

⚡ Day 19 of 30 - Murf AI Voice Agent Challenge | Streaming LLM Responses 🚀🧵

Today’s milestone was all about making the LLM respond in real time once the transcription is done. Instead of waiting for the full reply at once, I made the response stream directly into the server console.

Here’s what I accomplished:

✅ Once the final transcript is received from AssemblyAI, it’s sent to the LLM API
✅ The LLM now streams its response chunk by chunk into the server console
✅ Accumulated the pieces to build the full response as they arrived
✅ No UI changes needed — streaming happens entirely on the backend

💡 The result? After transcription completes, the LLM immediately starts responding in the server console — giving a feel of real-time conversation flow.

### Day 20

🔌 Day 20 of 30 - Murf AI Voice Agent Challenge | WebSockets + Streaming Audio 🎧⚡

Today’s milestone was about connecting the LLM’s streaming response directly to Murf via WebSockets — making the pipeline even more seamless! 🤖🎙️

Here’s what I accomplished:

✅ Set up a WebSocket connection between the server and Murf
✅ Sent the LLM’s streaming text response directly to Murf in real time
✅ Received the audio output in base64 format from Murf
✅ Printed the base64 encoded audio to the console for verification
✅ No UI changes required — everything happens under the hood

💡 The result? Now, as soon as the LLM starts streaming text, Murf begins streaming back speech in base64, ready to be decoded and played — pushing us closer to a true real-time voice AI loop.
### Day 21

🎉 Day 21 of 30 - Murf AI Voice Agent Challenge | Streaming Audio Data to Client 🔊⚡

✅ 3 Weeks Done, 9 Days To Go! 🚀

Today’s milestone was all about sending audio data directly to the client over WebSockets — making the pipeline fully interactive and end-to-end.

Here’s what I accomplished:

✅ Streamed base64 audio chunks from the server to the client over WebSockets
✅ Accumulated the incoming base64 chunks into an array on the client side
✅ Printed acknowledgements in the console whenever the client received new audio data
✅ Skipped audio playback in the <audio> element for now — focusing purely on streaming flow verification

💡 The result? My client can now receive audio in real time, chunk by chunk, confirming each packet — a huge step toward live, low-latency voice conversations.

### Day 22

🎶 Day 22 of 30 - Murf AI Voice Agent Challenge | Playing Streaming Audio 🎧⚡

Yesterday, I successfully streamed audio data to the client. Today’s milestone was making that audio actually play in the UI — live, as it arrives! 🤖🔊

Here’s what I accomplished:

✅ Handled incoming base64 audio chunks on the client in real time
✅ Converted chunks into audio buffers for playback
✅ Ensured the playback was as seamless as possible — smooth streaming without waiting for the entire response
✅ Built the foundation for true low-latency conversational voice AI

💡 The result? Instead of waiting for the AI to finish speaking, my assistant now plays audio as it streams in — it feels much closer to a real conversation.
### Day 23
🤖 Day 23 of 30 - Murf AI Voice Agent Challenge | Complete Voice Agent 🎯🎧

Today marks a major milestone — I’ve officially connected all the pieces together into a fully working conversational voice agent! 🚀

Here’s what I accomplished:

✅ Captured the user’s query through voice input
✅ Transcribed the audio using AssemblyAI
✅ Sent the transcript (with chat history) to the LLM API
✅ Generated a contextual response and saved it to the chat history
✅ Forwarded the response to Murf for speech synthesis
✅ Streamed the audio back to the client in real time over WebSockets

💡 The result? My AI assistant can now handle a full conversation loop — listening, understanding, responding, and speaking back — all while remembering context. It feels like talking to a real assistant!

### Day 24

🏴‍☠️ Day 24 of 30 - Murf AI Voice Agent Challenge | Agent Persona 🎭🤖

Today’s milestone was about giving my AI Voice Agent a personality — so it doesn’t just talk, it talks with style! ⚡

I decided to make my agent a Pirate 🏴‍☠️⚓

Here’s what I accomplished:

✅ Added a persona layer to the LLM prompts so responses match a specific role
✅ Tuned the agent to speak like a pirate — full of “Ahoy!” and “Matey!” 🗡️
✅ Ensured Murf voices captured the tone and style of the persona
✅ Made conversations more engaging and fun instead of plain AI replies

💡 The result? My AI assistant now feels alive — it doesn’t just answer, it roleplays! Talking to it is like chatting with a pirate crewmate. 🏴‍☠️

### Day 25

🛠️ Day 25 of 30 - Murf AI Voice Agent Challenge | Agent Special Skill ⚡🤖

Today’s milestone was about making my AI Voice Agent more useful by giving it a special skill — so it’s not just conversational, but also actionable! 🚀

Here’s what I accomplished:

✅ Added a new skill module to the agent
✅ Enabled the agent to perform tasks beyond chat (e.g., fetch latest info)
✅ Integrated the skill into the existing conversation flow so it feels natural
✅ Ensured the skill works seamlessly with transcription, LLM response, and Murf speech

💡 The result? My assistant can now do more than just talk — it has a real skill that makes it practical in everyday scenarios.

📰 Day 26 of 30 - Murf AI Voice Agent Challenge | Agent Special Skill 2 ⚡🤖

Yesterday, I gave my AI Voice Agent its first special skill.
Today, I added another — the ability to fetch the latest news in real time! 🗞️✨

Here’s what I accomplished:

✅ Integrated a news API into the agent’s skill set
✅ Allowed the agent to fetch fresh, real-world updates on demand
✅ Blended the news results into the LLM’s conversational flow
✅ Converted the response into Murf-powered speech so the assistant can read out the news naturally

💡 The result? My AI assistant can now act like a personal newsreader, keeping conversations informative and up-to-date.

📹 Posted a demo below where the agent fetches and narrates the latest headlines — sounding less like a bot and more like a helpful companion. 🚀

✨ Day 27 of 30 - Murf AI Voice Agent Challenge | Revamp UI & Code Cleanup 🎨⚡

Today’s milestone was all about polishing things up — improving the UI, codebase, and user experience to get closer to a final product.

Here’s what I accomplished:

✅ Added a config section in the UI where users can enter their own API keys (instead of relying on .env files)
✅ Built the config as a sidebar panel for easy access and flexibility
✅ Did a UI revamp to make the app cleaner and more user-friendly
✅ Performed code cleanup — better structure, reusable components, and simplified flows
✅ Prepped the foundation for adding final touches & features before the finish line

💡 The result? The voice agent now feels less like a dev prototype and more like a real product — customizable, clean, and user-ready.

🌍 Day 28 of 30 - Murf AI Voice Agent Challenge | Deploying the Agent 🚀🤖

With just 2 days left, today’s milestone was all about making my AI Voice Agent accessible to the world by deploying it! 🌐✨

Here’s what I accomplished:

✅ Chose Render as the hosting platform (great free tier + smooth setup)
✅ Deployed the full FastAPI backend + WebSocket services
✅ Configured environment variables and API key management safely
✅ Tested the live deployment end-to-end to ensure transcription → LLM → Murf → streaming audio loop works in production
✅ Shared the deployed link for others to try 🎉

💡 The result? My agent is no longer just running locally — it’s now live on the cloud and can be accessed from anywhere. A huge step toward making it usable for real-world scenarios!

📝 Day 29 of 30 - Murf AI Voice Agent Challenge | Final Documentation 📚⚡

Almost there — just 1 day to go! 🚀

Today’s milestone was all about documenting the journey. I updated my README.md to cover all the features my agent now has — from speech-to-text, chat history, and streaming responses, all the way to Murf-powered audio streaming and special skills like fetching the latest news.

I also wrote a blog post that goes deeper into the 30-day build journey, my learnings, and how everything comes together into a complete conversational AI voice agent.

💡 This project taught me how to combine FastAPI, AssemblyAI, Gemini, Murf, WebSockets, and cloud deployment into a smooth real-time system. Truly feels like building the future of voice tech.