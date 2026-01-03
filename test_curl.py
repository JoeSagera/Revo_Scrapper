"""Test curl-direct scraper."""
print('\nTesting CURL-DIRECT scraper (native executable)\n')

from src.scraper_curl import scrape_revolico_curl

try:
    print('Fetching listings with curl...')
    results = scrape_revolico_curl('car', max_pages=1)
    
    print(f'\nFound {len(results)} listings\n')
    
    if results:
        for i, r in enumerate(results[:10], 1):
            print(f'{i}. {r["titulo"][:70]}')
            print(f'   Price: {r["precio_raw"]}')
            print(f'   URL: {r["url"][:60]}...\n')
    else:
        print('No listings found')
        
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
