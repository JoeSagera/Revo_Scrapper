"""Test requests scraper."""
print('\nTesting REQUESTS scraper\n')

from src.scraper_requests import scrape_revolico_requests

try:
    print('Fetching listings with requests...')
    results = scrape_revolico_requests('car', max_pages=1)
    
    print(f'\nFound {len(results)} listings\n')
    
    if results:
        for i, r in enumerate(results[:10], 1):
            print(f'{i}. {r["titulo"][:70]}')
            print(f'   Price: {r["precio_raw"]}')
    else:
        print('No listings found')
        
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()

print()
