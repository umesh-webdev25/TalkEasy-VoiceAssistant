document.addEventListener("DOMContentLoaded", function () {
  // Global variables
  let sessionId = getSessionIdFromUrl() || generateSessionId();

  // DOM elements
  const toggleChatHistoryBtn = document.getElementById("toggleLogs");

  // Audio streaming variables
  let audioStreamSocket;
  let audioStreamRecorder;
  let audioStreamStream;
  let isStreaming = false;

  // Audio playback variables
  let audioContext = null;
  let audioChunks = [];
  let playheadTime = 0;
  let isPlaying = false;
  let wavHeaderSet = true;
  const SAMPLE_RATE = 44100;

  const audioStreamBtn = document.getElementById("audioStreamBtn");
  const audioStreamStatus = document.getElementById("audioStreamStatus");
  const streamingStatusLog = document.getElementById("streamingStatusLog");
  const connectionStatus = document.getElementById("connectionStatus");
  const streamingSessionId = document.getElementById("streamingSessionId");
  const chatHistoryList = document.getElementById("chatHistoryList");

  // Initialize session
  initializeSession();

  // Event listeners
  if (toggleChatHistoryBtn) {
    toggleChatHistoryBtn.addEventListener("click", toggleLogs);
  }

  // Conversation history elements
  const toggleConversationBtn = document.getElementById("toggleCnversation");
  const conversationHistoryPopup = document.getElementById("conversationHistoryPopup");
  const closeConversationPopup = document.getElementById("closeConversationPopup");
  const refreshConversationsBtn = document.getElementById("refreshConversations");
  const conversationList = document.getElementById("conversationList");
  const conversationMessages = document.getElementById("conversationMessages");
  const selectedConversationInfo = document.getElementById("selectedConversationInfo");

  // Function to toggle conversation history popup
  function toggleConversationHistory() {
    if (conversationHistoryPopup.style.display === "none" || conversationHistoryPopup.style.display === "") {
      loadConversationHistory();
      conversationHistoryPopup.style.display = "block";
    } else {
      conversationHistoryPopup.style.display = "none";
    }
  }

  // Function to close conversation history popup
  function closeConversationHistory() {
    conversationHistoryPopup.style.display = "none";
  }

  // Function to load conversation history
  async function loadConversationHistory() {
    try {
      const response = await fetch(`/agent/chat/history?session_id=${sessionId}`);
      const data = await response.json();
      if (data.success && data.messages.length > 0) {
        displayConversationList(data.messages);
      } else {
        conversationList.innerHTML = '<p class="no-history">No conversations found.</p>';
      }
    } catch (error) {
      console.error("Failed to load conversation history:", error);
    }
  }

  // Function to display conversation list
  function displayConversationList(conversations) {
    conversationList.innerHTML = ""; // Clear existing list
    conversations.forEach(conversation => {
      const listItem = document.createElement("div");
      listItem.className = "conversation-list-item";
      listItem.textContent = `Session ID: ${conversation.session_id} - Messages: ${conversation.message_count}`;
      listItem.onclick = () => loadConversationMessages(conversation.session_id);
      conversationList.appendChild(listItem);
    });
  }

  // Function to load messages for a selected conversation
  async function loadConversationMessages(sessionId) {
    try {
      const response = await fetch(`/agent/chat/history?session_id=${sessionId}`);
      const data = await response.json();
      if (data.success) {
        displayConversationMessages(data.messages);
        selectedConversationInfo.textContent = `Showing messages for session: ${sessionId}`;
      }
    } catch (error) {
      console.error("Failed to load conversation messages:", error);
    }
  }

  // Function to display messages for a selected conversation
  function displayConversationMessages(messages) {
    conversationMessages.innerHTML = ""; // Clear existing messages
    messages.forEach(message => {
      const messageDiv = document.createElement("div");
      messageDiv.className = "chat-message";
      messageDiv.innerHTML = `
        <div class="message-header">
          <span class="message-role">${message.role === 'user' ? '👤 You' : '🤖 AI Assistant'}</span>
          <small class="message-time">${new Date(message.timestamp).toLocaleString()}</small>
        </div>
        <div class="message-content">${message.content}</div>
      `;
      conversationMessages.appendChild(messageDiv);
    });
  }
  if (toggleConversationBtn) {
    toggleConversationBtn.addEventListener("click", toggleConversationHistory);
  }

  if (closeConversationPopup) {
    closeConversationPopup.addEventListener("click", closeConversationHistory);
  }

  if (refreshConversationsBtn) {
    refreshConversationsBtn.addEventListener("click", loadConversationHistory);
  }

  // Initialize streaming mode
  initializeStreamingMode();

  function getSessionIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get("session_id");
  }

  function generateSessionId() {
    return (
      "session_" + Math.random().toString(36).substr(2, 9) + "_" + Date.now()
    );
  }

  function updateUrlWithSessionId(sessionId) {
    const url = new URL(window.location);
    url.searchParams.set("session_id", sessionId);
    window.history.replaceState({}, "", url);
    const sessionIdElement = document.getElementById("sessionId");
    if (sessionIdElement) {
      sessionIdElement.textContent = sessionId;
    }
  }

  async function initializeSession() {
    updateUrlWithSessionId(sessionId);
    await loadChatHistory();
  }

  function initializeStreamingMode() {
    const audioStreamBtn = document.getElementById("audioStreamBtn");
    if (audioStreamBtn) {
      audioStreamBtn.addEventListener("click", function () {
        const state = this.getAttribute("data-state");
        if (state === "ready") {
          startAudioStreaming();
        } else if (state === "recording") {
          stopAudioStreaming();
        }
      });
    }

    resetStreamingState();
  }

  async function loadChatHistory() {
    try {
      const response = await fetch(`/agent/chat/history?session_id=${sessionId}`);
      const data = await response.json();
      if (data.success && data.messages.length > 0) {
        displayChatHistory(data.messages);
      }
    } catch (error) {
      console.error("Failed to load chat history:", error);
    }
  }

  function displayChatHistory(messages, isNewMessage = false) {
    const chatHistoryList = document.getElementById("chatHistoryList");
    if (!chatHistoryList) return;

    // If it's a new message, don't clear the existing content
    if (!isNewMessage) {
      chatHistoryList.innerHTML = "";
    }

    if (messages.length === 0 && !isNewMessage) {
      chatHistoryList.innerHTML =
        '<p class="no-history">No previous messages in this session.</p>';
      return;
    }

    // Process messages
    messages.forEach((message, index) => {
      // Check if this message already exists to avoid duplicates
      const existingMessage = document.querySelector(`[data-message-id="${message.id || index}"]`);
      if (existingMessage && !isNewMessage) {
        return; // Skip if already exists and we're not adding a new message
      }

      const messageDiv = document.createElement("div");
      messageDiv.className = `chat-message ${message.role} ${isNewMessage ? 'new' : ''}`;
      messageDiv.setAttribute("data-message-id", message.id || index);

      // Parse markdown content if available
      let messageContent = message.content;
      try {
        if (typeof marked !== "undefined") {
          messageContent = marked.parse(message.content);
        }
      } catch (error) {
        console.warn("Markdown parsing error:", error);
      }

      messageDiv.innerHTML = `
          <div class="message-header">
            <span class="message-role">${message.role === 'user' ? '👤 You' : '🤖 AI Assistant'}</span>
            <small class="message-time">${new Date(
        message.timestamp || Date.now()
      ).toLocaleString()}</small>
          </div>
          <div class="message-content">${messageContent}</div>
        `;

      // If it's a new message, add it to the bottom and scroll to it
      if (isNewMessage) {
        chatHistoryList.appendChild(messageDiv);

        // Apply syntax highlighting if available
        if (typeof hljs !== "undefined") {
          messageDiv.querySelectorAll("pre code").forEach((block) => {
            hljs.highlightElement(block);
          });
        }

        // Scroll to the new message
        setTimeout(() => {
          messageDiv.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }, 100);
      } else {
        chatHistoryList.appendChild(messageDiv);
      }
    });

    // Apply syntax highlighting to all code blocks if available
    if (typeof hljs !== "undefined" && !isNewMessage) {
      chatHistoryList.querySelectorAll("pre code").forEach((block) => {
        hljs.highlightElement(block);
      });
    }

    // Scroll to bottom if it's not a new message (initial load)
    if (!isNewMessage) {
      setTimeout(() => {
        chatHistoryList.scrollTop = chatHistoryList.scrollHeight;
      }, 100);
    }
  }

  function toggleLogs() {
    if (audioStreamStatus) {
      const isVisible = audioStreamStatus.style.display !== "none";
      audioStreamStatus.style.display = isVisible ? "none" : "block";

      if (toggleChatHistoryBtn) {
        toggleChatHistoryBtn.textContent = isVisible
          ? "Show Streaming Logs"
          : "Hide Streaming Logs";
      }
    }
  }

  function showMessage(message, type) {
    // Simple console log for now - can be enhanced with UI notifications
  }

  // ==================== AUDIO STREAMING FUNCTIONALITY ====================

  async function startAudioStreaming() {
    try {
      // Reset streaming state and UI
      resetStreamingState();

      updateConnectionStatus("connecting", "Connecting...");

      // Clear any previous transcriptions
      clearPreviousTranscriptions();

      // Connect to WebSocket with session ID
      audioStreamSocket = new WebSocket(`ws://localhost:8000/ws/audio-stream?session_id=${sessionId}`);

      audioStreamSocket.onopen = function (event) {
        updateConnectionStatus("connected", "Connected");
        updateStreamingStatus("Connected to server", "success");

        // Send session ID to establish the session on the backend
        audioStreamSocket.send(JSON.stringify({
          type: "session_id",
          session_id: sessionId
        }));
      };

      audioStreamSocket.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.type === "audio_stream_ready") {
          updateStreamingStatus(
            `Ready to stream audio with transcription. Session: ${data.session_id}`,
            "info"
          );
          streamingSessionId.textContent = `Session: ${data.session_id}`;

          // Ensure the frontend session ID matches the backend
          if (data.session_id !== sessionId) {
            sessionId = data.session_id;
            updateUrlWithSessionId(sessionId);
          }

          if (data.transcription_enabled) {
            updateStreamingStatus("🎙️ Real-time transcription enabled", "success");
          }
          startRecordingForStreaming();
        } else if (data.type === "final_transcript") {
          // Display final transcription in chat history
          if (data.text && data.text.trim()) {
            addUserMessageToHistory(data.text);
          }
        } else if (data.type === "partial_transcript") {
          // Show partial transcripts in chat history
          if (data.text && data.text.trim()) {
            updateUserMessageInHistory(data.text);
          }
        } else if (data.type === "llm_streaming_start") {
          // Add AI response placeholder with dots loader
          addAIResponsePlaceholder();
        } else if (data.type === "llm_streaming_chunk") {
          // Display LLM text chunks as they arrive
          updateAIResponse(data.chunk, data.accumulated_length);
        } else if (data.type === "tts_audio_chunk") {
          // Handle audio base64 chunks from TTS
          handleAudioChunk(data);
        } else if (data.type === "llm_streaming_complete") {
          // Finalize AI response
          finalizeAIResponse(data.complete_response);

          // Reload chat history after conversation is complete
          setTimeout(() => {
            loadChatHistory();
          }, 1000);
        } else if (data.type === "transcription_complete") {
          if (data.text && data.text.trim()) {
            updateStreamingStatus(`✅ COMPLETE TRANSCRIPTION: "${data.text}"`, "success");
          } else {
            updateStreamingStatus("⚠️ No speech detected in recording", "warning");
          }
        } else if (data.type === "transcription_error") {
          updateStreamingStatus("❌ Transcription error: " + data.message, "error");
        } else if (data.type === "llm_streaming_error") {
          updateStreamingStatus(`❌ ${data.message}`, "error");
          removeAIResponsePlaceholder();
        } else if (data.type === "tts_streaming_error") {
          updateStreamingStatus(`❌ ${data.message}`, "error");
        }
      };

      audioStreamSocket.onerror = function (error) {
        console.error("WebSocket error:", error);
        updateConnectionStatus("error", "Connection Error");
        updateStreamingStatus("WebSocket connection error", "error");
      };

      audioStreamSocket.onclose = function (event) {
        updateConnectionStatus("disconnected", "Disconnected");
        updateStreamingStatus("Connection closed", "warning");
      };
    } catch (error) {
      console.error("Error starting audio streaming:", error);
      updateConnectionStatus("error", "Error");
      updateStreamingStatus(
        "Error starting streaming: " + error.message,
        "error"
      );
    }
  }

  // Add user message to chat history
  function addUserMessageToHistory(text) {
    const message = {
      role: 'user',
      content: text,
      timestamp: Date.now()
    };

    // Check if the message already exists to avoid duplicates
    const existingMessage = document.querySelector(`[data-message-id="${message.id}"]`);
    if (!existingMessage) {
        displayChatHistory([message], true);
    }
  }

  // Update user message in chat history (for partial transcripts)
  function updateUserMessageInHistory(text) {
    let userMessage = document.querySelector('.chat-message.user:last-child');

    if (!userMessage) {
      addUserMessageToHistory(text);
      return;
    }

    const contentDiv = userMessage.querySelector('.message-content');
    if (contentDiv) {
      contentDiv.textContent = text;
    }

    // Scroll to the message
    setTimeout(() => {
      userMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
  }

  // Add AI response placeholder with dots loader
  function addAIResponsePlaceholder() {
    const messageDiv = document.createElement("div");
    messageDiv.className = "chat-message assistant";
    messageDiv.setAttribute("data-message-id", "ai-response-placeholder");
    messageDiv.innerHTML = `
          <div class="message-header">
            <span class="message-role">🤖 AI Assistant</span>
            <small class="message-time">${new Date().toLocaleString()}</small>
          </div>
          <div class="message-content">
            <div class="dots-loader">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        `;

    chatHistoryList.appendChild(messageDiv);

    // Scroll to the message
    setTimeout(() => {
      messageDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
  }

  // Update AI response with new content
  function updateAIResponse(chunk, accumulatedLength) {
    let aiMessage = document.querySelector('.chat-message.assistant:last-child');

    if (!aiMessage || !aiMessage.querySelector('.dots-loader')) {
      return;
    }

    const contentDiv = aiMessage.querySelector('.message-content');
    if (contentDiv) {
      // Remove dots loader if it exists
      const dotsLoader = contentDiv.querySelector('.dots-loader');
      if (dotsLoader) {
        contentDiv.removeChild(dotsLoader);
      }

      // Add the new content
      let currentText = contentDiv.textContent || '';
      contentDiv.textContent = currentText + chunk;
    }

    // Scroll to the message
    setTimeout(() => {
      aiMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
  }

  // Finalize AI response with complete content
  function finalizeAIResponse(completeResponse) {
    let aiMessage = document.querySelector('.chat-message.assistant:last-child');

    if (!aiMessage) {
      return;
    }

    const contentDiv = aiMessage.querySelector('.message-content');
    if (contentDiv) {
      // Remove dots loader if it exists
      const dotsLoader = contentDiv.querySelector('.dots-loader');
      if (dotsLoader) {
        contentDiv.removeChild(dotsLoader);
      }

      // Set the complete response
      contentDiv.textContent = completeResponse;

      // Parse as Markdown if available
      try {
        if (typeof marked !== "undefined") {
          const markdownHtml = marked.parse(completeResponse);
          contentDiv.innerHTML = markdownHtml;

          // Apply syntax highlighting if available
          if (typeof hljs !== "undefined") {
            contentDiv.querySelectorAll("pre code").forEach((block) => {
              hljs.highlightElement(block);
            });
          }
        }
      } catch (error) {
        console.warn("Markdown parsing error:", error);
      }
    }

    // Scroll to the message
    setTimeout(() => {
      aiMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
  }

  // Remove AI response placeholder (in case of error)
  function removeAIResponsePlaceholder() {
    const placeholder = document.querySelector('[data-message-id="ai-response-placeholder"]');
    if (placeholder) {
      placeholder.remove();
    }
  }

  async function startRecordingForStreaming() {
    try {
      audioStreamStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,  // 16kHz for AssemblyAI
          channelCount: 1,    // Mono
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        },
      });

      const audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 16000
      });

      const source = audioContext.createMediaStreamSource(audioStreamStream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);

      processor.onaudioprocess = function (e) {
        if (audioStreamSocket && audioStreamSocket.readyState === WebSocket.OPEN) {
          const inputData = e.inputBuffer.getChannelData(0);
          const pcmData = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            pcmData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32767));
          }
          audioStreamSocket.send(pcmData.buffer);
        }
      };

      source.connect(processor);
      processor.connect(audioContext.destination);

      // Store references for cleanup
      audioStreamRecorder = {
        stop: () => {
          processor.disconnect();
          source.disconnect();
          audioContext.close();
        }
      };

      isStreaming = true;
      if (audioStreamBtn) {
        audioStreamBtn.innerHTML =
          '<span class="btn-icon">⏹️</span><span class="btn-text">Stop Conversation</span>';
        audioStreamBtn.className = "btn danger";
        audioStreamBtn.setAttribute("data-state", "recording");
      }

      updateConnectionStatus("recording", "Recording & Streaming");
      updateStreamingStatus("Recording and streaming audio...", "recording");
      if (
        audioStreamSocket &&
        audioStreamSocket.readyState === WebSocket.OPEN
      ) {
        audioStreamSocket.send("start_streaming");
      }
    } catch (error) {
      console.error("Error starting recording for streaming:", error);
      updateConnectionStatus("error", "Recording Error");
      updateStreamingStatus(
        "Error starting recording: " + error.message,
        "error"
      );
    }
  }

  async function stopAudioStreaming() {
    try {
      isStreaming = false;

      // Stop the audio recording (either MediaRecorder or custom processor)
      if (audioStreamRecorder) {
        if (typeof audioStreamRecorder.stop === 'function') {
          audioStreamRecorder.stop();
        }
        audioStreamRecorder = null;
      }

      // Stop media stream
      if (audioStreamStream) {
        audioStreamStream.getTracks().forEach((track) => track.stop());
        audioStreamStream = null;
      }
      if (
        audioStreamSocket &&
        audioStreamSocket.readyState === WebSocket.OPEN
      ) {
        audioStreamSocket.send("stop_streaming");
      }

      // Close WebSocket after a short delay to allow final messages
      setTimeout(() => {
        if (audioStreamSocket) {
          audioStreamSocket.close();
        }
      }, 1000);

      // Update UI
      if (audioStreamBtn) {
        audioStreamBtn.innerHTML =
          '<span class="btn-icon">🎤</span><span class="btn-text">Start Conversation</span>';
        audioStreamBtn.className = "btn primary";
        audioStreamBtn.setAttribute("data-state", "ready");
      }

      updateConnectionStatus("disconnected", "Disconnected");
      updateStreamingStatus("Audio streaming stopped", "info");
    } catch (error) {
      console.error("Error stopping audio streaming:", error);
      updateStreamingStatus(
        "Error stopping streaming: " + error.message,
        "error"
      );
    }
  }

  function updateConnectionStatus(status, text) {
    if (connectionStatus) {
      connectionStatus.className = `status-badge ${status}`;
      connectionStatus.textContent = text;
    }
  }

  function updateStreamingStatus(message, type) {
    if (streamingStatusLog && audioStreamStatus) {
      const statusEntry = document.createElement("div");
      statusEntry.className = `streaming-status ${type}`;
      statusEntry.innerHTML = `
            <strong>${new Date().toLocaleTimeString()}</strong>: ${message}
          `;

      streamingStatusLog.appendChild(statusEntry);
      streamingStatusLog.scrollTop = streamingStatusLog.scrollHeight;
    }
  }

  function resetStreamingState() {
    // Clear status log
    if (streamingStatusLog) {
      streamingStatusLog.innerHTML = '';
    }
    resetAudioPlayback();
  }

  function clearPreviousTranscriptions() {
    // Clear any temporary messages
    removeAIResponsePlaceholder();
  }

  function handleAudioChunk(audioData) {
    // Play the audio chunk for streaming
    playAudioChunk(audioData.audio_base64);

    // Update UI with basic audio streaming progress
    updateStreamingStatus(
      `Audio chunk received (${audioData.chunk_size} bytes)`,
      "success"
    );
  }

  function initializeAudioContext() {
    try {
      if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        playheadTime = audioContext.currentTime;
      }
      return true;
    } catch (error) {
      console.error('Failed to initialize audio context:', error);
      return false;
    }
  }

  function base64ToPCMFloat32(base64) {
    try {
      let binary = atob(base64);
      const offset = wavHeaderSet ? 44 : 0; // Skip WAV header if present

      if (wavHeaderSet) {
        wavHeaderSet = false; // Only process header once
      }

      const length = binary.length - offset;
      const buffer = new ArrayBuffer(length);
      const byteArray = new Uint8Array(buffer);

      for (let i = 0; i < byteArray.length; i++) {
        byteArray[i] = binary.charCodeAt(i + offset);
      }

      const view = new DataView(byteArray.buffer);
      const sampleCount = byteArray.length / 2; // 16-bit samples
      const float32Array = new Float32Array(sampleCount);

      for (let i = 0; i < sampleCount; i++) {
        const int16 = view.getInt16(i * 2, true); // Little endian
        float32Array[i] = int16 / 32768; // Convert to float32 range [-1, 1]
      }

      return float32Array;
    } catch (error) {
      console.error('Error converting base64 to PCM:', error);
      return null;
    }
  }

  function chunkPlay() {
    if (audioChunks.length > 0) {
      const chunk = audioChunks.shift();

      if (audioContext.state === "suspended") {
        audioContext.resume();
      }

      try {
        const buffer = audioContext.createBuffer(1, chunk.length, SAMPLE_RATE);
        buffer.copyToChannel(chunk, 0);

        const source = audioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(audioContext.destination);

        const now = audioContext.currentTime;
        if (playheadTime < now) {
          playheadTime = now + 0.05; // Add small delay to prevent audio gaps
        }

        source.start(playheadTime);
        playheadTime += buffer.duration;

        updatePlaybackStatus(`Playing audio chunk`);

        // Continue playing remaining chunks
        if (audioChunks.length > 0) {
          chunkPlay();
        } else {
          isPlaying = false;
          updatePlaybackStatus('Audio streaming paused - waiting for more chunks...');
        }
      } catch (error) {
        console.error('Error playing audio chunk:', error);
        isPlaying = false;
        hideAudioPlaybackIndicator();
      }
    }
  }

  function playAudioChunk(base64Audio) {
    try {
      // Initialize audio context if not already done
      if (!initializeAudioContext()) {
        return;
      }

      // Show audio playback indicator
      showAudioPlaybackIndicator();

      // Convert base64 to PCM data
      const float32Array = base64ToPCMFloat32(base64Audio);
      if (!float32Array || float32Array.length === 0) {
        return;
      }

      // Add chunk to playback queue
      audioChunks.push(float32Array);

      // Start playback if not already playing
      if (!isPlaying && (playheadTime <= audioContext.currentTime + 0.1 || audioChunks.length >= 2)) {
        isPlaying = true;
        audioContext.resume().then(() => {
          chunkPlay();
        });
      }
    } catch (error) {
      console.error('Error in playAudioChunk:', error);
    }
  }

  function resetAudioPlayback() {
    audioChunks = [];
    isPlaying = false;
    wavHeaderSet = true;

    if (audioContext) {
      playheadTime = audioContext.currentTime;
    }

    hideAudioPlaybackIndicator();
  }

  /**
   * Show the audio playback indicator with animation
   */
  function showAudioPlaybackIndicator() {
    const playbackContainer = document.getElementById('audioPlaybackStatus');
    if (playbackContainer) {
      playbackContainer.style.display = 'block';

      // Update status text
      const statusText = document.getElementById('playbackStatusText');
      if (statusText) {
        statusText.textContent = 'Audio is streaming and playing...';
      }
    }
  }

  /**
   * Hide the audio playback indicator
   */
  function hideAudioPlaybackIndicator() {
    const playbackContainer = document.getElementById('audioPlaybackStatus');
    if (playbackContainer) {
      playbackContainer.style.display = 'none';
    }
  }

  /**
   * Update playback status text
   */
  function updatePlaybackStatus(text) {
    const statusText = document.getElementById('playbackStatusText');
    if (statusText) {
      statusText.textContent = text;
    }
  }
});