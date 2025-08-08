// FastAPI Voice Agents App with Text-to-Speech, Echo Bot, and Transcription functionality

document.addEventListener('DOMContentLoaded', function () {
    console.log('FastAPI Voice Agents App Loaded!');

    // Existing functionality for backend message
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
                    throw new Error('No audio URL received');
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

                    // Use the new /tts/echo endpoint for Murf voice synthesis
                    try {
                        await processMurfEcho(audioBlob);
                    } catch (error) {
                        console.error('Echo processing error:', error);
                        recordingStatus.textContent = `Error: ${error.message}`;
                    } finally {
                        // Stop all tracks to release the microphone
                        stream.getTracks().forEach(track => track.stop());
                    }
                };

                mediaRecorder.start(100); // Collect data every 100ms
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

    // Process Murf echo
    async function processMurfEcho(audioBlob) {
        const recordingStatus = document.getElementById('recordingStatus');
        const transcriptionDisplay = document.getElementById('transcriptionDisplay');
        const echoAudioPlayer = document.getElementById('echoAudioPlayer');
        const echoAudioContainer = document.getElementById('echoAudioContainer');

        if (!recordingStatus || !echoAudioPlayer || !echoAudioContainer) {
            throw new Error('Required DOM elements not found');
        }

        recordingStatus.textContent = 'Processing with Murf AI...';
        recordingStatus.style.display = 'block';

        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        try {
            const response = await fetch('/tts/echo', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Murf echo failed with status ${response.status}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.detail || 'Unknown error occurred');
            }

            // Display transcription if element exists
            if (transcriptionDisplay) {
                transcriptionDisplay.innerHTML = `
                    <div class="transcription-result">
                        <h3>You said:</h3>
                        <p>"${data.transcription}"</p>
                        ${data.confidence ? `<small>Confidence: ${(data.confidence * 100).toFixed(1)}%</small>` : ''}
                    </div>
                `;
                transcriptionDisplay.style.display = 'block';
            }

            // Set up Murf audio player
            echoAudioPlayer.src = data.audio_url;
            echoAudioContainer.style.display = 'block';

            recordingStatus.textContent = 'Murf voice generated! Click Play to hear your echo.';

            // Auto-play the Murf audio
            echoAudioPlayer.play().catch(error => {
                console.log('Auto-play prevented:', error);
                recordingStatus.textContent = 'Audio ready (click play to listen)';
            });

            return data;

        } catch (error) {
            console.error('Murf echo error:', error);
            recordingStatus.textContent = `Processing failed: ${error.message}`;
            throw error; // Re-throw for calling function to handle
        }
    }

    // Keep old functions for backward compatibility
    async function uploadAudioToServer(audioBlob) {
        const recordingStatus = document.getElementById('recordingStatus');
        if (!recordingStatus) return;

        recordingStatus.textContent = 'Uploading audio...';

        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        try {
            const response = await fetch('/upload-audio', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server responded with ${response.status}`);
            }

            const data = await response.json();
            recordingStatus.textContent = `Upload successful: ${data.filename} (${data.size} bytes)`;
            return data;
        } catch (error) {
            console.error('Upload error:', error);
            recordingStatus.textContent = `Upload failed: ${error.message}`;
            throw error;
        }
    }

    async function transcribeAudio(audioBlob) {
        const recordingStatus = document.getElementById('recordingStatus');
        const transcriptionDisplay = document.getElementById('transcriptionDisplay');

        if (!recordingStatus) return null;

        recordingStatus.textContent = 'Transcribing audio...';
        recordingStatus.style.display = 'block';

        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');

        try {
            const response = await fetch('/transcribe/file', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Transcription failed with status ${response.status}`);
            }

            const data = await response.json();

            // Display transcription if element exists
            if (transcriptionDisplay) {
                transcriptionDisplay.innerHTML = `
                    <div class="transcription-result">
                        <h3>Transcription:</h3>
                        <p>${data.transcription}</p>
                        ${data.confidence ? `<small>Confidence: ${(data.confidence * 100).toFixed(1)}%</small>` : ''}
                    </div>
                `;
                transcriptionDisplay.style.display = 'block';
            }

            recordingStatus.textContent = 'Transcription completed!';
            return data.transcription;

        } catch (error) {
            console.error('Transcription error:', error);
            recordingStatus.textContent = `Transcription failed: ${error.message}`;
            throw error;
        }
    }
});