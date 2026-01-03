#!/usr/bin/env python
"""Test threading fix for Playwright on Windows+Python3.14."""
import sys
import time

print("\n" + "="*60)
print("TESTING THREADING-BASED PLAYWRIGHT FIX")
print("="*60 + "\n")

print("🔍 Testing hybrid scraper with threading...")
print("   This should work without NotImplementedError now\n")

try:
    from src.scraper_hybrid import scrape_revolico_hybrid
    
    print("⏳ Starting scrape... (browser should open)")
    print("   Allow 2-3 seconds for browser to launch\n")
    
    start = time.time()
    results = scrape_revolico_hybrid("car", max_pages=1)
    elapsed = time.time() - start
    
    if results:
        print(f"\n✅ SUCCESS!")
        print(f"   Found {len(results)} listings in {elapsed:.1f} seconds")
        for i, listing in enumerate(results[:3], 1):
            title = listing.get('title', 'No title')[:50]
            price = listing.get('price', 'N/A')
            print(f"   {i}. {title}... (${price})")
    else:
        print(f"\n⚠️ No results found (scraped in {elapsed:.1f} seconds)")
        print("   This might mean Revolico returned empty results")
        
except NotImplementedError as e:
    print(f"\n❌ STILL GETTING NotImplementedError!")
    print(f"   {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Other error: {type(e).__name__}")
    print(f"   {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ Threading fix is working!")
print("="*60 + "\n")
