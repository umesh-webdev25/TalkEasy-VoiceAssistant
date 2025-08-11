// FastAPI Voice Agents App with Text-to-Speech, Echo Bot, and Voice-to-LLM functionality

document.addEventListener('DOMContentLoaded', function () {
    console.log('FastAPI Voice Agents App Loaded!');

    // Get session ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    let sessionId = urlParams.get('session_id');
    if (!sessionId) {
        sessionId = crypto.randomUUID();
        urlParams.set('session_id', sessionId);
        const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
        window.history.replaceState({}, '', newUrl);
    }

    // Text-to-Speech functionality
    const ttsForm = document.getElementById('ttsForm');
    const textInput = document.getElementById('textInput');
    const audioContainer = document.getElementById('audioContainer');
    const audioPlayer = document.getElementById('audioPlayer');
    const ttsMessage = document.getElementById('ttsMessage');

    if (ttsForm && textInput && audioContainer && audioPlayer && ttsMessage) {
        ttsForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const text = textInput.value.trim();
            if (!text) {
                ttsMessage.textContent = 'Please enter some text.';
                ttsMessage.style.display = 'block';
                return;
            }

            ttsMessage.textContent = 'Generating audio...';
            ttsMessage.style.display = 'block';
            audioContainer.style.display = 'none';
            audioPlayer.src = '';

            try {
                const response = await fetch('/tts/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: text })
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
                }

                const data = await response.json();
                const audioUrl = data.audio_url;

                if (!audioUrl) {
                    throw new Error('No audio URL returned');
                }

                audioPlayer.src = audioUrl;
                audioContainer.style.display = 'block';
                ttsMessage.textContent = 'Audio generated successfully!';

                // Auto-play the audio
                audioPlayer.play().catch(error => {
                    console.log('Auto-play prevented:', error);
                    ttsMessage.textContent = 'Audio ready (click play to listen)';
                });

            } catch (error) {
                console.error('TTS Error:', error);
                ttsMessage.textContent = 'Error generating audio: ' + (error.message || 'Unknown error');
                ttsMessage.style.color = 'red';
            }
        });
    }

    // Voice to LLM Assistant functionality
    const startLLMRecordingBtn = document.getElementById('startLLMRecordingBtn');
    const stopLLMRecordingBtn = document.getElementById('stopLLMRecordingBtn');
    const llmRecordingStatus = document.getElementById('llmRecordingStatus');
    const llmTranscriptionDisplay = document.getElementById('llmTranscriptionDisplay');
    const llmTranscriptionText = document.getElementById('llmTranscriptionText');
    const llmResponseText = document.getElementById('llmResponseText');
    const llmAudioContainer = document.getElementById('llmAudioContainer');
    const llmAudioPlayer = document.getElementById('llmAudioPlayer');

    let llmMediaRecorder;
    let llmAudioChunks = [];

    if (startLLMRecordingBtn && stopLLMRecordingBtn && llmRecordingStatus) {
        startLLMRecordingBtn.addEventListener('click', async () => {
            if (!navigator.mediaDevices?.getUserMedia) {
                llmRecordingStatus.textContent = 'Your browser does not support audio recording or you may need to allow microphone access.';
                llmRecordingStatus.style.display = 'block';
                llmRecordingStatus.style.color = 'red';
                return;
            }

            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                llmMediaRecorder = new MediaRecorder(stream);

                llmMediaRecorder.onstart = () => {
                    llmAudioChunks = [];
                    llmRecordingStatus.style.display = 'block';
                    llmRecordingStatus.textContent = 'Recording...';
                    llmRecordingStatus.style.color = 'inherit';
                    startLLMRecordingBtn.disabled = true;
                    stopLLMRecordingBtn.disabled = false;
                    if (llmAudioContainer) llmAudioContainer.style.display = 'none';
                    if (llmAudioPlayer) llmAudioPlayer.src = '';
                    if (llmTranscriptionDisplay) llmTranscriptionDisplay.style.display = 'none';
                    if (llmResponseText) llmResponseText.textContent = '';
                };

                llmMediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        llmAudioChunks.push(event.data);
                    }
                };

                llmMediaRecorder.onstop = async () => {
                    llmRecordingStatus.textContent = 'Processing with AI...';
                    const audioBlob = new Blob(llmAudioChunks, { type: 'audio/webm' });
                    
                    try {
                        await processLLMQuery(audioBlob);
                    } catch (error) {
                        console.error('LLM processing error:', error);
                        llmRecordingStatus.textContent = `Error: ${error.message}`;
                        llmRecordingStatus.style.color = 'red';
                    } finally {
                        stream.getTracks().forEach(track => track.stop());
                        startLLMRecordingBtn.disabled = false;
                        stopLLMRecordingBtn.disabled = true;
                    }
                };

                llmMediaRecorder.start(100);
            } catch (error) {
                console.error('Microphone access error:', error);
                llmRecordingStatus.textContent = `Error: ${error.message}`;
                llmRecordingStatus.style.display = 'block';
                llmRecordingStatus.style.color = 'red';
                startLLMRecordingBtn.disabled = false;
                stopLLMRecordingBtn.disabled = true;
            }
        });

        stopLLMRecordingBtn.addEventListener('click', () => {
            if (llmMediaRecorder?.state === 'recording') {
                llmMediaRecorder.stop();
            }
        });
    }

    async function processLLMQuery(audioBlob) {
        if (!llmRecordingStatus) return;

        llmRecordingStatus.textContent = 'Processing with AI...';
        llmRecordingStatus.style.display = 'block';
        llmRecordingStatus.style.color = 'inherit';

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

            // Set up audio player
            if (llmAudioPlayer && data.audio_url) {
                llmAudioPlayer.src = data.audio_url;
            }
            if (llmAudioContainer) {
                llmAudioContainer.style.display = 'block';
            }

            llmRecordingStatus.textContent = 'AI response ready!';

            // Auto-play the audio and start recording again after audio ends
            if (llmAudioPlayer && startLLMRecordingBtn) {
                llmAudioPlayer.play().then(() => {
                    llmAudioPlayer.onended = () => {
                        if (startLLMRecordingBtn) startLLMRecordingBtn.click();
                    };
                }).catch(error => {
                    console.log('Auto-play prevented:', error);
                    llmRecordingStatus.textContent = 'AI response ready (click play to listen)';
                });
            }

            return data;

        } catch (error) {
            console.error('LLM processing error:', error);
            if (llmRecordingStatus) {
                llmRecordingStatus.textContent = `Processing failed: ${error.message}`;
                llmRecordingStatus.style.color = 'red';
            }
            throw error;
        }
    }
});