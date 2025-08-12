"""
Error handling utilities for 30 Days of Voice Agents
Provides centralized error handling and fallback responses
"""

import logging
import time
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import os
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIErrorHandler:
    """Centralized error handling for API endpoints"""
    
    @staticmethod
    def create_fallback_audio(text: str = "I'm having trouble connecting right now") -> Dict[str, str]:
        """Create a fallback audio response when APIs fail"""
        return {
            "audio_url": None,
            "fallback_text": text,
            "error": True,
            "message": "Service temporarily unavailable"
        }
    
    @staticmethod
    def handle_api_error(error: Exception, service: str) -> Dict[str, Any]:
        """Handle API errors with appropriate messages and codes"""
        error_message = str(error).lower()
        
        if "api key" in error_message or "authentication" in error_message:
            return {
                "error": True,
                "code": "AUTH_ERROR",
                "message": f"Authentication failed for {service}. Please check your API key.",
                "details": str(error)
            }
        elif "quota" in error_message or "limit" in error_message:
            return {
                "error": True,
                "code": "QUOTA_EXCEEDED",
                "message": f"API quota exceeded for {service}. Please try again later.",
                "details": str(error)
            }
        elif "network" in error_message or "connection" in error_message:
            return {
                "error": True,
                "code": "NETWORK_ERROR",
                "message": f"Network error connecting to {service}. Please check your internet connection.",
                "details": str(error)
            }
        elif "timeout" in error_message:
            return {
                "error": True,
                "code": "TIMEOUT_ERROR",
                "message": f"Request to {service} timed out. Please try again.",
                "details": str(error)
            }
        else:
            return {
                "error": True,
                "code": "GENERAL_ERROR",
                "message": f"Error processing request with {service}. Please try again.",
                "details": str(error)
            }

class RetryHandler:
    """Handle retry logic for failed API calls"""
    
    @staticmethod
    def exponential_backoff(attempt: int, base_delay: float = 1.0) -> float:
        """Calculate exponential backoff delay"""
        return base_delay * (2 ** attempt)
    
    @staticmethod
    def should_retry(attempt: int, max_retries: int = 3) -> bool:
        """Determine if we should retry based on attempt count"""
        return attempt < max_retries

class ErrorSimulator:
    """Simulate various error conditions for testing"""
    
    @staticmethod
    def simulate_stt_error():
        """Simulate Speech-to-Text API failure"""
        raise Exception("AssemblyAI STT service unavailable")
    
    @staticmethod
    def simulate_llm_error():
        """Simulate LLM API failure"""
        raise Exception("Gemini API authentication failed")
    
    @staticmethod
    def simulate_tts_error():
        """Simulate TTS API failure"""
        raise Exception("Murf TTS quota exceeded")
    
    @staticmethod
    def simulate_network_error():
        """Simulate network connectivity issues"""
        raise Exception("Network connection timeout")

# Global error handler
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "details": str(exc) if os.getenv("DEBUG", "").lower() == "true" else None
        }
    )

# Error response templates
ERROR_RESPONSES = {
    "STT_ERROR": {
        "audio_url": None,
        "fallback_text": "I'm having trouble understanding your speech right now",
        "error": True,
        "message": "Speech recognition service unavailable"
    },
    "LLM_ERROR": {
        "audio_url": None,
        "fallback_text": "I'm having trouble processing your request right now",
        "error": True,
        "message": "AI processing service unavailable"
    },
    "TTS_ERROR": {
        "audio_url": None,
        "fallback_text": "I'm having trouble generating audio right now",
        "error": True,
        "message": "Text-to-speech service unavailable"
    },
    "GENERAL_ERROR": {
        "audio_url": None,
        "fallback_text": "I'm having trouble connecting right now",
        "error": True,
        "message": "Service temporarily unavailable"
    }
}
