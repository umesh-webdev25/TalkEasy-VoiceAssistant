// FastAPI Voice Agents App with Text-to-Speech, Echo Bot, and Voice-to-LLM functionality

document.addEventListener('DOMContentLoaded', function () {
    console.log('FastAPI Voice Agents App Loaded!');

    // Backend message functionality
    const getMessageBtn = document.getElementById('getMessageBtn');
    const messageDisplay = document.getElementById('messageDisplay');

    if (getMessageBtn && messageDisplay) {
        getMessageBtn.addEventListener('click', async function () {
            getMessageBtn.textContent = 'Loading...';
            getMessageBtn.disabled = true;

            try {
                const response = await fetch('/api/backend');
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();

                messageDisplay.innerHTML = `
                    <div class="success-message">
                        ${data.message}
                    </div>
                `;
            } catch (error) {
                console.error('Backend connection error:', error);
                messageDisplay.innerHTML = `
                    <div class="error-message">
                        Could not connect to backend: ${error.message}
                    </div>
                `;
            } finally {
                getMessageBtn.textContent = 'Fetch Message';
                getMessageBtn.disabled = false;
            }
        });
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

            try {
                const response = await fetch('/tts/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: text })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
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
                ttsMessage.textContent = 'Error generating audio: ' + error.message;
            }
        });
    }

    // Echo Bot functionality
    const startRecordingBtn = document.getElementById('startRecordingBtn');
    const stopRecordingBtn = document.getElementById('stopRecordingBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const echoAudioContainer = document.getElementById('echoAudioContainer');
    const echoAudioPlayer = document.getElementById('echoAudioPlayer');

    let mediaRecorder;
    let audioChunks = [];

    if (startRecordingBtn && stopRecordingBtn && recordingStatus && echoAudioContainer && echoAudioPlayer) {
        startRecordingBtn.addEventListener('click', async () => {
            if (!navigator.mediaDevices?.getUserMedia) {
                alert('Your browser does not support audio recording or you may need to allow microphone access.');
                return;
            }

            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);

                mediaRecorder.onstart = () => {
                    audioChunks = [];
                    recordingStatus.style.display = 'block';
                    recordingStatus.textContent = 'Recording...';
                    startRecordingBtn.disabled = true;
                    stopRecordingBtn.disabled = false;
                    echoAudioContainer.style.display = 'none';
                    echoAudioPlayer.src = '';
                };

                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        audioChunks.push(event.data);
                    }
                };

                mediaRecorder.onstop = async () => {
                    recordingStatus.textContent = 'Processing recording...';
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });

                    try {
                        await processEcho(audioBlob);
                    } catch (error) {
                        console.error('Echo processing error:', error);
                        recordingStatus.textContent = `Error: ${error.message}`;
                    } finally {
                        stream.getTracks().forEach(track => track.stop());
                    }
                };

                mediaRecorder.start(100);
            } catch (error) {
                console.error('Microphone access error:', error);
                recordingStatus.textContent = `Error: ${error.message}`;
                recordingStatus.style.display = 'block';
            }
        });

        stopRecordingBtn.addEventListener('click', () => {
            if (mediaRecorder?.state === 'recording') {
                mediaRecorder.stop();
            }
        });
    }

    // Echo Bot functionality
    async function processEcho(audioBlob) {
        const recordingStatus = document.getElementById('recordingStatus');
        const transcriptionDisplay = document.getElementById('transcriptionDisplay');
        const echoAudioContainer = document.getElementById('echoAudioContainer');
        const echoAudioPlayer = document.getElementById('echoAudioPlayer');

        recordingStatus.textContent = 'Processing recording...';
        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        try {
            const response = await fetch('/tts/echo', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Echo processing failed with status ${response.status}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.detail || 'Unknown error occurred');
            }

            transcriptionDisplay.innerHTML = `
                <div class="transcription-result">
                    <h3>You said:</h3>
                    <p>"${data.transcription}"</p>
                    ${data.confidence ? `<small>Confidence: ${(data.confidence * 100).toFixed(1)}%</small>` : ''}
                </div>
            `;
            transcriptionDisplay.style.display = 'block';

            echoAudioPlayer.src = data.audio_url;
            echoAudioContainer.style.display = 'block';

            recordingStatus.textContent = 'Echo response ready!';
        } catch (error) {
            console.error('Echo processing error', error);
            recordingStatus.textContent = `Error: ${error.message}`;
        }
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

    if (startLLMRecordingBtn && stopLLMRecordingBtn) {
        startLLMRecordingBtn.addEventListener('click', async () => {
            if (!navigator.mediaDevices?.getUserMedia) {
                alert('Your browser does not support audio recording or you may need to allow microphone access.');
                return;
            }

            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                llmMediaRecorder = new MediaRecorder(stream);

                llmMediaRecorder.onstart = () => {
                    llmAudioChunks = [];
                    llmRecordingStatus.style.display = 'block';
                    llmRecordingStatus.textContent = 'Recording...';
                    startLLMRecordingBtn.disabled = true;
                    stopLLMRecordingBtn.disabled = false;
                    llmAudioContainer.style.display = 'none';
                    llmAudioPlayer.src = '';
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
                    } finally {
                        stream.getTracks().forEach(track => track.stop());
                    }
                };

                llmMediaRecorder.start(100);
            } catch (error) {
                console.error('Microphone access error:', error);
                llmRecordingStatus.textContent = `Error: ${error.message}`;
                llmRecordingStatus.style.display = 'block';
            }
        });

        stopLLMRecordingBtn.addEventListener('click', () => {
            if (llmMediaRecorder?.state === 'recording') {
                llmMediaRecorder.stop();
            }
        });
    }

    // Voice to LLM Assistant functionality
    async function processLLMQuery(audioBlob) {
        llmRecordingStatus.textContent = 'Processing with AI...';
        llmRecordingStatus.style.display = 'block';

        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        try {
            const response = await fetch('/llm/query-audio', {
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
            llmTranscriptionText.textContent = data.transcription;
            llmTranscriptionDisplay.style.display = 'block';

            // Display response
            llmResponseText.textContent = data.llm_response;

            // Set up audio player
            llmAudioPlayer.src = data.audio_url;
            llmAudioContainer.style.display = 'block';

            llmRecordingStatus.textContent = 'AI response ready! Click Play to hear the answer.';

            // Auto-play the audio
            llmAudioPlayer.play().catch(error => {
                console.log('Auto-play prevented:', error);
                llmRecordingStatus.textContent = 'AI response ready (click play to listen)';
            });

            return data;

        } catch (error) {
            console.error('LLM processing error:', error);
            llmRecordingStatus.textContent = `Processing failed: ${error.message}`;
            throw error;
        }
    }
});
