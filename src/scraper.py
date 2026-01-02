import asyncio
from playwright.async_api import async_playwright
from faker import Faker
import random
import time

fake = Faker()

async def scrape_revolico(query: str) -> list[dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=fake.user_agent(),
            viewport={'width': 1280, 'height': 720}
        )
        
        # Block images and CSS
        await context.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet"] else route.continue_())
        
        page = await context.new_page()
        
        url = f"https://www.revolico.com/search.html?q={query}"
        await page.goto(url)
        
        # Random delay
        await asyncio.sleep(random.uniform(2, 5))
        
        # Assume listings have data-cy="listing"
        listings = await page.query_selector_all('[data-cy="listing"]')
        
        results = []
        for listing in listings:
            title_elem = await listing.query_selector('[data-cy="title"]')
            price_elem = await listing.query_selector('[data-cy="price"]')
            link_elem = await listing.query_selector('a')
            
            title = await title_elem.inner_text() if title_elem else ""
            price_text = await price_elem.inner_text() if price_elem else ""
            url = await link_elem.get_attribute('href') if link_elem else ""
            
            results.append({
                'titulo': title,
                'precio_raw': price_text,
                'url': url
            })
        
        await browser.close()
        return results

if __name__ == "__main__":
    # Test
    import asyncio
    results = asyncio.run(scrape_revolico("car"))
    print(results)