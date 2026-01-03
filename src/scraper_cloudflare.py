"""Ultra-potent Cloudflare bypass scraper using cloudscraper and curl-cffi."""
import cloudscraper
from bs4 import BeautifulSoup
import re
import time
import random
from logger import get_logger
import config

logger = get_logger(__name__)


class CloudflareBypassScraper:
    """Scraper that bypasses Cloudflare using cloudscraper library."""
    
    def __init__(self):
        self.base_url = config.REVOLICO_SEARCH_URL
        self.scraper = cloudscraper.create_scraper()
        
    def scrape(self, query: str, max_pages: int = 1) -> list[dict]:
        """
        Scrape Revolico listings bypassing Cloudflare.
        
        Args:
            query: Search query
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of listing dictionaries
        """
        logger.info(f"Starting Cloudflare-bypass scrape for: {query} ({max_pages} pages)")
        
        results = []
        
        for page_num in range(1, max_pages + 1):
            logger.info(f"Scraping page {page_num}")
            try:
                page_results = self._scrape_page(query, page_num)
                results.extend(page_results)
                
                if page_num < max_pages:
                    # Random delay between pages
                    delay = random.uniform(1, 3)
                    logger.debug(f"Waiting {delay:.1f}s before next page")
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error scraping page {page_num}: {e}")
                if page_num == 1:
                    raise  # If first page fails, something is really wrong
                continue
        
        logger.info(f"Completed scrape. Found {len(results)} listings")
        return results
    
    def _scrape_page(self, query: str, page_num: int) -> list[dict]:
        """Scrape a single page."""
        url = f"{self.base_url}?q={query}"
        if page_num > 1:
            url += f"&page={page_num}"
        
        logger.debug(f"Fetching: {url}")
        
        try:
            # Use cloudscraper to get past Cloudflare
            response = self.scraper.get(
                url,
                timeout=15,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            logger.debug(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.warning(f"Page returned status {response.status_code}")
                return []
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all listings
            listings = self._find_listings_soup(soup)
            logger.info(f"Found {len(listings)} listings on page {page_num}")
            
            results = []
            for listing in listings:
                try:
                    item = self._extract_data_soup(listing)
                    if item and item.get('titulo') and item.get('precio_raw'):
                        results.append(item)
                except Exception as e:
                    logger.debug(f"Error extracting listing: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error fetching page: {e}")
            raise
    
    def _find_listings_soup(self, soup):
        """Find listing elements using BeautifulSoup."""
        # Try different selectors
        selectors = [
            ('a[href*="/anuncio/"]', 'a'),  # Direct links to listings
            ('article', 'article'),
            ('div.listing', 'div'),
            ('div[class*="ListingCard"]', 'div'),
            ('div[class*="card"]', 'div'),
        ]
        
        for css_selector, tag_name in selectors:
            try:
                elements = soup.select(css_selector)
                if len(elements) > 3:  # Need at least 4 results
                    logger.debug(f"Found {len(elements)} listings using selector: {css_selector}")
                    return elements
            except Exception as e:
                logger.debug(f"Selector error {css_selector}: {e}")
                continue
        
        # Fallback: try all links that look like listings
        logger.warning("No listings found with standard selectors. Trying fallback...")
        all_links = soup.find_all('a', href=re.compile(r'/anuncio/|/es/anuncio/'))
        if all_links:
            logger.debug(f"Found {len(all_links)} potential listing links via regex")
            return all_links
        
        return []
    
    def _extract_data_soup(self, element):
        """Extract listing data from BeautifulSoup element."""
        try:
            # Get title
            titulo = ""
            
            # Try title attribute
            if element.get('title'):
                titulo = element.get('title')
            
            # Try from text
            if not titulo:
                text = element.get_text(strip=True)
                if text:
                    titulo = text.split('\n')[0][:100]
            
            # Get price
            precio_raw = ""
            
            # Look for price elements
            price_elem = element.find(class_=re.compile(r'price|precio', re.I))
            if price_elem:
                precio_raw = price_elem.get_text(strip=True)
            
            # Look in all text for currency patterns
            if not precio_raw:
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
            
            # Make sure URL is absolute
            if url and not url.startswith('http'):
                if url.startswith('/'):
                    url = 'https://revolico.com' + url
                else:
                    url = 'https://revolico.com/' + url
            
            if titulo and precio_raw:
                return {
                    'titulo': titulo,
                    'precio_raw': precio_raw,
                    'url': url or "",
                    'fuente': 'revolico'
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting data: {e}")
            return None


def scrape_revolico_cloudflare(query: str, max_pages: int = 1) -> list[dict]:
    """Convenience function using Cloudflare bypass."""
    scraper = CloudflareBypassScraper()
    return scraper.scrape(query, max_pages)


if __name__ == "__main__":
    try:
        results = scrape_revolico_cloudflare("car", max_pages=1)
        print(f"✓ Found {len(results)} listings")
        for r in results[:3]:
            print(f"  - {r['titulo'][:60]}: {r['precio_raw']}")
    except Exception as e:
        print(f"✗ Error: {e}")
