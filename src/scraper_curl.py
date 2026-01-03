"""Scraper using curl executable directly - ultimate bypass."""
import subprocess
import json
import re
from bs4 import BeautifulSoup
import time
import random
from logger import get_logger
import config

logger = get_logger(__name__)


class CurlDirectScraper:
    """Scraper using curl executable directly (not Python libs - can't be blocked)."""
    
    def __init__(self):
        self.base_url = config.REVOLICO_SEARCH_URL
        
    def scrape(self, query: str, max_pages: int = 1) -> list[dict]:
        """
        Scrape using native curl executable.
        
        Args:
            query: Search query
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of listings
        """
        logger.info(f"Starting curl-direct scrape for: {query} ({max_pages} pages)")
        
        results = []
        
        for page_num in range(1, max_pages + 1):
            logger.info(f"Scraping page {page_num}")
            try:
                page_results = self._scrape_page_curl(query, page_num)
                results.extend(page_results)
                
                if page_num < max_pages:
                    delay = random.uniform(1, 2)
                    logger.debug(f"Waiting {delay:.1f}s...")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error on page {page_num}: {e}")
                if page_num == 1:
                    raise
                continue
        
        logger.info(f"Found {len(results)} listings")
        return results
    
    def _scrape_page_curl(self, query: str, page_num: int) -> list[dict]:
        """Use curl executable directly."""
        url = f"{self.base_url}?q={query}"
        if page_num > 1:
            url += f"&page={page_num}"
        
        logger.debug(f"Fetching with curl: {url}")
        
        try:
            # Use curl executable directly with all anti-block headers
            cmd = [
                "curl.exe",
                "-L",  # Follow redirects
                "-s",  # Silent mode
                "--compressed",  # Automatic decompression
                "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "-H", "Accept-Language: en-US,en;q=0.5",
                "-H", "Accept-Encoding: gzip, deflate",
                "-H", "DNT: 1",
                "-H", "Connection: keep-alive",
                "-H", "Upgrade-Insecure-Requests: 1",
                "--max-time", "15",
                url
            ]
            
            # Execute curl with UTF-8 encoding
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=20,
                encoding='utf-8',
                errors='ignore'  # Ignore encoding errors
            )
            
            if result.returncode != 0:
                logger.error(f"curl error: {result.stderr}")
                raise Exception(f"curl failed with code {result.returncode}")
            
            html = result.stdout
            
            if not html or len(html) < 1000:
                logger.warning("Got empty or very small response")
                return []
            
            logger.debug(f"Got {len(html)} bytes of HTML")
            
            # Parse with BeautifulSoup
            return self._extract_listings(html)
            
        except subprocess.TimeoutExpired:
            logger.error("curl timeout")
            raise
        except Exception as e:
            logger.error(f"curl execution failed: {e}")
            raise
    
    def _extract_listings(self, html: str) -> list[dict]:
        """Extract listings from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find listing links
        listings = soup.find_all('a', href=re.compile(r'/anuncio/|/es/anuncio/'))
        logger.debug(f"Found {len(listings)} listing links")
        
        if len(listings) == 0:
            # Try other selectors
            listings = soup.find_all(['article', 'div'], class_=re.compile(r'card|listing|item', re.I))
            logger.debug(f"Fallback selectors found {len(listings)} elements")
        
        results = []
        for listing in listings[:50]:  # Limit to first 50
            try:
                item = self._parse_listing(listing)
                if item and item.get('titulo') and item.get('precio_raw'):
                    results.append(item)
            except Exception as e:
                logger.debug(f"Parse error: {e}")
                continue
        
        logger.info(f"Extracted {len(results)} valid listings")
        return results
    
    def _parse_listing(self, element):
        """Parse listing element."""
        # Get title
        titulo = ""
        if element.get('title'):
            titulo = element.get('title')
        if not titulo:
            text = element.get_text(strip=True)
            if text:
                titulo = text.split('\n')[0][:100]
        
        # Get price
        precio_raw = ""
        full_text = element.get_text()
        match = re.search(r'([\d,\.]+\s*(USD|CUP|MLC|pesos|€))', full_text, re.IGNORECASE)
        if match:
            precio_raw = match.group(1)
        
        # Get URL
        url = ""
        if element.name == 'a':
            url = element.get('href', '')
        else:
            link = element.find('a', href=True)
            if link:
                url = link.get('href', '')
        
        if url and not url.startswith('http'):
            url = 'https://revolico.com' + (url if url.startswith('/') else '/' + url)
        
        if titulo and precio_raw:
            return {
                'titulo': titulo,
                'precio_raw': precio_raw,
                'url': url,
                'fuente': 'revolico'
            }
        
        return None


def scrape_revolico_curl(query: str, max_pages: int = 1) -> list[dict]:
    """Curl-direct scraper."""
    scraper = CurlDirectScraper()
    return scraper.scrape(query, max_pages)


if __name__ == "__main__":
    try:
        results = scrape_revolico_curl("car", max_pages=1)
        print(f"Found {len(results)} listings")
        for r in results[:5]:
            print(f"  - {r['titulo'][:60]}")
    except Exception as e:
        print(f"Error: {e}")
