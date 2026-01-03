"""Hybrid scraper: User solves Cloudflare challenge manually, app scrapes automatically."""
from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup
import re
import time
import random
from logger import get_logger
from src.threading_wrapper import run_playwright_in_thread
import config

logger = get_logger(__name__)


class HybridInteractiveScraper:
    """
    Scraper that shows browser to user for Cloudflare challenge,
    then automatically scrapes once challenge is passed.
    """
    
    def __init__(self):
        self.base_url = config.REVOLICO_SEARCH_URL
        
    def scrape(self, query: str, max_pages: int = 1) -> list[dict]:
        """
        Scrape with user interaction for Cloudflare challenge.
        
        Browser will be VISIBLE so user can complete the challenge.
        
        Args:
            query: Search query
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of listings
        """
        logger.info(f"Starting HYBRID scrape for: {query} ({max_pages} pages)")
        logger.info("Browser will open - please complete Cloudflare challenge if it appears")
        
        # Run in thread to avoid asyncio conflicts on Windows+Python3.14
        return run_playwright_in_thread(self._scrape_internal, query, max_pages)
    
    def _scrape_internal(self, query: str, max_pages: int) -> list[dict]:
        """Internal scrape logic (runs in thread)."""
        results = []
        
        with sync_playwright() as p:
            # Launch with headless=False so user can see and interact
            browser = p.chromium.launch(
                headless=False,  # VISIBLE BROWSER - user can see and solve captcha
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                ]
            )
            
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = context.new_page()
            
            for page_num in range(1, max_pages + 1):
                logger.info(f"Scraping page {page_num}")
                try:
                    page_results = self._scrape_page_interactive(page, query, page_num)
                    results.extend(page_results)
                    
                    if page_num < max_pages:
                        time.sleep(random.uniform(2, 4))
                        
                except Exception as e:
                    logger.error(f"Error on page {page_num}: {e}")
                    if page_num == 1:
                        raise
                    continue
            
            browser.close()
        
        logger.info(f"Found {len(results)} listings")
        return results
    
    def _scrape_page_interactive(self, page: Page, query: str, page_num: int) -> list[dict]:
        """Scrape a page with user interaction for Cloudflare."""
        url = f"{self.base_url}?q={query}"
        if page_num > 1:
            url += f"&page={page_num}"
        
        logger.info(f"Navigating to {url}")
        logger.info("Please complete Cloudflare challenge if it appears (you have 60 seconds)")
        
        try:
            # Navigate and wait for page to load
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            
            # Wait for Cloudflare to be passed - look for listings to appear
            logger.info("Waiting for content to load (up to 45 seconds)...")
            
            try:
                # Wait for specific elements we're looking for
                page.wait_for_selector(
                    'a[href*="/anuncio/"], a[href*="/es/anuncio/"], article, [data-testid*="listing"]',
                    timeout=45000
                )
                logger.info("Found listing elements!")
            except:
                logger.warning("Timeout waiting for standard selectors - checking anyway")
            
            # Give page extra time to fully render
            import time
            time.sleep(3)
            
            # Get HTML
            html = page.content()
            
            # Check if still on Cloudflare
            if 'Just a moment' in html or len(html) < 5000:
                logger.warning("Still on Cloudflare or page too small - waiting 30 seconds...")
                logger.info("Please complete the challenge manually in the browser window")
                time.sleep(30)
                html = page.content()
            
            return self._extract_listings(html)
            
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            raise
    
    def _extract_listings(self, html: str) -> list[dict]:
        """Extract listings from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        if 'Just a moment' in html:
            logger.warning("Still on Cloudflare page - couldn't get real content")
            return []
        
        # First, check what we actually have on the page
        logger.debug(f"HTML length: {len(html)}")
        
        # Try MANY different selectors
        listings = []
        
        selectors_to_try = [
            ('a[href*="/anuncio/"]', 'a'),
            ('a[href*="/es/anuncio/"]', 'a'),
            ('article', 'article'),
            ('div[class*="ListingCard"]', 'div'),
            ('div[class*="listing"]', 'div'),
            ('div[class*="card"]', 'div'),
            ('div[class*="item"]', 'div'),
            ('a[href*="/anuncio"], a[href*="/es/anuncio"]', 'a'),
            ('[role="link"][href*="/anuncio/"]', 'element'),
            ('div > a', 'a'),  # Any link in div
            ('main a', 'a'),  # Links in main
            ('[data-testid*="listing"]', 'div'),
            ('[data-cy*="listing"]', 'div'),
        ]
        
        for selector, name in selectors_to_try:
            try:
                found = soup.select(selector)
                if len(found) > 3:  # Need at least 4 results
                    logger.info(f"Found {len(found)} results with selector: {selector}")
                    listings = found
                    break
                elif len(found) > 0:
                    logger.debug(f"Found {len(found)} results with {selector} (too few)")
            except Exception as e:
                logger.debug(f"Selector error {selector}: {e}")
                continue
        
        # If no listings found, try to find ANY links that look relevant
        if not listings:
            logger.warning("No standard selectors matched - trying fallback")
            all_links = soup.find_all('a', href=True)
            relevant_links = [l for l in all_links if 'anuncio' in l.get('href', '').lower()]
            if len(relevant_links) > 3:
                logger.info(f"Found {len(relevant_links)} links with 'anuncio' in href")
                listings = relevant_links
            else:
                logger.warning(f"Only found {len(relevant_links)} relevant links - page may not have loaded")
        
        if not listings:
            logger.warning("No listings found on page")
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
        titulo = ""
        
        # Try multiple ways to get title
        if element.get('title'):
            titulo = element.get('title')
        
        if not titulo and element.get('aria-label'):
            titulo = element.get('aria-label')
        
        if not titulo:
            text = element.get_text(strip=True)
            if text:
                # Take first line as title
                lines = text.split('\n')
                titulo = lines[0][:100]
        
        # Get all text for price extraction
        full_text = element.get_text()
        
        # Try to find price in multiple patterns
        precio_raw = ""
        
        # Pattern 1: Number followed by currency
        match = re.search(r'([\d,\.]+)\s*(USD|CUP|MLC|pesos)', full_text, re.IGNORECASE)
        if match:
            precio_raw = f"{match.group(1)} {match.group(2)}"
        
        # Pattern 2: Just currency mentions with numbers
        if not precio_raw:
            match = re.search(r'([\d,\.]+\s*(?:USD|CUP|MLC))', full_text, re.IGNORECASE)
            if match:
                precio_raw = match.group(1)
        
        # Pattern 3: Try to find any price element
        if not precio_raw:
            price_elem = element.find(class_=re.compile(r'price|precio|cost', re.I))
            if price_elem:
                precio_raw = price_elem.get_text(strip=True)
        
        # Get URL
        url = ""
        if element.name == 'a':
            url = element.get('href', '')
        else:
            link = element.find('a', href=True)
            if link:
                url = link.get('href', '')
        
        # Make URL absolute
        if url:
            if not url.startswith('http'):
                if url.startswith('/'):
                    url = 'https://revolico.com' + url
                else:
                    url = 'https://revolico.com/' + url
        
        # Only return if we have both title and price
        if titulo and precio_raw:
            return {
                'titulo': titulo.strip(),
                'precio_raw': precio_raw.strip(),
                'url': url,
                'fuente': 'revolico'
            }
        
        return None


def scrape_revolico_hybrid(query: str, max_pages: int = 1) -> list[dict]:
    """Hybrid scraper with user interaction."""
    scraper = HybridInteractiveScraper()
    return scraper.scrape(query, max_pages)


if __name__ == "__main__":
    try:
        print("\nStarting hybrid scraper (browser will open)...")
        results = scrape_revolico_hybrid("car", max_pages=1)
        print(f"\nFound {len(results)} listings\n")
        for r in results[:5]:
            print(f"  - {r['titulo'][:60]}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
