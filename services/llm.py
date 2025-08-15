import google.generativeai as genai
from fastapi import HTTPException
import os

def get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Gemini API key not set.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def query_gemini(text, max_tokens=1000, temperature=0.7):
    model = get_gemini_model()
    generation_config = genai.types.GenerationConfig(
        max_output_tokens=max_tokens,
        temperature=temperature
    )
    response = model.generate_content(text, generation_config=generation_config)
    if not response.text:
        raise HTTPException(status_code=500, detail="No response generated from Gemini API")
    return response
