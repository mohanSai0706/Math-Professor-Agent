import logging
from typing import List, Dict, Any, Optional
from tavily import TavilyClient
from app.core.config import settings
from app.models.schemas import WebSearchResult

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        self.client = TavilyClient(api_key=settings.tavily_api_key)
    
    async def search_mathematics(self, question: str, max_results: int = 3) -> WebSearchResult:
        """Search the web for mathematical solutions using Tavily."""
        try:
            # Enhance query for better mathematical results
            enhanced_query = f"mathematics solve step by step: {question}"
            
            # Search using Tavily
            response = self.client.search(
                query=enhanced_query,
                search_depth="advanced",
                max_results=max_results,
                include_domains=["khanacademy.org", "mathway.com", "wolframalpha.com", 
                              "stackoverflow.com", "math.stackexchange.com"],
                exclude_domains=["pinterest.com", "instagram.com"]
            )
            
            if response and "results" in response and response["results"]:
                # Combine results into comprehensive content
                combined_content = self._combine_search_results(response["results"])
                sources = [result.get("url", "") for result in response["results"]]
                
                return WebSearchResult(
                    found=True,
                    content=combined_content,
                    sources=sources,
                    search_query=enhanced_query
                )
            else:
                return WebSearchResult(
                    found=False,
                    content=None,
                    sources=[],
                    search_query=enhanced_query
                )
                
        except Exception as e:
            logger.error(f"Error in web search: {str(e)}")
            return WebSearchResult(
                found=False,
                content=None,
                sources=[],
                search_query=question
            )
    
    def _combine_search_results(self, results: List[Dict]) -> str:
        """Combine multiple search results into coherent content."""
        combined_content = []
        
        for i, result in enumerate(results, 1):
            title = result.get("title", f"Source {i}")
            content = result.get("content", "")
            
            if content:
                section = f"Source {i} - {title}:\n{content}\n"
                combined_content.append(section)
        
        return "\n".join(combined_content)