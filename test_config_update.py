import requests

# Sample configuration data
config_data = {
    "persona": "Test Persona",
    "gemini_api_key": "test_gemini_key",
    "assemblyai_api_key": "test_assemblyai_key",
    "murf_api_key": "test_murf_key",
    "murf_voice_id": "en-IN-aarav",
    "mongodb_url": "mongodb://localhost:27017"
}

# Send a POST request to update the configuration
response = requests.post("http://127.0.0.1:8000/api/config", json=config_data)

# Print the response
print(response.json())
