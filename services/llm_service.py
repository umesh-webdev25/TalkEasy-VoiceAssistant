import google.generativeai as genai
from typing import List, Dict, Optional, AsyncGenerator, Union
import logging
from services.web_search_service import web_search_service

logger = logging.getLogger(__name__)


class LLMService:    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash", persona: str = None):
        self.api_key = api_key
        self.model_name = model_name
        self.persona = persona or "helpful AI assistant"
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"🤖 LLM Service initialized with model: {model_name}, persona: {self.persona}")
    
    def format_chat_history_for_llm(self, messages: List[Dict]) -> str:
        if not messages:
            return ""
        
        formatted_history = "\n\nPrevious conversation context:\n"
        for msg in messages[-10:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted_history += f"{role}: {msg['content']}\n"
        
        return formatted_history
    
    def _should_perform_web_search(self, user_message: str) -> bool:
        """Determine if a web search should be performed based on the user message"""
        search_triggers = [
            'search for', 'find information about', 'look up', 
            'what is', 'who is', 'when is', 'where is', 'how to',
            'latest news about', 'current weather in', 'recent developments in',
            'tell me about', 'information on', 'details about'
        ]
        
        user_message_lower = user_message.lower()
        
        # Check for explicit search commands
        if any(trigger in user_message_lower for trigger in ['search for', 'find information about', 'look up']):
            return True
        
        # Check for information-seeking questions that would benefit from current data
        if any(user_message_lower.startswith(trigger) for trigger in ['what is', 'who is', 'when is', 'where is']):
            return True
        
        # Check for topics that require current information
        current_info_topics = ['news', 'weather', 'stock', 'price', 'recent', 'latest', 'current', 'today', 'now']
        if any(topic in user_message_lower for topic in current_info_topics):
            return True
        
        return False
    
    def _extract_search_query(self, user_message: str) -> str:
        """Extract the search query from the user message"""
        user_message_lower = user_message.lower()
        
        # Remove common search phrases to get the actual query
        search_phrases = [
            'search for', 'find information about', 'look up', 
            'what is', 'who is', 'when is', 'where is', 'how to',
            'tell me about', 'information on', 'details about'
        ]
        
        for phrase in search_phrases:
            if phrase in user_message_lower:
                return user_message_lower.split(phrase, 1)[1].strip()
        
        # If no specific phrase found, use the entire message as query
        return user_message.strip()
    
    async def generate_response(self, user_message: str, chat_history: List[Dict]) -> str:
        try:
            # Check if web search is needed
            if self._should_perform_web_search(user_message):
                query = self._extract_search_query(user_message)
                logger.info(f"🔍 Performing web search for query: {query}")
                
                try:
                    search_results = await web_search_service.search_web(query)
                    formatted_results = web_search_service.format_search_results(search_results, query)
                    
                    # Combine search results with LLM processing for better response
                    history_context = self.format_chat_history_for_llm(chat_history)
                    
                    enhanced_prompt = f"""You are {self.persona}. Based on the following search results, provide a comprehensive answer to the user's question.

SEARCH RESULTS FOR "{query}":
{formatted_results}

USER'S ORIGINAL QUESTION: "{user_message}"

{history_context}

Please provide a helpful, accurate answer based on the search results. Summarize the key information and cite relevant sources if appropriate."""
                    
                    llm_response = self.model.generate_content(enhanced_prompt)
                    
                    if llm_response.candidates:
                        response_text = ""
                        for part in llm_response.candidates[0].content.parts:
                            if hasattr(part, 'text'):
                                response_text += part.text
                        
                        if response_text.strip():
                            return response_text.strip()
                    
                    # Fallback to just returning formatted search results if LLM fails
                    return formatted_results
                    
                except Exception as search_error:
                    logger.error(f"Web search failed: {search_error}")
                    # Continue with normal LLM response if search fails
            
            # Normal LLM response for non-search queries
            history_context = self.format_chat_history_for_llm(chat_history)
            
            llm_prompt = f"""You are {self.persona}. Please respond directly to the user's current question.

IMPORTANT: Always answer the CURRENT user question directly. Do not give generic responses about your capabilities unless specifically asked "what can you do".

User's current question: "{user_message}"

{history_context}

Please provide a specific, helpful answer to the user's current question. Keep your response under 3000 characters."""
            
            llm_response = self.model.generate_content(llm_prompt)
            
            if not llm_response.candidates:
                raise Exception("No response candidates generated from LLM")
            
            response_text = ""
            for part in llm_response.candidates[0].content.parts:
                if hasattr(part, 'text'):
                    response_text += part.text
            
            if not response_text.strip():
                raise Exception("Empty response text from LLM")
            
            response_text = response_text.strip()
            return response_text
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"LLM response generation error: {error_msg}")
            
            # Check for specific error types
            if "quota" in error_msg.lower() or "429" in error_msg:
                raise Exception("API quota exceeded. Please check your billing and rate limits.")
            elif "403" in error_msg or "unauthorized" in error_msg.lower():
                raise Exception("API authentication failed. Please check your API key.")
            elif "404" in error_msg or "not found" in error_msg.lower():
                raise Exception("Model not found. Please check the model name.")
            else:
                raise

    async def generate_streaming_response(self, user_message: str, chat_history: List[Dict]) -> AsyncGenerator[str, None]:
        """Generate a streaming response from the LLM"""
        try:
            history_context = self.format_chat_history_for_llm(chat_history)
            
            llm_prompt = f"""You are {self.persona}. Please respond directly to the user's current question.

IMPORTANT: Always answer the CURRENT user question directly. Do not give generic responses about your capabilities unless specifically asked "what can you do".

User's current question: "{user_message}"

{history_context}

Please provide a specific, helpful answer to the user's current question. Keep your response under 3000 characters."""
            
            # Use stream_generate_content for streaming response
            response_stream = self.model.generate_content(llm_prompt, stream=True)
            
            accumulated_response = ""
            for chunk in response_stream:
                if chunk.candidates and len(chunk.candidates) > 0:
                    candidate = chunk.candidates[0]
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                accumulated_response += part.text
                                yield part.text
            
            if not accumulated_response.strip():
                raise Exception("Empty response text from LLM")
            
            logger.info(f"LLM streaming response completed: {len(accumulated_response)} characters")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"LLM streaming response generation error for '{user_message[:50]}...': {error_msg}")
            
            # Check for specific error types
            if "quota" in error_msg.lower() or "429" in error_msg:
                logger.error("❌ API quota exceeded or rate limited")
                raise Exception("API quota exceeded. Please check your billing and rate limits.")
            elif "403" in error_msg or "unauthorized" in error_msg.lower():
                logger.error("❌ API authentication failed")
                raise Exception("API authentication failed. Please check your API key.")
            elif "404" in error_msg or "model" in error_msg.lower():
                logger.error("❌ Model issue")
                raise Exception("Model issue. Please check the model name or availability.")
            else:
                raise