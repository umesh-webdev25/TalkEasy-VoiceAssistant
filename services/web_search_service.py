import logging
from typing import List, Dict, Optional
import os
import asyncio
from datetime import datetime, timedelta
from tavily import TavilyClient

logger = logging.getLogger(__name__)


class WebSearchService:
    """Service for performing web searches using Tavily API"""
    
    def __init__(self, max_results: int = 5, timeout: int = 10):
        self.max_results = max_results
        self.timeout = timeout
        self.search_cache = {}
        self.cache_duration = timedelta(minutes=5)
        self.tavily_client = None
        self._initialize_tavily_client()
        logger.info("🔍 Web Search Service initialized")
    
    def _initialize_tavily_client(self):
        """Initialize Tavily client with API key from environment"""
        api_key = os.getenv("TAVILY_API_KEY")
        if api_key and api_key != "your_tavily_api_key_here":
            try:
                self.tavily_client = TavilyClient(api_key=api_key)
                logger.info("✅ Tavily API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {str(e)}")
                self.tavily_client = None
        else:
            logger.warning("⚠️ TAVILY_API_KEY not found in environment variables")
            self.tavily_client = None
    
    def is_configured(self) -> bool:
        """Check if Tavily API is properly configured"""
        return self.tavily_client is not None
    
    async def search_web(self, query: str, use_cache: bool = True, max_results: int = None) -> List[Dict]:
        """
        Perform a web search using Tavily API and return formatted results
        
        Args:
            query: Search query string
            use_cache: Whether to use cached results if available
            max_results: Maximum number of results to return (overrides instance default)
            
        Returns:
            List of search results with title, url, and snippet
        """
        try:
            # Check if Tavily is configured
            if not self.is_configured():
                logger.error("Tavily API is not configured. Please set TAVILY_API_KEY environment variable.")
                return []
            
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
            
            # Use Tavily API for search
            results = []
            try:
                # Perform search using Tavily
                search_response = self.tavily_client.search(
                    query=query,
                    max_results=max_results or self.max_results,
                    search_depth="basic"
                )
                
                # Process results
                for result in search_response.get("results", []):
                    formatted_result = {
                        'title': result.get("title", "No title"),
                        'url': result.get("url", ""),
                        'snippet': result.get("content", "No description available"),
                        'source': 'Tavily'
                    }
                    results.append(formatted_result)
                
            except Exception as tavily_error:
                logger.error(f"Tavily search failed: {tavily_error}")
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
