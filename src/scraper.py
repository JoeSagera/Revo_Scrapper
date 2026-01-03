"""Advanced web scraper for Revolico listings."""
import random
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright, Page
from faker import Faker
from logger import get_logger
import config

logger = get_logger(__name__)
fake = Faker()


class RevolicoScraper:
    """Scraper for Revolico.com listings."""
    
    def __init__(self):
        self.base_url = config.REVOLICO_SEARCH_URL
        self.timeout = config.SCRAPER_TIMEOUT
        self.headless = config.SCRAPER_HEADLESS
        
    def scrape(self, query: str, max_pages: int = 1) -> list[dict]:
        """
        Scrape Revolico listings for a given query.
        
        Tries multiple methods:
        1. Hybrid (user solves Cloudflare challenge manually - MOST RELIABLE)
        2. Requests with proper headers
        3. Curl direct
        4. Ultimate bypass
        5. Playwright headless
        
        Args:
            query: Search query
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of listing dictionaries
        """
        logger.info(f"Starting scrape for query: {query} (max {max_pages} pages)")
        
        # NOTE: Hybrid interactive scraper disabled on Python 3.14 (Playwright bug)
        # Playwright has known issues with asyncio.subprocess on Python 3.14 Windows
        # Try requests method instead
        logger.info("Skipping HYBRID scraper (Playwright incompatible with Python 3.14)")
        
        # Try requests
        try:
            logger.info("Attempting requests scraper...")
            from src.scraper_requests import scrape_revolico_requests
            results = scrape_revolico_requests(query, max_pages)
            if results and len(results) > 0:
                logger.info(f"Success with requests: {len(results)} listings")
                return results
            logger.info("Requests returned no results, trying curl-direct...")
        except Exception as e:
            logger.warning(f"Requests failed: {e}. Trying curl-direct...")
        
        # Try curl direct
        try:
            logger.info("Attempting curl-direct scraping...")
            from src.scraper_curl import scrape_revolico_curl
            results = scrape_revolico_curl(query, max_pages)
            if results and len(results) > 0:
                logger.info(f"Success with curl-direct: {len(results)} listings")
                return results
            logger.info("curl-direct returned no results, trying ultimate bypass...")
        except Exception as e:
            logger.warning(f"curl-direct failed: {e}. Trying ultimate bypass...")
        
        # Try ultimate bypass
        try:
            logger.info("Attempting ultimate Cloudflare bypass...")
            from src.scraper_ultimate import scrape_revolico_ultimate
            results = scrape_revolico_ultimate(query, max_pages)
            if results and len(results) > 0:
                logger.info(f"Success with ultimate bypass: {len(results)} listings")
                return results
            logger.info("Ultimate bypass returned no results, trying Playwright...")
        except Exception as e:
            logger.warning(f"Ultimate bypass failed: {e}. Trying Playwright...")
        
        # All HTTP methods failed
        logger.error("All HTTP scraping methods failed")
        raise Exception(
            "All scraping methods failed. Revolico requires either:\n"
            "1. Real browser interaction (Playwright - not compatible with Python 3.14)\n"
            "2. Proxy services like ScraperAPI\n"
            "Try restarting or use mock data for testing"
        )
    
    def _scrape_playwright(self, query: str, max_pages: int) -> list[dict]:
        """Internal Playwright scraping - DISABLED on Python 3.14 (asyncio bug)."""
        raise Exception(
            "Playwright is disabled on Python 3.14 (known incompatibility with asyncio.subprocess)\n"
            "Python 3.14 has a bug that breaks subprocess creation in asyncio.\n"
            "Alternatives:\n"
            "1. Downgrade to Python 3.13\n"
            "2. Use mock data mode\n"
            "3. Use a paid API service"
        )
    
    def _scrape_playwright(self, query: str, max_pages: int) -> list[dict]:
        """Internal Playwright scraping implementation (runs in thread to avoid asyncio issues)."""
        from src.threading_wrapper import run_playwright_in_thread
        return run_playwright_in_thread(self._scrape_playwright_internal, query, max_pages)
    
    def _scrape_playwright_internal(self, query: str, max_pages: int) -> list[dict]:
        """Playwright scraping implementation (runs in thread)."""
        results = []
        
        with sync_playwright() as p:
            # Launch with stealth mode to bypass Cloudflare
            browser = p.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                user_agent=fake.user_agent() if config.USER_AGENT_ROTATION else None,
                viewport={'width': 1280, 'height': 720}
            )
            
            # Add stealth script to hide automation
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
            """)
            
            # Block resource types to speed up scraping
            context.route(
                "**/*",
                lambda route: route.abort() if route.request.resource_type in 
                ["image", "stylesheet", "font", "media"] else route.continue_()
            )
            
            page = context.new_page()
            
            for page_num in range(1, max_pages + 1):
                logger.info(f"Scraping page {page_num}")
                results.extend(self._scrape_page(page, query, page_num))
                
                # Random delay between pages
                if page_num < max_pages:
                    delay = random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX)
                    logger.debug(f"Waiting {delay:.2f}s before next page")
                    page.wait_for_timeout(int(delay * 1000))
            
            browser.close()
        
        logger.info(f"Completed scrape. Found {len(results)} listings")
        return results
    
    def _scrape_page(self, page: Page, query: str, page_num: int = 1) -> list[dict]:
        """Scrape a single page of results."""
        url = f"{self.base_url}?q={query}&page={page_num}" if page_num > 1 else f"{self.base_url}?q={query}"
        
        try:
            logger.debug(f"Navigating to {url}")
            page.goto(url, timeout=self.timeout, wait_until="networkidle")
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return []
        
        # Wait for listings to load - try multiple wait strategies
        try:
            # Try to wait for common listing selectors
            page.wait_for_selector('article, div[class*="card"], div[class*="item"], a[href*="/anuncio/"]', timeout=5000)
            logger.debug("Waited for listings to load")
        except Exception as e:
            logger.warning(f"Timeout waiting for listings: {e}")
        
        # Random delay after page load
        page.wait_for_timeout(random.randint(1000, 3000))
        
        # Try multiple selector strategies
        listings = self._find_listings(page)
        logger.info(f"Found {len(listings)} listings on page {page_num}")
        
        results = []
        for i, listing in enumerate(listings):
            try:
                item = self._extract_listing_data(listing)
                if item and item.get('titulo') and item.get('precio_raw'):
                    results.append(item)
                    logger.debug(f"Extracted listing {i+1}: {item['titulo'][:50]}")
            except Exception as e:
                logger.warning(f"Error extracting listing {i+1}: {e}")
                continue
        
        return results
    
    def _find_listings(self, page: Page) -> list:
        """Find listing containers using multiple selector strategies."""
        # Dump page HTML for debugging
        logger.debug("Page content length: " + str(len(page.content())))
        
        # Strategy 1: data-cy attribute (modern Revolico)
        listings = page.query_selector_all('[data-cy="listing"]')
        if listings:
            logger.debug("Found listings using [data-cy='listing']")
            return listings
        
        # Strategy 2: Class-based selectors
        selectors_to_try = [
            'div[class*="ListingCard"]',
            'div[class*="listing-item"]',
            'article[class*="listing"]',
            'div.listing',
            '[class*="ProductCard"]',
            'div[class*="ad-item"]',
            # More aggressive strategies
            'article',  # Try all articles
            'div[class*="card"]',
            'div[class*="item"]',
            'a[class*="listing"]',
            'section[class*="listing"]',
            'div[data-testid*="listing"]',
            # Maybe it's a link-based structure
            'a[href*="/es/anuncio/"]',
            'a[href*="/anuncio/"]',
            'div > a[href*="/"]',  # All links in divs
        ]
        
        for selector in selectors_to_try:
            try:
                listings = page.query_selector_all(selector)
                if listings and len(listings) > 5:  # Only return if we got multiple results
                    logger.debug(f"Found {len(listings)} listings using {selector}")
                    return listings
                elif listings:
                    logger.debug(f"Found only {len(listings)} listings using {selector} (need more)")
            except Exception as e:
                logger.debug(f"Selector failed {selector}: {e}")
                continue
        
        # If all selectors fail, try to get all divs and look for price patterns
        logger.warning("Could not find listings with standard selectors. Trying fallback...")
        all_divs = page.query_selector_all('div')
        logger.debug(f"Total divs on page: {len(all_divs)}")
        
        return []
    
    def _extract_listing_data(self, listing) -> dict:
        """Extract data from a listing element."""
        try:
            # Title extraction
            titulo = self._extract_text(listing, [
                '[data-cy="title"]',
                'h2, h3',
                '[class*="title"]',
                'a[class*="link"]'
            ])
            
            # Price extraction
            precio_raw = self._extract_text(listing, [
                '[data-cy="price"]',
                '[class*="price"]',
                'span[class*="amount"]',
                '[class*="cost"]'
            ])
            
            # URL extraction
            url = ""
            for selector in ['a[data-cy="listing-link"]', 'a[href*="/listing/"]', 'a']:
                link = listing.query_selector(selector)
                if link:
                    url = link.get_attribute('href')
                    if url:
                        # Make absolute URL if necessary
                        if not url.startswith('http'):
                            url = urljoin(config.REVOLICO_BASE_URL, url)
                        break
            
            return {
                'titulo': titulo.strip() if titulo else "",
                'precio_raw': precio_raw.strip() if precio_raw else "",
                'url': url if url else ""
            }
        except Exception as e:
            logger.warning(f"Error extracting listing data: {e}")
            return None
    
    def _extract_text(self, element, selectors: list[str]) -> str:
        """Try multiple selectors to extract text."""
        for selector in selectors:
            try:
                el = element.query_selector(selector)
                if el:
                    text = el.inner_text()
                    if text:
                        return text
            except Exception:
                continue
        return ""


def scrape_revolico(query: str, max_pages: int = 1) -> list[dict]:
    """Convenience function to scrape Revolico."""
    scraper = RevolicoScraper()
    return scraper.scrape(query, max_pages)


if __name__ == "__main__":
    results = scrape_revolico("car", max_pages=1)
    for r in results[:5]:
        print(r)