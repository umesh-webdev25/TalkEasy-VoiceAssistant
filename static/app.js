// FastAPI Voice Agents App with Text-to-Speech and Echo Bot functionality

document.addEventListener('DOMContentLoaded', function () {
    console.log('FastAPI Voice Agents App Loaded!');

    // Existing functionality for backend message
    const getMessageBtn = document.getElementById('getMessageBtn');
    const messageDisplay = document.getElementById('messageDisplay');

    if (getMessageBtn) {
        getMessageBtn.addEventListener('click', async function () {
            getMessageBtn.textContent = 'Loading...';
            getMessageBtn.disabled = true;

            try {
                const response = await fetch('/api/backend');
                const data = await response.json();

                messageDisplay.innerHTML = `
                    <div class="success-message">
                        ${data.message}
                    </div>
                `;
            } catch (error) {
                messageDisplay.innerHTML = `
                    <div class="error-message">
                        Could not connect to backend
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

    if (ttsForm) {
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
                });

            } catch (error) {
                ttsMessage.textContent = 'Error generating audio: ' + error.message;
                console.error('Error:', error);
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

    if (startRecordingBtn && stopRecordingBtn) {
        startRecordingBtn.addEventListener('click', async () => {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                alert('Your browser does not support audio recording.');
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

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    const audioUrl = URL.createObjectURL(audioBlob);
                    echoAudioPlayer.src = audioUrl;
                    echoAudioContainer.style.display = 'block';

                    // Upload the audio file to server
                    uploadAudioToServer(audioBlob);

                    // Auto-play the recorded audio
                    echoAudioPlayer.play().catch(error => {
                        console.log('Auto-play prevented:', error);
                    });

                    startRecordingBtn.disabled = false;
                    stopRecordingBtn.disabled = true;
                };

                mediaRecorder.start();
            } catch (error) {
                console.error('Error accessing microphone:', error);
                alert('Error accessing microphone: ' + error.message);
            }
        });

        stopRecordingBtn.addEventListener('click', () => {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
                // Stop all tracks to release the microphone
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
        });
    }

    // Upload audio file to server and update status message
    async function uploadAudioToServer(audioBlob) {
        const recordingStatus = document.getElementById('recordingStatus');
        console.log('Starting uploadAudioToServer...');
        recordingStatus.textContent = 'Uploading audio...';

        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm');
        console.log('FormData prepared:', formData);

        try {
            const response = await fetch('/upload-audio', {
                method: 'POST',
                body: formData
            });
            console.log('Fetch response received:', response);

            if (!response.ok) {
                throw new Error(`Upload failed with status ${response.status}`);
            }

            const data = await response.json();
            console.log('Response JSON:', data);
            recordingStatus.textContent = `Upload successful: ${data.filename} (${data.size} bytes)`;
        } catch (error) {
            console.error('Upload error:', error);
            recordingStatus.textContent = `Upload failed: ${error.message}`;
        }
    }
});
