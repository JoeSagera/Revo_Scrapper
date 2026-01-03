#!/usr/bin/env python
"""Direct scraper debugging - shows exact errors."""
import sys
import traceback
from logger import get_logger

logger = get_logger(__name__)

def test_hybrid():
    """Test hybrid scraper directly."""
    print("\n" + "="*60)
    print("TESTING HYBRID SCRAPER")
    print("="*60 + "\n")
    
    try:
        logger.info("Importing hybrid scraper...")
        from src.scraper_hybrid import scrape_revolico_hybrid
        
        logger.info("Calling scrape_revolico_hybrid('car', 1)...")
        print("🔍 Starting hybrid scrape - browser should open in 2-3 seconds...")
        print("   If you see a Cloudflare challenge, please solve it manually.")
        print("   The app will automatically continue scraping after the page loads.\n")
        
        results = scrape_revolico_hybrid("car", max_pages=1)
        
        if results:
            print(f"\n✅ SUCCESS! Found {len(results)} listings")
            for i, listing in enumerate(results[:3], 1):
                print(f"   {i}. {listing.get('title', 'No title')[:50]}...")
        else:
            print("\n⚠️ No results returned")
            
    except Exception as e:
        print(f"\n❌ ERROR IN HYBRID SCRAPER:")
        print(f"   {type(e).__name__}: {e}")
        traceback.print_exc()
        logger.error(f"Hybrid error: {e}", exc_info=True)


def test_all_methods():
    """Test all 5 methods to see which one works."""
    print("\n" + "="*60)
    print("TESTING ALL 5 METHODS")
    print("="*60 + "\n")
    
    methods = [
        ("hybrid", "scraper_hybrid", "scrape_revolico_hybrid"),
        ("requests", "scraper_requests", "scrape_revolico_requests"),
        ("curl", "scraper_curl", "scrape_revolico_curl"),
        ("ultimate", "scraper_ultimate", "scrape_revolico_ultimate"),
        ("playwright", "scraper", "_scrape_playwright"),
    ]
    
    for name, module, func in methods:
        print(f"\n🔄 Testing {name.upper()}...", end=" ")
        try:
            if name == "playwright":
                from src.scraper import RevolicoScraper
                scraper = RevolicoScraper()
                results = scraper._scrape_playwright("car", 1)
            else:
                mod = __import__(f"src.{module}", fromlist=[func])
                fn = getattr(mod, func)
                results = fn("car", 1)
            
            if results:
                print(f"✅ SUCCESS ({len(results)} listings)")
            else:
                print("⚠️ No results")
        except Exception as e:
            print(f"❌ FAILED: {type(e).__name__}")
            print(f"   Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        test_all_methods()
    else:
        test_hybrid()
