"""Test ultimate scraper."""
print('\nTesting ULTIMATE Cloudflare bypass scraper...\n')

from src.scraper_ultimate import scrape_revolico_ultimate

try:
    print('Fetching listings...')
    results = scrape_revolico_ultimate('car', max_pages=1)
    
    print(f'\n✓ SUCCESS! Found {len(results)} listings\n')
    
    if results:
        for i, r in enumerate(results[:8], 1):
            print(f'{i}. {r["titulo"][:70]}')
            print(f'   Price: {r["precio_raw"]}')
    else:
        print('(No listings found - may need retry)')
        
except Exception as e:
    print(f'\n✗ ERROR: {e}')
    import traceback
    traceback.print_exc()

print()
