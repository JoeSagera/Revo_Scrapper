"""Test hybrid scraper."""
print('\n' + '='*60)
print('Testing HYBRID scraper (Playwright visible + manual Cloudflare)')
print('='*60)

from src.scraper_hybrid import scrape_revolico_hybrid

try:
    print('\nThe browser will open in a few seconds...')
    print('If you see a Cloudflare challenge, please complete it manually.')
    print('The app will then automatically scrape the page.\n')
    
    import time
    time.sleep(2)
    
    results = scrape_revolico_hybrid('car', max_pages=1)
    
    print(f'\n' + '='*60)
    print(f'SUCCESS! Found {len(results)} listings')
    print('='*60)
    
    if results:
        for i, r in enumerate(results[:10], 1):
            print(f'\n{i}. {r["titulo"][:70]}')
            print(f'   Price: {r["precio_raw"]}')
    else:
        print('\nNo listings found - Cloudflare may have blocked the request')
    
    print('\n' + '='*60 + '\n')
        
except Exception as e:
    print(f'\nERROR: {e}')
    import traceback
    traceback.print_exc()
    print()
