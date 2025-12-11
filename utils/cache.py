"""
Wikipedia page caching system.

Provides disk-based caching for Wikipedia pages to reduce API calls
and improve performance during development and re-runs.
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict

from utils.logger import setup_logger

logger = setup_logger(__name__)


class WikipediaCache:
    """
    Disk-based cache for Wikipedia pages.
    
    Caches page content by concept name using JSON files.
    Never expires - manual clearing only via clear() method.
    """
    
    def __init__(self, cache_dir: str = ".cache/wikipedia"):
        """
        Initialise cache.
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Wikipedia cache initialized at {self.cache_dir}")
    
    def _get_cache_path(self, concept: str) -> Path:
        """
        Get cache file path for concept.
        
        Uses MD5 hash of concept name to avoid filesystem issues
        with special characters.
        
        Args:
            concept: Wikipedia concept/page name
            
        Returns:
            Path to cache file
        """
        # hash concept name for safe filename
        concept_hash = hashlib.md5(concept.encode()).hexdigest()
        return self.cache_dir / f"{concept_hash}.json"
    
    def get(self, concept: str) -> Optional[str]:
        """
        Get cached page content for concept.
        
        Args:
            concept: Wikipedia concept/page name
            
        Returns:
            Cached page content if exists, None otherwise
        """
        cache_path = self._get_cache_path(concept)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.debug(f"Cache hit for concept: {concept}")
                return data["content"]
        except Exception as e:
            logger.warning(f"Error reading cache for '{concept}': {e}")
            return None
    
    def set(self, concept: str, content: str, page_id: str) -> None:
        """
        Cache page content for concept.
        
        Args:
            concept: Wikipedia concept/page name
            content: Page content to cache
            page_id: Wikipedia page ID
        """
        cache_path = self._get_cache_path(concept)
        
        try:
            data = {
                "concept": concept,
                "page_id": page_id,
                "content": content
            }
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Cached concept: {concept}")
        except Exception as e:
            logger.warning(f"Error caching '{concept}': {e}")
    
    def clear(self) -> int:
        """
        Clear all cached pages.
        
        Returns:
            Number of cache files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                logger.warning(f"Error deleting cache file {cache_file}: {e}")
        
        logger.info(f"Cleared {count} cached Wikipedia pages")
        return count
    
    def stats(self) -> Dict[str, float]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache stats (total_pages, total_size_mb)
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "total_pages": len(cache_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
