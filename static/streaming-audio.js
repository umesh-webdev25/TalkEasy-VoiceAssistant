// 30 Days of AI Voice Agents | Day 16: Streaming Audio
// Record and Stream audio data from client to server using websockets

document.addEventListener('DOMContentLoaded', function () {
    console.log('AI Voice Assistant - Streaming Audio Mode Loaded!');

    // ======================
    // Session Management
    // ======================
    const urlParams = new URLSearchParams(window.location.search);
    let sessionId = urlParams.get('session_id');
    if (!sessionId) {
        sessionId = crypto.randomUUID();
        urlParams.set('session_id', sessionId);
        const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
        window.history.replaceState({}, '', newUrl);
    }

    // ======================
    // WebSocket Audio Streaming
    // ======================
    let ws = null;
    let mediaRecorder = null;
    let audioStream = null;
    let isRecording = false;
    let isStreaming = false;

    // DOM Elements
    const recordBtn = document.getElementById('recordBtn');
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.status-text');
    const llmTranscriptionDisplay = document.getElementById('llmTranscriptionDisplay');
    const llmTranscriptionText = document.getElementById('llmTranscriptionText');
    const llmResponseText = document.getElementById('llmResponseText');
    const llmAudioPlayer = document.getElementById('llmAudioPlayer');

    // ======================
    // WebSocket Connection Management
    // ======================
    function connectWebSocket() {
        if (ws && ws.readyState === WebSocket.OPEN) {
            return ws;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/audio-stream`;
        
        ws = new WebSocket(wsUrl);
        
        ws.onopen = function() {
            console.log('WebSocket audio stream connected');
            updateStatus('Connected - Ready to stream', 'connected');
        };
        
        ws.onclose = function() {
            console.log('WebSocket audio stream disconnected');
            updateStatus('Disconnected', 'disconnected');
        };
        
        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
            updateStatus('Connection error', 'error');
        };
        
        return ws;
    }

    function disconnectWebSocket() {
        if (ws) {
            ws.close();
            ws = null;
        }
    }

    // ======================
    // Audio Streaming Recording
    // ======================
    async function startAudioStreaming() {
        if (!navigator.mediaDevices?.getUserMedia) {
            updateStatus('Your browser does not support audio recording', 'error');
            return;
        }

        try {
            // Connect WebSocket
            connectWebSocket();
            
            // Get audio stream
            audioStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 44100,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });
            
            // Create MediaRecorder for streaming
            mediaRecorder = new MediaRecorder(audioStream, {
                mimeType: 'audio/webm;codecs=opus',
                audioBitsPerSecond: 128000
            });
            
            // Handle data available events
            mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0 && ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(event.data);
                }
            };
            
            // Start recording with data available every 100ms
            mediaRecorder.start(100);
            isStreaming = true;
            isRecording = true;
            
            updateStatus('Streaming audio...', 'streaming');
            
        } catch (error) {
            console.error('Error starting audio streaming:', error);
            updateStatus('Error starting stream', 'error');
        }
    }

    function stopAudioStreaming() {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            isStreaming = false;
            isRecording = false;
            updateStatus('Stream stopped', 'ready');
        }
        
        if (audioStream) {
            audioStream.getTracks().forEach(track => track.stop());
            audioStream = null;
        }
        
        disconnectWebSocket();
    }

    // ======================
    // UI Controls
    // ======================
    function updateStatus(message, type = 'ready') {
        if (statusText) {
            statusText.textContent = message;
        }
        
        // Update button state
        if (recordBtn) {
            if (type === 'streaming') {
                recordBtn.textContent = 'Stop Streaming';
                recordBtn.classList.add('recording');
            } else {
                recordBtn.textContent = 'Start Streaming';
                recordBtn.classList.remove('recording');
            }
        }
    }

    // ======================
    // Event Listeners
    // ======================
    recordBtn?.addEventListener('click', async () => {
        if (!isStreaming) {
            await startAudioStreaming();
        } else {
            stopAudioStreaming();
        }
    });

    // ======================
    // Initialization
    // ======================
    // Test connection on page load
    setTimeout(() => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/audio-stream`;
        
        const testWs = new WebSocket(wsUrl);
        
        testWs.onopen = () => {
            console.log('✅ WebSocket audio stream test connection successful');
            testWs.close();
        };
        
        testWs.onerror = (error) => {
            console.error('❌ WebSocket connection test failed:', error);
        };
    }, 1000);

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        stopAudioStreaming();
    });
});
