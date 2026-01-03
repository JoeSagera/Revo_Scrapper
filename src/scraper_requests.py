"""Scraper using requests with proper gzip handling."""
import requests
from bs4 import BeautifulSoup
import gzip
import re
import time
import random
from logger import get_logger
import config

logger = get_logger(__name__)


class RequestsScraper:
    """Scraper using requests with proper encoding handling."""
    
    def __init__(self):
        self.base_url = config.REVOLICO_SEARCH_URL
        # Create session with good headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        })
        
    def scrape(self, query: str, max_pages: int = 1) -> list[dict]:
        """Scrape using requests."""
        logger.info(f"Starting requests scrape for: {query} ({max_pages} pages)")
        
        results = []
        
        for page_num in range(1, max_pages + 1):
            logger.info(f"Scraping page {page_num}")
            try:
                page_results = self._scrape_page(query, page_num)
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
    
    def _scrape_page(self, query: str, page_num: int) -> list[dict]:
        """Scrape a single page."""
        url = f"{self.base_url}?q={query}"
        if page_num > 1:
            url += f"&page={page_num}"
        
        logger.debug(f"Fetching: {url}")
        
        try:
            response = self.session.get(
                url,
                timeout=15,
                verify=True,
                allow_redirects=True
            )
            
            logger.debug(f"Status: {response.status_code}")
            
            if response.status_code != 200:
                logger.warning(f"Status: {response.status_code}")
                return []
            
            # Get HTML - requests automatically handles gzip
            html = response.text
            
            if not html or len(html) < 1000:
                logger.warning(f"Small response: {len(html)} bytes")
                return []
            
            logger.debug(f"Got {len(html)} bytes of HTML")
            
            # Extract listings
            return self._extract_listings(html)
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def _extract_listings(self, html: str) -> list[dict]:
        """Extract listings from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Check if we got Cloudflare block
        if 'Just a moment' in html or 'cf-challenge' in html:
            logger.warning("Got Cloudflare challenge page")
            return []
        
        # Find listings
        listings = []
        
        # Try direct listing links first
        links = soup.find_all('a', href=re.compile(r'/anuncio/|/es/anuncio/'))
        if len(links) > 3:
            logger.debug(f"Found {len(links)} listing links")
            listings = links
        else:
            # Try articles
            articles = soup.find_all('article')
            if len(articles) > 3:
                logger.debug(f"Found {len(articles)} article elements")
                listings = articles
            else:
                # Try divs with class
                divs = soup.find_all('div', class_=re.compile(r'card|listing|item|product', re.I))
                if len(divs) > 3:
                    logger.debug(f"Found {len(divs)} div elements")
                    listings = divs[:50]  # Limit to 50
        
        if not listings:
            logger.warning("No listing elements found")
            return []
        
        results = []
        for listing in listings:
            try:
                item = self._parse_listing(listing)
                if item and item.get('titulo') and item.get('precio_raw'):
                    results.append(item)
            except Exception as e:
                logger.debug(f"Parse error: {e}")
                continue
        
        logger.info(f"Extracted {len(results)} valid listings from {len(listings)} elements")
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
        match = re.search(r'([\d,\.]+\s*(USD|CUP|MLC|pesos))', full_text, re.IGNORECASE)
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


def scrape_revolico_requests(query: str, max_pages: int = 1) -> list[dict]:
    """Requests-based scraper."""
    scraper = RequestsScraper()
    return scraper.scrape(query, max_pages)


if __name__ == "__main__":
    try:
        results = scrape_revolico_requests("car", max_pages=1)
        print(f"Found {len(results)} listings")
        for r in results[:5]:
            print(f"  - {r['titulo'][:60]}")
    except Exception as e:
        print(f"Error: {e}")
