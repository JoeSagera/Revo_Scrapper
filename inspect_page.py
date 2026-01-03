"""Inspect Revolico page structure."""
from playwright.sync_api import sync_playwright
import time
import re
import os

# Set encoding to UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    page = browser.new_page()
    
    url = "https://revolico.com/es/search?q=car"
    print(f"Loading {url}...")
    print("(Cloudflare may block initial connection - waiting...)")
    
    try:
        # First load
        response = page.goto(url, timeout=60000, wait_until="domcontentloaded")
        print(f"Initial response: {response.status if response else 'None'}")
        
        # Wait for Cloudflare challenge to complete
        print("Waiting for Cloudflare challenge completion...")
        page.wait_for_load_state("networkidle", timeout=60000)
        print("Page fully loaded")
        
    except Exception as e:
        print(f"Load timeout (might be Cloudflare block): {e}")
        print("Continuing with partial page...")
    
    time.sleep(3)
    
    html = page.content()
    
    # Save a sample to analyze
    with open('page_sample.html', 'w', encoding='utf-8') as f:
        f.write(html[:5000])  # First 5000 chars
    
    print("\n=== Page Analysis ===")
    
    # Look for common patterns
    if 'anuncio' in html.lower():
        print("Found 'anuncio' in page")
    if 'listing' in html.lower():
        print("Found 'listing' in page")
    if 'card' in html.lower():
        print("Found 'card' in page")
    if 'product' in html.lower():
        print("Found 'product' in page")
    
    # Look for price patterns
    prices = re.findall(r'USD|CUP|pesos|euros', html, re.IGNORECASE)
    print(f"Found {len(prices)} price mentions")
    
    # Count articles and divs
    articles = html.count('<article')
    divs = html.count('<div')
    print(f"HTML has {articles} articles, {divs} divs")
    
    # Try to find listings with more detailed selectors
    page.wait_for_selector('div', timeout=5000)
    
    all_articles = page.query_selector_all('article')
    print(f"Found {len(all_articles)} <article> elements")
    
    all_links = page.query_selector_all('a[href*="/anuncio/"]')
    print(f"Found {len(all_links)} links with '/anuncio/'")
    
    # Save HTML snippet for inspection
    print(f"\nTotal HTML length: {len(html)}")
    print("Saved first 5000 chars to page_sample.html")
    
    browser.close()
    print("\nInspection complete")
