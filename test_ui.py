"""Comprehensive UI and feature tests for the improved Streamlit app."""
import sys
import pandas as pd
from src.processor import DataProcessor
from src.scraper import scrape_revolico
import asyncio
import config
from logger import get_logger

logger = get_logger(__name__)


def test_mock_data_processing():
    """Test processing mock data with new UI features."""
    print("\n" + "="*60)
    print("TEST 1: Mock Data Processing")
    print("="*60)
    
    mock_data = [
        {'titulo': 'Audi A4 2020', 'precio_raw': '12.000 USD', 'url': 'http://example.com/1'},
        {'titulo': 'BMW X5 2019', 'precio_raw': '15.000 USD', 'url': 'http://example.com/2'},
        {'titulo': 'Toyota Camry 2018', 'precio_raw': '8.500 USD', 'url': 'http://example.com/3'},
        {'titulo': 'Honda Civic 2017', 'precio_raw': '6.500 USD', 'url': 'http://example.com/4'},
        {'titulo': 'Mazda CX-5 2019', 'precio_raw': '9.500 USD', 'url': 'http://example.com/5'},
    ]
    
    try:
        processor = DataProcessor(
            exchange_rate={'CUP': 350, 'USD': 1, 'MLC': 1}
        )
        df = processor.process_data(mock_data)
        
        print(f"✅ Processed {len(df)} listings")
        print(f"✅ Columns: {list(df.columns)}")
        print(f"✅ Average price: ${df['price_usd'].mean():.2f}")
        print(f"✅ Median price: ${df['price_usd'].median():.2f}")
        print(f"✅ Labels detected: {df['label'].unique().tolist()}")
        
        assert len(df) == 5, "Should process 5 listings"
        assert 'price_usd' in df.columns, "Should have price_usd column"
        assert 'label' in df.columns, "Should have label column"
        assert not df['price_usd'].isna().any(), "No NaN prices allowed"
        
        print("✅ TEST PASSED")
        return True
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


def test_advanced_filtering():
    """Test advanced filtering functionality."""
    print("\n" + "="*60)
    print("TEST 2: Advanced Filtering")
    print("="*60)
    
    mock_data = [
        {'titulo': 'Cheap Car', 'precio_raw': '3.000 USD', 'url': 'http://example.com/1'},
        {'titulo': 'Normal Car', 'precio_raw': '10.000 USD', 'url': 'http://example.com/2'},
        {'titulo': 'Expensive Car', 'precio_raw': '50.000 USD', 'url': 'http://example.com/3'},
        {'titulo': 'Another Car', 'precio_raw': '8.000 USD', 'url': 'http://example.com/4'},
        {'titulo': 'Luxury Car', 'precio_raw': '100.000 USD', 'url': 'http://example.com/5'},
    ]
    
    try:
        processor = DataProcessor(exchange_rate={'CUP': 350, 'USD': 1, 'MLC': 1})
        df = processor.process_data(mock_data)
        
        # Test 1: Filter by price range
        df_filtered = df[(df['price_usd'] >= 5000) & (df['price_usd'] <= 15000)]
        print(f"✅ Price range filter: {len(df_filtered)} results (5k-15k)")
        assert len(df_filtered) > 0, "Should have results in price range"
        
        # Test 2: Filter by label
        gangas = df[df['label'] == '🔥 GANGA']
        print(f"✅ Ganga filter: {len(gangas)} deals found")
        
        estafas = df[df['label'] == '⚠️ POSIBLE ESTAFA']
        print(f"✅ Scam filter: {len(estafas)} scams detected")
        
        # Test 3: Multi-filter
        multi_filtered = df[
            (df['price_usd'] >= 5000) & 
            (df['price_usd'] <= 50000) & 
            (df['label'].isin(['🔥 GANGA', '✅ MERCADO']))
        ]
        print(f"✅ Multi-filter: {len(multi_filtered)} results")
        
        # Test 4: Sorting
        df_sorted_asc = df.sort_values('price_usd')
        df_sorted_desc = df.sort_values('price_usd', ascending=False)
        print(f"✅ Sorting ascending: {df_sorted_asc['price_usd'].iloc[0]:.2f} → {df_sorted_asc['price_usd'].iloc[-1]:.2f}")
        print(f"✅ Sorting descending: {df_sorted_desc['price_usd'].iloc[0]:.2f} → {df_sorted_desc['price_usd'].iloc[-1]:.2f}")
        
        print("✅ TEST PASSED")
        return True
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


