// FastAPI Voice Agents App with Text-to-Speech functionality

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
});
