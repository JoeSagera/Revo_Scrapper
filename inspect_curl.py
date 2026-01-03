"""Save curl HTML for inspection."""
import subprocess
from bs4 import BeautifulSoup

url = "https://www.revolico.com/es/search?q=car"

print(f"Fetching {url} with curl...")

cmd = [
    "curl.exe",
    "-L",
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "-H", "Accept-Language: en-US,en;q=0.5",
    "-H", "Accept-Encoding: gzip, deflate",
    "-H", "DNT: 1",
    "-H", "Connection: keep-alive",
    "--max-time", "15",
    url
]

result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')

html = result.stdout

print(f"Got {len(html)} bytes")

# Save to file
with open('curl_output.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Parse and analyze
soup = BeautifulSoup(html, 'html.parser')

# Look for listings
links = soup.find_all('a', href=True)
listing_links = [l for l in links if '/anuncio/' in l.get('href', '')]

print(f"Found {len(links)} links total")
print(f"Found {len(listing_links)} listing links")

# Look for any product-related elements
articles = soup.find_all('article')
print(f"Found {len(articles)} articles")

divs_with_class = soup.find_all('div', class_=True)
print(f"Found {len(divs_with_class)} divs with class")

# Print first 500 chars
print(f"\nFirst 500 chars of HTML:")
print(html[:500])

# Count common patterns
if 'Cloudflare' in html:
    print("\n! WARNING: Cloudflare security page detected")
if 'Just a moment' in html:
    print("\n! WARNING: Cloudflare challenge page")
if 'anuncio' in html.lower():
    print("\n✓ Found 'anuncio' in HTML")
if 'car' in html.lower():
    print("✓ Found 'car' in HTML")
    
print("\nHTML saved to curl_output.html")
