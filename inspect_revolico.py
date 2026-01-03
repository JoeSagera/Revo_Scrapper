#!/usr/bin/env python
"""Inspect what Revolico HTML looks like."""
import requests
from bs4 import BeautifulSoup
import json

print("\n" + "="*60)
print("INSPECTING REVOLICO HTML RESPONSE")
print("="*60 + "\n")

url = "https://www.revolico.com/search.html?q=car"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br'
}

print(f"🌐 Fetching: {url}\n")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"📊 Status Code: {response.status_code}")
    print(f"📋 Content-Type: {response.headers.get('content-type', 'Unknown')}")
    print(f"📏 Content Length: {len(response.content)} bytes\n")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try different selectors
        selectors_to_try = [
            ('a[href*="/anuncio/"]', 'Links with /anuncio/'),
            ('a[href*="/es/anuncio/"]', 'Links with /es/anuncio/'),
            ('article', 'Article tags'),
            ('[data-testid*="listing"]', 'Data-testid with listing'),
            ('div.listing', 'Div with class listing'),
            ('h2', 'H2 tags (potential titles)'),
            ('span.price', 'Price spans'),
            ('.price', 'Price classes'),
        ]
        
        print("🔍 SELECTOR RESULTS:")
        print("-" * 60)
        
        for selector, description in selectors_to_try:
            try:
                results = soup.select(selector)
                count = len(results)
                print(f"✓ {description:30} : {count:3} found")
                
                if count > 0 and count <= 3:
                    for i, elem in enumerate(results[:3], 1):
                        print(f"    {i}. {str(elem)[:100]}...")
            except Exception as e:
                print(f"✗ {description:30} : Error - {e}")
        
        # Check page structure
        print("\n📄 PAGE STRUCTURE:")
        print("-" * 60)
        
        body = soup.find('body')
        if body:
            # Look for any text mentioning "anuncio", "listings", "results"
            text = body.get_text().lower()
            
            has_results = 'resultado' in text or 'result' in text
            has_anuncio = 'anuncio' in text
            has_error = 'cloudflare' in text or 'just a moment' in text.lower()
            
            print(f"✓ Has 'resultado/result': {has_results}")
            print(f"✓ Has 'anuncio': {has_anuncio}")
            print(f"✓ Has Cloudflare/challenge: {has_error}")
            
            if has_error:
                print("\n⚠️ PAGE APPEARS TO BE SHOWING CLOUDFLARE CHALLENGE")
                print("   (This is expected for HTTP requests without browser)")
        
        # Save first 2000 chars of HTML for inspection
        with open('revolico_sample.html', 'w', encoding='utf-8') as f:
            f.write(response.text[:5000])
        print("\n💾 Saved first 5000 chars to revolico_sample.html")
        
    else:
        print(f"❌ Got status {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60 + "\n")
