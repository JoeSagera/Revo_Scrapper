import asyncio
import json
import os
from src.scraper import scrape_revolico
from src.processor import DataProcessor

async def main(query: str, exchange_rate=350):
    print("Scraping...")
    data = await scrape_revolico(query)
    
    print("Processing...")
    processor = DataProcessor(exchange_rate=exchange_rate)
    df = processor.process_data(data)
    
    print("Saving...")
    os.makedirs('data', exist_ok=True)
    df.to_json('data/results.json', orient='records', indent=2)
    
    # Print Summary
    avg_price = df['price_usd'].mean()
    total_ads = len(df)
    num_deals = (df['label'] == '🔥 GANGA').sum()
    num_scams = (df['label'] == '⚠️ POSIBLE ESTAFA').sum()
    
    print("Summary:")
    print(f"Average Price (USD): {avg_price:.2f}")
    print(f"Total Ads Found: {total_ads}")
    print(f"Number of Deals: {num_deals}")
    print(f"Number of Possible Scams: {num_scams}")
    
    print("Done.")

if __name__ == "__main__":
    query = "car"  # or input
    asyncio.run(main(query))