import logging
from typing import List, Dict, Optional
import requests
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class WebSearchService:
    """Service for performing web searches and retrieving information"""
    
    def __init__(self, max_results: int = 5, timeout: int = 10):
        self.max_results = max_results
        self.timeout = timeout
        self.search_cache = {}
        self.cache_duration = timedelta(minutes=5)
        logger.info("🔍 Web Search Service initialized")
    
    async def search_web(self, query: str, use_cache: bool = True) -> List[Dict]:
        """
        Perform a web search and return formatted results
        
        Args:
            query: Search query string
            use_cache: Whether to use cached results if available
            
        Returns:
            List of search results with title, url, and snippet
        """
        try:
            # Check cache first
            cache_key = query.lower().strip()
            if use_cache and cache_key in self.search_cache:
                cached_result = self.search_cache[cache_key]
                if datetime.now() - cached_result['timestamp'] < self.cache_duration:
                    logger.info(f"Using cached search results for: {query}")
                    return cached_result['results']
                else:
                    # Remove expired cache entry
                    del self.search_cache[cache_key]
            
            logger.info(f"Searching web for: {query}")
            
            # Try DuckDuckGo search first
            results = []
            try:
                # Try to import ddgs (new package name)
                try:
                    from ddgs import DDGS
                    # Use sync version since async might not be available
                    with DDGS() as ddgs:
                        search_results = []
                        for result in ddgs.text(query, max_results=self.max_results):
                            search_results.append(result)
                        
                        for result in search_results:
                            formatted_result = {
                                'title': result.get('title', 'No title'),
                                'url': result.get('href', ''),
                                'snippet': result.get('body', 'No description available'),
                                'source': 'DuckDuckGo'
                            }
                            results.append(formatted_result)
                            
                except ImportError:
                    # Fallback to old package name
                    from duckduckgo_search import DDGS
                    with DDGS() as ddgs:
                        search_results = []
                        for result in ddgs.text(query, max_results=self.max_results):
                            search_results.append(result)
                        
                        for result in search_results:
                            formatted_result = {
                                'title': result.get('title', 'No title'),
                                'url': result.get('href', ''),
                                'snippet': result.get('body', 'No description available'),
                                'source': 'DuckDuckGo'
                            }
                            results.append(formatted_result)
                            
            except Exception as ddgs_error:
                logger.warning(f"DuckDuckGo search failed: {ddgs_error}. Falling back to alternative method.")
                # Fallback: try a simple requests-based approach
                try:
                    fallback_results = await self._fallback_search(query)
                    results.extend(fallback_results)
                except Exception as fallback_error:
                    logger.error(f"Fallback search also failed: {fallback_error}")
                    # Return empty results instead of raising exception to avoid breaking the flow
                    return []
            
            # Cache the results
            if results and use_cache:
                self.search_cache[cache_key] = {
                    'results': results,
                    'timestamp': datetime.now()
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Web search error for query '{query}': {str(e)}")
            # Return empty results instead of raising exception
            return []
    
    async def _fallback_search(self, query: str) -> List[Dict]:
        """Fallback search method using requests"""
        try:
            # Simple fallback using a different approach if DuckDuckGo fails
            # This is a placeholder - in production, you might use a different API
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # You could integrate with another search API here if needed
            # For now, return empty results to avoid breaking the flow
            return []
            
        except Exception as e:
            logger.error(f"Fallback search error: {e}")
            return []
    
    def format_search_results(self, results: List[Dict], query: str) -> str:
        """Format search results into a readable string for the LLM"""
        if not results:
            return f"I couldn't find any recent information about '{query}'. The search didn't return any results."
        
        formatted = f"Here are the most relevant search results for '{query}':\n\n"
        
        for i, result in enumerate(results[:self.max_results], 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   URL: {result['url']}\n"
            formatted += f"   Summary: {result['snippet'][:200]}...\n\n"
        
        formatted += "Please use this information to provide a comprehensive answer to the user's question."
        return formatted
    
    async def get_current_weather(self, location: str) -> Optional[Dict]:
        """Get current weather for a location (placeholder for future weather skill)"""
        # This is a placeholder method that can be implemented later
        # with a weather API like OpenWeatherMap
        logger.info(f"Weather request for: {location}")
        return None
    
    async def get_news_headlines(self, category: str = "general") -> Optional[List[Dict]]:
        """Get news headlines (placeholder for future news skill)"""
        # This is a placeholder method that can be implemented later
        # with a news API like NewsAPI
        logger.info(f"News request for category: {category}")
        return None
    
    def clear_cache(self):
        """Clear the search cache"""
        self.search_cache.clear()
        logger.info("Search cache cleared")


# Singleton instance for easy access
web_search_service = WebSearchService()
