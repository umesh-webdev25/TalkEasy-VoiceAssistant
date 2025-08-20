import google.generativeai as genai
from typing import List, Dict, Optional, AsyncGenerator
import logging

logger = logging.getLogger(__name__)


class LLMStreamingService:    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def format_chat_history_for_llm(self, messages: List[Dict]) -> str:
        if not messages:
            return ""
        
        formatted_history = "\n\nPrevious conversation context:\n"
        for msg in messages[-10:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted_history += f"{role}: {msg['content']}\n"
        
        return formatted_history
    
    async def generate_streaming_response(self, user_message: str, chat_history: List[Dict]) -> AsyncGenerator[str, None]:
        """Generate streaming response from LLM"""
        try:
            history_context = self.format_chat_history_for_llm(chat_history)
            
            llm_prompt = f"""Please provide a helpful and well-formatted response to the following user message. 
                            Guidelines:
                            - Keep your response under 3000 characters to ensure it can be converted to speech effectively
                            - Use Markdown formatting when appropriate:
                              - Use **bold** for emphasis
                              - Use `code` for technical terms or code snippets
                              - Use bullet points (-) or numbered lists (1.) when listing items
                              - Use code blocks (```) for longer code examples
                              - Use headers (##) for sections if needed
                              - Use tables when organizing data
                            - Structure your response clearly and logically
                            - Be concise but comprehensive
                            - Consider the conversation history to provide relevant and contextual responses
                            
                            {history_context}
                            
                            Current user message: {user_message}"""
            
            # Use streaming generation
            response = self.model.generate_content(llm_prompt, stream=True)
            
            accumulated_response = ""
            for chunk in response:
                if chunk.candidates and chunk.candidates[0].content.parts:
                    for part in chunk.candidates[0].content.parts:
                        if hasattr(part, 'text'):
                            text_chunk = part.text
                            accumulated_response += text_chunk
                            yield text_chunk
            
            logger.info(f"LLM streaming response generated successfully: {len(accumulated_response)} characters")
            
        except Exception as e:
            logger.error(f"LLM streaming response generation error: {str(e)}")
            raise
