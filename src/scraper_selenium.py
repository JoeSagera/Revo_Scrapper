"""Selenium-based scraper for Revolico (handles Cloudflare)."""
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
from logger import get_logger
import config

logger = get_logger(__name__)


class RevolicoSeleniumScraper:
    """Scraper using Selenium with undetected_chromedriver (bypasses Cloudflare)."""
    
    def __init__(self):
        self.base_url = config.REVOLICO_SEARCH_URL
        self.timeout = config.SCRAPER_TIMEOUT
        
    def scrape(self, query: str, max_pages: int = 1) -> list[dict]:
        """
        Scrape Revolico listings using Selenium.
        
        Args:
            query: Search query
            max_pages: Maximum number of pages to scrape
            
        Returns:
            List of listing dictionaries
        """
        logger.info(f"Starting Selenium scrape for: {query} ({max_pages} pages)")
        
        # Use undetected_chromedriver to bypass Cloudflare
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")  # Use new headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        driver = None
        try:
            driver = uc.Chrome(options=options, version_main=None)
            results = []
            
            for page_num in range(1, max_pages + 1):
                logger.info(f"Scraping page {page_num}")
                page_results = self._scrape_page(driver, query, page_num)
                results.extend(page_results)
                
                if page_num < max_pages:
                    time.sleep(random.uniform(2, 4))
            
            return results
            
        except Exception as e:
            logger.error(f"Selenium scraping error: {e}", exc_info=True)
            raise
        finally:
            if driver:
                driver.quit()
    
    def _scrape_page(self, driver, query: str, page_num: int) -> list[dict]:
        """Scrape a single page."""
        url = f"{self.base_url}?q={query}"
        if page_num > 1:
            url += f"&page={page_num}"
        
        try:
            logger.debug(f"Loading {url}")
            driver.get(url)
            
            # Wait for listings to load
            wait = WebDriverWait(driver, 15)
            
            # Try to wait for common elements
            try:
                wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "a[href*='/anuncio/'], article, div[class*='card']")
                ))
                logger.debug("Listings loaded")
            except:
                logger.warning("Timeout waiting for listings")
            
            time.sleep(random.uniform(1, 3))
            
            # Get listings
            listings = self._find_listings(driver)
            logger.info(f"Found {len(listings)} listings on page {page_num}")
            
            results = []
            for listing_elem in listings:
                try:
                    item = self._extract_data(listing_elem)
                    if item and item.get('titulo') and item.get('precio_raw'):
                        results.append(item)
                except Exception as e:
                    logger.debug(f"Error extracting listing: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error scraping page {page_num}: {e}")
            return []
    
    def _find_listings(self, driver):
        """Find all listing elements on the page."""
        # Try different selectors
        selectors = [
            "a[href*='/anuncio/']",  # Direct links to listings
            "article",
            "div[class*='ListingCard']",
            "div[class*='listing-item']",
            "div[class*='card']",
            "div[class*='item']",
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(elements) > 3:  # Need at least 4 results
                    logger.debug(f"Found {len(elements)} elements with {selector}")
                    return elements
            except:
                pass
        
        logger.warning("No listings found with standard selectors")
        return []
    
    def _extract_data(self, element):
        """Extract listing data from element."""
        try:
            # Get title
            titulo = ""
            try:
                titulo = element.get_attribute("title")
            except:
                pass
            
            if not titulo:
                try:
                    titulo = element.text.split('\n')[0][:100]
                except:
                    pass
            
            # Get price
            precio_raw = ""
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, "[class*='price'], [class*='precio']")
                precio_raw = price_elem.text
            except:
                try:
                    text = element.text
                    # Look for currency patterns
                    import re
                    match = re.search(r'([\d,\.]+\s*(USD|CUP|MLC|pesos))', text, re.IGNORECASE)
                    if match:
                        precio_raw = match.group(1)
                except:
                    pass
            
            # Get URL
            url = ""
            try:
                url = element.get_attribute("href")
            except:
                pass
            
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


def scrape_revolico_selenium(query: str, max_pages: int = 1) -> list[dict]:
    """Convenience function using Selenium."""
    scraper = RevolicoSeleniumScraper()
    return scraper.scrape(query, max_pages)


if __name__ == "__main__":
    results = scrape_revolico_selenium("car", max_pages=1)
    print(f"Found {len(results)} listings")
    for r in results[:3]:
        print(r)