def test_statistics_calculation():
    """Test statistics and analytics features."""
    print("\n" + "="*60)
    print("TEST 3: Statistics & Analytics")
    print("="*60)
    
    mock_data = [
        {'titulo': 'Item 1', 'precio_raw': '1.000 USD', 'url': 'http://example.com/1'},
        {'titulo': 'Item 2', 'precio_raw': '2.000 USD', 'url': 'http://example.com/2'},
        {'titulo': 'Item 3', 'precio_raw': '3.000 USD', 'url': 'http://example.com/3'},
        {'titulo': 'Item 4', 'precio_raw': '4.000 USD', 'url': 'http://example.com/4'},
        {'titulo': 'Item 5', 'precio_raw': '5.000 USD', 'url': 'http://example.com/5'},
    ]
    
    try:
        processor = DataProcessor(exchange_rate={'CUP': 350, 'USD': 1, 'MLC': 1})
        df = processor.process_data(mock_data)
        
        # Calculate stats
        mean_price = df['price_usd'].mean()
        median_price = df['price_usd'].median()
        std_price = df['price_usd'].std()
        min_price = df['price_usd'].min()
        max_price = df['price_usd'].max()
        
        print(f"✅ Mean price: ${mean_price:.2f}")
        print(f"✅ Median price: ${median_price:.2f}")
        print(f"✅ Std dev: ${std_price:.2f}")
        print(f"✅ Min price: ${min_price:.2f}")
        print(f"✅ Max price: ${max_price:.2f}")
        
        # Count by label
        label_counts = df['label'].value_counts()
        print(f"✅ Label distribution:\n{label_counts}")
        
        # Verify calculations
        assert mean_price > 0, "Mean should be positive"
        assert median_price > 0, "Median should be positive"
        assert std_price >= 0, "Std dev should be non-negative"
        assert min_price <= mean_price <= max_price, "Mean should be between min and max"
        
        print("✅ TEST PASSED")
        return True
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


def test_export_functionality():
    """Test data export features."""
    print("\n" + "="*60)
    print("TEST 4: Export Functionality")
    print("="*60)
    
    mock_data = [
        {'titulo': 'Item 1', 'precio_raw': '1.000 USD', 'url': 'http://example.com/1'},
        {'titulo': 'Item 2', 'precio_raw': '2.000 USD', 'url': 'http://example.com/2'},
        {'titulo': 'Item 3', 'precio_raw': '3.000 USD', 'url': 'http://example.com/3'},
    ]
    
    try:
        processor = DataProcessor(exchange_rate={'CUP': 350, 'USD': 1, 'MLC': 1})
        df = processor.process_data(mock_data)
        
        # Test CSV export
        csv_data = df.to_csv(index=False)
        print(f"✅ CSV export generated: {len(csv_data)} bytes")
        assert len(csv_data) > 0, "CSV should have content"
        assert 'titulo' in csv_data, "CSV should contain title column"
        assert 'price_usd' in csv_data, "CSV should contain price column"
        
        # Test JSON export
        json_data = df.to_json(orient='records')
        print(f"✅ JSON export generated: {len(json_data)} bytes")
        assert len(json_data) > 0, "JSON should have content"
        
        # Test dictionary conversion
        dict_data = df.to_dict('records')
        print(f"✅ Dict conversion: {len(dict_data)} records")
        assert len(dict_data) == 3, "Should have 3 records"
        assert 'titulo' in dict_data[0], "Record should have titulo"
        
        print("✅ TEST PASSED")
        return True
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


def test_ui_components_integration():
    """Test that all UI components work together."""
    print("\n" + "="*60)
    print("TEST 5: UI Components Integration")
    print("="*60)
    
    try:
        # Create sample data
        mock_data = [
            {'titulo': f'Car {i}', 'precio_raw': f'{5000 + i*1000} USD', 'url': f'http://example.com/{i}'}
            for i in range(1, 11)
        ]
        
        processor = DataProcessor(exchange_rate={'CUP': 350, 'USD': 1, 'MLC': 1})
        df = processor.process_data(mock_data)
        
        # Verify all required columns exist
        required_cols = ['titulo', 'price_usd', 'label', 'currency']
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"
            print(f"✅ Column '{col}' present")
        
        # Verify no null values in critical columns
        assert not df['titulo'].isna().any(), "Title cannot be null"
        assert not df['price_usd'].isna().any(), "Price cannot be null"
        assert not df['label'].isna().any(), "Label cannot be null"
        print("✅ No null values in critical columns")
        
        # Verify label values are correct
        valid_labels = {'🔥 GANGA', '⚠️ POSIBLE ESTAFA', '✅ MERCADO'}
        assert df['label'].isin(valid_labels).all(), "Invalid labels found"
        print(f"✅ All labels valid: {df['label'].unique().tolist()}")
        
        # Verify price_usd is numeric
        assert pd.api.types.is_numeric_dtype(df['price_usd']), "price_usd should be numeric"
        print("✅ price_usd is numeric")
        
        # Verify we can perform aggregations
        agg_stats = df.groupby('label')['price_usd'].agg(['mean', 'count', 'min', 'max'])
        print(f"✅ Aggregation works:\n{agg_stats}")
        
        print("✅ TEST PASSED")
        return True
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*60)
    print("🧪 STARTING UI & FEATURE TEST SUITE")
    print("="*60)
    
    tests = [
        test_mock_data_processing,
        test_advanced_filtering,
        test_statistics_calculation,
        test_export_functionality,
        test_ui_components_integration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Unexpected error in {test.__name__}: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! UI is ready for use.")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
