import asyncio
import json
from src.scraper import scrape_revolico
from src.processor import process_data

async def main(query: str):
    print("Scraping...")
    data = await scrape_revolico(query)
    
    print("Processing...")
    df = process_data(data)
    
    print("Saving...")
    df.to_json('data/results.json', orient='records', indent=2)
    
    print("Done.")

if __name__ == "__main__":
    query = "car"  # or input
    asyncio.run(main(query))