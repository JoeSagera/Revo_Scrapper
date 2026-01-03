"""Main orchestrator for Revolico scraper."""
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from src.scraper import scrape_revolico
from src.processor import DataProcessor
from logger import get_logger
import config

logger = get_logger(__name__)


async def main(query: str, max_pages: int = 1, use_mock: bool = False):
    """
    Main scraping and processing pipeline.
    
    Args:
        query: Search query
        max_pages: Number of pages to scrape
        use_mock: Use mock data instead of real scraping
    """
    logger.info(f"Starting pipeline: query='{query}', pages={max_pages}, mock={use_mock}")
    
    # Scrape
    if use_mock:
        logger.info("Using mock data for testing")
        data = [
            {'titulo': 'Car 1', 'precio_raw': '150 USD', 'url': 'http://example.com/1'},
            {'titulo': 'Car 2', 'precio_raw': '40.000 CUP', 'url': 'http://example.com/2'},
            {'titulo': 'Car 3', 'precio_raw': '200 USD', 'url': 'http://example.com/3'},
            {'titulo': 'Car 4', 'precio_raw': '5.000 CUP', 'url': 'http://example.com/4'},
            {'titulo': 'Car 5', 'precio_raw': '300 USD', 'url': 'http://example.com/5'},
            {'titulo': 'Car 6', 'precio_raw': '75 USD', 'url': 'http://example.com/6'},
            {'titulo': 'Car 7', 'precio_raw': '100.000 CUP', 'url': 'http://example.com/7'},
        ]
    else:
        logger.info("Scraping Revolico")
        try:
            data = await scrape_revolico(query, max_pages=max_pages)
        except Exception as e:
            logger.error(f"Scraping failed: {e}", exc_info=True)
            return
    
    if not data:
        logger.warning("No data scraped. Exiting.")
        return
    
    logger.info(f"Scraped {len(data)} listings")
    
    # Process
    logger.info("Processing data")
    try:
        processor = DataProcessor()
        df = processor.process_data(data)
    except Exception as e:
        logger.error(f"Processing failed: {e}", exc_info=True)
        return
    
    if df.empty:
        logger.warning("No valid data after processing. Exiting.")
        return
    
    # Save
    logger.info("Saving results")
    try:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # JSON with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = config.DATA_DIR / f"results_{timestamp}.json"
        
        df.to_json(json_file, orient='records', indent=2, date_format='iso')
        logger.info(f"Results saved to {json_file}")
        
        # Also save to main results.json
        df.to_json(config.RESULTS_FILE, orient='records', indent=2, date_format='iso')
    except Exception as e:
        logger.error(f"Failed to save results: {e}", exc_info=True)
        return
    
    # Print summary
    print_summary(df)


def print_summary(df):
    """Print summary statistics."""
    if df.empty:
        logger.warning("Cannot print summary: empty DataFrame")
        return
    
    print("\n" + "="*60)
    print("📊 REVOLICO DEALS FINDER - SUMMARY".center(60))
    print("="*60)
    
    avg_price = df['price_usd'].mean()
    median_price = df['price_usd'].median()
    min_price = df['price_usd'].min()
    max_price = df['price_usd'].max()
    std_price = df['price_usd'].std()
    
    total_ads = len(df)
    deals = (df['label'] == '🔥 GANGA').sum()
    scams = (df['label'] == '⚠️ POSIBLE ESTAFA').sum()
    normal = (df['label'] == '✅ MERCADO').sum()
    
    print(f"\n💰 PRICE STATISTICS (USD)")
    print(f"   Average:        ${avg_price:>10.2f}")
    print(f"   Median:         ${median_price:>10.2f}")
    print(f"   Min:            ${min_price:>10.2f}")
    print(f"   Max:            ${max_price:>10.2f}")
    print(f"   Std Dev:        ${std_price:>10.2f}")
    
    print(f"\n📈 LISTINGS BREAKDOWN")
    print(f"   Total:          {total_ads:>10}")
    print(f"   🔥 Deals:       {deals:>10} ({deals/total_ads*100:>5.1f}%)")
    print(f"   ⚠️  Scams:      {scams:>10} ({scams/total_ads*100:>5.1f}%)")
    print(f"   ✅ Normal:      {normal:>10} ({normal/total_ads*100:>5.1f}%)")
    
    # Top 5 deals
    if deals > 0:
        print(f"\n🏆 TOP 5 DEALS")
        deals_df = df[df['label'] == '🔥 GANGA'].nsmallest(5, 'price_usd')
        for idx, (_, row) in enumerate(deals_df.iterrows(), 1):
            print(f"   {idx}. {row['titulo'][:40]:<40} ${row['price_usd']:>8.2f}")
    
    print(f"\n💾 Results saved to {config.RESULTS_FILE}")
    print("="*60 + "\n")


if __name__ == "__main__":
    import sys
    
    query = sys.argv[1] if len(sys.argv) > 1 else config.DEFAULT_SEARCH_QUERY
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    use_mock = "--mock" in sys.argv
    
    asyncio.run(main(query, max_pages=max_pages, use_mock=use_mock))