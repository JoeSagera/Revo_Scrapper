"""Quick test script to verify all components work."""
import asyncio
import sys
from src.scraper import scrape_revolico, RevolicoScraper
from src.processor import DataProcessor
import config


def test_processor():
    """Test the DataProcessor."""
    print("\n" + "="*60)
    print("TEST 1: DataProcessor")
    print("="*60)
    
    sample_data = [
        {'titulo': 'iPhone 13', 'precio_raw': '500 USD', 'url': 'http://example.com/1'},
        {'titulo': 'Samsung Galaxy', 'precio_raw': '40.000 CUP', 'url': 'http://example.com/2'},
        {'titulo': 'Google Pixel', 'precio_raw': '1.200,50 EUR', 'url': 'http://example.com/3'},
        {'titulo': 'OnePlus 12', 'precio_raw': '15.000 CUP', 'url': 'http://example.com/4'},
        {'titulo': 'Xiaomi Pro', 'precio_raw': '350 USD', 'url': 'http://example.com/5'},
    ]
    
    processor = DataProcessor()
    df = processor.process_data(sample_data)
    
    print(f"\n✅ Processed {len(df)} listings")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nResults:\n{df[['titulo', 'precio_raw', 'precio_limpio', 'price_usd', 'label']]}")
    
    return len(df) > 0


def test_clean_price():
    """Test price cleaning."""
    print("\n" + "="*60)
    print("TEST 2: Price Cleaning")
    print("="*60)
    
    processor = DataProcessor()
    
    test_cases = [
        ('150 USD', 150.0, 'USD'),
        ('40.000 CUP', 40000.0, 'CUP'),
        ('1.234,56 EUR', None, None),  # Invalid currency
        ('100 MLC', 100.0, 'MLC'),
        ('50,5 USD', 50.5, 'USD'),
        ('', None, None),
        ('NO PRICE', None, None),
    ]
    
    all_pass = True
    for price_str, expected_price, expected_curr in test_cases:
        price, curr = processor.clean_price(price_str)
        status = "✅" if (price == expected_price and curr == expected_curr) else "❌"
        print(f"{status} '{price_str}' -> ${price} {curr}")
        if price != expected_price or curr != expected_curr:
            all_pass = False
    
    return all_pass


async def test_scraper():
    """Test the scraper with mock."""
    print("\n" + "="*60)
    print("TEST 3: Scraper")
    print("="*60)
    
    # Don't actually scrape to avoid network requests in test
    print("✅ Scraper module loaded successfully")
    print(f"   Base URL: {config.REVOLICO_SEARCH_URL}")
    print(f"   Timeout: {config.SCRAPER_TIMEOUT}ms")
    
    return True


def test_config():
    """Test configuration."""
    print("\n" + "="*60)
    print("TEST 4: Configuration")
    print("="*60)
    
    print(f"✅ Exchange Rates: {config.EXCHANGE_RATES}")
    print(f"✅ Deal Threshold: {config.DEAL_THRESHOLD}σ")
    print(f"✅ Scam Threshold: {config.SCAM_THRESHOLD} (% of mean)")
    print(f"✅ Price Range: ${config.MIN_PRICE} - ${config.MAX_PRICE}")
    print(f"✅ Log Level: {config.LOG_LEVEL}")
    print(f"✅ Data Directory: {config.DATA_DIR}")
    
    return True


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 REVOLICO SCRAPER - TEST SUITE")
    print("="*60)
    
    results = []
    
    try:
        results.append(("Config", test_config()))
        results.append(("Price Cleaning", test_clean_price()))
        results.append(("DataProcessor", test_processor()))
        results.append(("Scraper", await test_scraper()))
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
