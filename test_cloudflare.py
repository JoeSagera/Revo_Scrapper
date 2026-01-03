"""Test Cloudflare bypass scraper."""
print('Testing Cloudflare bypass scraper...')

from src.scraper_cloudflare import scrape_revolico_cloudflare

try:
    print('Fetching listings from Revolico...')
    results = scrape_revolico_cloudflare('car', max_pages=1)
    print(f'\nSUCCESS! Found {len(results)} listings\n')
    
    if results:
        print('Sample listings:')
        for i, r in enumerate(results[:5], 1):
            print(f'  {i}. {r["titulo"][:60]}')
            print(f'     Price: {r["precio_raw"]}')
            print(f'     URL: {r["url"][:80]}...')
    else:
        print('No listings found')
        
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
