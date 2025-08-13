// Modern AI Voice Assistant - Single Button Recording
document.addEventListener('DOMContentLoaded', function () {
    console.log('AI Voice Assistant Loaded!');

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

    // Display current session ID
    document.getElementById('currentSessionId').textContent = sessionId;

    // ======================
    // Chat History Management
    // ======================
    async function loadChatHistory() {
        try {
            const response = await fetch(`/agent/chat/${sessionId}/history`);
            const data = await response.json();
            if (data.success && data.messages.length > 0) {
                displayChatHistory(data.messages);
            } else {
                displayEmptyHistory();
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
            displayEmptyHistory();
        }
    }

    function displayChatHistory(messages) {
        const historyContainer = document.getElementById('chatHistory');
        if (!historyContainer) return;

        historyContainer.innerHTML = '';

        messages.forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${msg.role}`;
            messageDiv.style.cssText = `
                margin: 0.5rem 0;
                padding: 0.75rem;
                border-radius: 8px;
                max-width: 80%;
                ${msg.role === 'user' ?
                    'background: #e3f2fd; margin-left: auto; text-align: right;' :
                    'background: #f3e5f5; margin-right: auto; text-align: left;'}
            `;

            messageDiv.innerHTML = `
                <div class="message-content" style="font-size: 0.9rem;">${msg.content}</div>
                <div class="message-time" style="font-size: 0.7rem; color: #666; margin-top: 0.25rem;">
                    ${new Date(msg.timestamp).toLocaleTimeString()}
                </div>
            `;
            historyContainer.appendChild(messageDiv);
        });

        // Scroll to bottom
        historyContainer.scrollTop = historyContainer.scrollHeight;
    }

    function displayEmptyHistory() {
        const historyContainer = document.getElementById('chatHistory');
        if (historyContainer) {
            historyContainer.innerHTML = '<p class="empty-state">No conversation history yet. Start chatting to see your messages here!</p>';
        }
    }

    // Load chat history on page load
    loadChatHistory();

    // Chat history controls
    document.getElementById('refreshHistoryBtn')?.addEventListener('click', loadChatHistory);

    document.getElementById('clearHistoryBtn')?.addEventListener('click', async () => {
        if (confirm('Are you sure you want to clear the chat history?')) {
            try {
                const response = await fetch(`/agent/chat/${sessionId}`, {
                    method: 'DELETE'
                });
                const data = await response.json();
                if (data.success) {
                    displayEmptyHistory();
                    alert('Chat history cleared successfully!');
                }
            } catch (error) {
                console.error('Error clearing chat history:', error);
                alert('Error clearing chat history');
            }
        }
    });

    // ======================
    // Voice Assistant Functionality
    // ======================
    const recordBtn = document.getElementById('recordBtn');
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.querySelector('.status-text');
    const llmTranscriptionDisplay = document.getElementById('llmTranscriptionDisplay');
    const llmTranscriptionText = document.getElementById('llmTranscriptionText');
    const llmResponseText = document.getElementById('llmResponseText');
    const llmAudioPlayer = document.getElementById('llmAudioPlayer');

    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    // Recording functionality
    recordBtn?.addEventListener('click', async () => {
        if (!navigator.mediaDevices?.getUserMedia) {
            updateStatus('Your browser does not support audio recording', 'error');
            return;
        }

        if (!isRecording) {
            // Start recording
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.onstart = () => {
                    isRecording = true;
                    recordBtn.classList.add('recording');
                    recordBtn.querySelector('.record-text').textContent = 'Stop';
                    updateStatus('Recording...', 'recording');
                };

                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                    }
                };

                mediaRecorder.onstop = async () => {
                    isRecording = false;
                    recordBtn.classList.remove('recording');
                    recordBtn.querySelector('.record-text').textContent = 'Start Recording';
                    updateStatus('Processing...', 'processing');
                    
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    await processLLMQuery(audioBlob);
                    
                    // Clean up stream
                    stream.getTracks().forEach(track => track.stop());
                };

                mediaRecorder.start(100);
            } catch (error) {
                console.error('Microphone access error:', error);
                updateStatus('Microphone access denied', 'error');
            }
        } else {
            // Stop recording
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
        }
    });

    function updateStatus(message, type = 'ready') {
        if (statusIndicator && statusText) {
            statusText.textContent = message;
            
            // Update indicator color based on status
            statusIndicator.className = 'status-indicator';
            if (type === 'recording') {
                statusIndicator.classList.add('recording');
            }
        }
    }

    async function processLLMQuery(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        try {
            const response = await fetch(`/agent/chat/${sessionId}`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `AI processing failed with status ${response.status}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.detail || 'Unknown error occurred');
            }

            // Display transcription
            if (llmTranscriptionText) {
                llmTranscriptionText.textContent = data.transcription || 'No transcription available';
            }
            if (llmTranscriptionDisplay) {
                llmTranscriptionDisplay.style.display = 'block';
            }

            // Display response
            if (llmResponseText) {
                llmResponseText.textContent = data.llm_response || 'No response from AI';
            }

            // Set up and auto-play audio
            if (llmAudioPlayer && data.audio_url) {
                llmAudioPlayer.src = data.audio_url;
                llmAudioPlayer.style.display = 'none'; // Keep hidden but functional
                
                // Auto-play with error handling
                llmAudioPlayer.play().catch(error => {
                    console.log('Auto-play prevented:', error);
                    updateStatus('Response ready (click to play)', 'ready');
                });

                llmAudioPlayer.onended = () => {
                    updateStatus('Ready to record', 'ready');
                    // Optionally restart recording
                    setTimeout(() => {
                        if (recordBtn && !isRecording) {
                            recordBtn.click();
                        }
                    }, 1000);
                };
            }

            updateStatus('Response complete', 'ready');
            
            // Refresh chat history
            loadChatHistory();

        } catch (error) {
            console.error('LLM processing error:', error);
            updateStatus(`Error: ${error.message}`, 'error');
            
            // Play fallback audio message on error
            if ('speechSynthesis' in window) {
                const fallbackUtterance = new SpeechSynthesisUtterance("I'm having trouble connecting right now");
                window.speechSynthesis.speak(fallbackUtterance);
            }
        }
    }
});
