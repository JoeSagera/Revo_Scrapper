"""Ultra-potent Cloudflare bypass using curl-cffi and cf-clearance."""
try:
    from curl_cffi import requests as curl_requests
except ImportError:
    curl_requests = None

import requests
from bs4 import BeautifulSoup
import re
import time
import random
from logger import get_logger
import config

logger = get_logger(__name__)


class UltraPotentScraper:
    """Scraper using curl-cffi which is nearly impossible to block."""
    
    def __init__(self):
        self.base_url = config.REVOLICO_SEARCH_URL
        
    def scrape(self, query: str, max_pages: int = 1) -> list[dict]:
        """
        Scrape Revolico listings using curl-cffi (ultimate Cloudflare bypass).
        
        Args:
            query: Search query
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of listing dictionaries
        """
        logger.info(f"Starting ultra-potent scrape for: {query} ({max_pages} pages)")
        
        if not curl_requests:
            logger.warning("curl-cffi not available, falling back to requests")
            return self._scrape_with_requests(query, max_pages)
        
        results = []
        
        for page_num in range(1, max_pages + 1):
            logger.info(f"Scraping page {page_num} with curl-cffi")
            try:
                page_results = self._scrape_page_curl(query, page_num)
                results.extend(page_results)
                
                if page_num < max_pages:
                    delay = random.uniform(1, 3)
                    logger.debug(f"Waiting {delay:.1f}s...")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"curl-cffi failed on page {page_num}: {e}")
                logger.info("Falling back to cloudscraper...")
                try:
                    import cloudscraper
                    scraper = cloudscraper.create_scraper()
                    page_results = self._scrape_page_cloudscraper(scraper, query, page_num)
                    results.extend(page_results)
                except Exception as e2:
                    logger.error(f"Cloudscraper also failed: {e2}")
                    if page_num == 1:
                        raise
                    continue
        
        logger.info(f"Found {len(results)} listings total")
        return results
    
    def _scrape_page_curl(self, query: str, page_num: int) -> list[dict]:
        """Scrape using curl-cffi."""
        url = f"{self.base_url}?q={query}"
        if page_num > 1:
            url += f"&page={page_num}"
        
        logger.debug(f"Fetching {url}")
        
        try:
            # curl-cffi with browser simulation
            response = curl_requests.get(
                url,
                impersonate="chrome120",  # Impersonate Chrome 120
                timeout=15,
                headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            logger.debug(f"Response status: {response.status_code}")
            
            if response.status_code not in [200, 403]:
                logger.warning(f"Unexpected status: {response.status_code}")
                return []
            
            return self._extract_listings(response.text)
            
        except Exception as e:
            logger.error(f"curl-cffi request failed: {e}")
            raise
    
    def _scrape_page_cloudscraper(self, scraper, query: str, page_num: int) -> list[dict]:
        """Scrape using cloudscraper as fallback."""
        url = f"{self.base_url}?q={query}"
        if page_num > 1:
            url += f"&page={page_num}"
        
        response = scraper.get(url, timeout=15)
        
        if response.status_code != 200:
            logger.warning(f"Cloudscraper status: {response.status_code}")
            return []
        
        return self._extract_listings(response.text)
    
    def _scrape_with_requests(self, query: str, max_pages: int) -> list[dict]:
        """Fallback to regular requests with good headers."""
        logger.info("Using standard requests with enhanced headers")
        
        results = []
        
        for page_num in range(1, max_pages + 1):
            url = f"{self.base_url}?q={query}"
            if page_num > 1:
                url += f"&page={page_num}"
            
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                }
                
                response = requests.get(url, headers=headers, timeout=15)
                results.extend(self._extract_listings(response.text))
                
                if page_num < max_pages:
                    time.sleep(random.uniform(1, 2))
                    
            except Exception as e:
                logger.error(f"Request page {page_num} failed: {e}")
                if page_num == 1:
                    raise
                continue
        
        return results
    
    def _extract_listings(self, html: str) -> list[dict]:
        """Extract listings from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find listings
        listings = self._find_listings_in_soup(soup)
        logger.debug(f"Found {len(listings)} listing elements")
        
        results = []
        for listing in listings:
            try:
                item = self._parse_listing(listing)
                if item and item.get('titulo') and item.get('precio_raw'):
                    results.append(item)
            except Exception as e:
                logger.debug(f"Parse error: {e}")
                continue
        
        return results
    
    def _find_listings_in_soup(self, soup):
        """Find listing elements."""
        selectors = [
            'a[href*="/anuncio/"]',
            'article',
            'div.listing',
            'div[class*="ListingCard"]',
            'div[class*="card"]',
            'div[class*="item"]',
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if len(elements) > 3:
                logger.debug(f"Found listings with: {selector}")
                return elements
        
        return []
    
    def _parse_listing(self, element):
        """Parse single listing."""
        titulo = ""
        if element.get('title'):
            titulo = element.get('title')
        if not titulo:
            text = element.get_text(strip=True)
            if text:
                titulo = text.split('\n')[0][:100]
        
        precio_raw = ""
        full_text = element.get_text()
        match = re.search(r'([\d,\.]+\s*(USD|CUP|MLC|pesos))', full_text, re.IGNORECASE)
        if match:
            precio_raw = match.group(1)
        
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


def scrape_revolico_ultimate(query: str, max_pages: int = 1) -> list[dict]:
    """Ultimate Cloudflare bypass scraper."""
    scraper = UltraPotentScraper()
    return scraper.scrape(query, max_pages)


if __name__ == "__main__":
    try:
        results = scrape_revolico_ultimate("car", max_pages=1)
        print(f"\nFound {len(results)} listings\n")
        for r in results[:5]:
            print(f"  {r['titulo'][:60]}")
    except Exception as e:
        print(f"Error: {e}")
