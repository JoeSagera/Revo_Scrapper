"""Test using httpx (modern HTTP client)."""
print('\nTesting httpx...\n')

try:
    import httpx
    
    # Create client with modern setup
    client = httpx.Client(
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        },
        follow_redirects=True,
        timeout=15
    )
    
    url = 'https://revolico.com/es/search?q=car'
    print(f'Fetching {url} with httpx...')
    
    response = client.get(url)
    print(f'Status: {response.status_code}')
    
    html_size = len(response.text)
    print(f'Response size: {html_size} bytes')
    
    if 'anuncio' in response.text.lower():
        print('SUCCESS! Got real content with listings')
    elif 'Just a moment' in response.text or 'cf-challenge' in response.text:
        print('Got Cloudflare challenge page')
    else:
        print('Got page but no listings found')
    
    # Show first 300 chars
    print(f'\nFirst 300 chars:\n{response.text[:300]}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
