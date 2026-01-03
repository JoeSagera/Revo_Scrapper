#!/usr/bin/env python
"""Test scraper_hybrid directly to see what's happening."""
import sys
import time
from logger import get_logger

logger = get_logger(__name__)

def test_hybrid_directly():
    """Test hybrid scraper directly."""
    print("\n" + "="*60)
    print("TESTING HYBRID SCRAPER DIRECTLY")
    print("="*60 + "\n")
    
    try:
        from src.scraper_hybrid import HybridInteractiveScraper
        
        print("🔍 Creating scraper...")
        scraper = HybridInteractiveScraper()
        
        print("📍 Calling scrape() method...")
        print("   📢 Browser should open in next 2-3 seconds\n")
        
        start = time.time()
        results = scraper.scrape("car", max_pages=1)
        elapsed = time.time() - start
        
        if results:
            print(f"\n✅ SUCCESS! Found {len(results)} listings in {elapsed:.1f}s")
        else:
            print(f"\n⚠️ No results (scraped in {elapsed:.1f}s)")
            
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_via_scraper_module():
    """Test via scraper.py function."""
    print("\n" + "="*60)
    print("TESTING VIA scraper.scrape_revolico()")
    print("="*60 + "\n")
    
    try:
        from src.scraper import scrape_revolico
        
        print("📍 Calling scrape_revolico('car')...")
        print("   📢 Browser should open in next 2-3 seconds\n")
        
        start = time.time()
        results = scrape_revolico("car", max_pages=1)
        elapsed = time.time() - start
        
        if results:
            print(f"\n✅ SUCCESS! Found {len(results)} listings in {elapsed:.1f}s")
        else:
            print(f"\n⚠️ No results (scraped in {elapsed:.1f}s)")
            
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"   {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_num = sys.argv[1] if len(sys.argv) > 1 else "1"
    
    if test_num == "2":
        success = test_via_scraper_module()
    else:
        success = test_hybrid_directly()
    
    sys.exit(0 if success else 1)
