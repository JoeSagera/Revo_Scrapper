"""Data processing and analysis for Revolico listings."""
import pandas as pd
import numpy as np
import re
from logger import get_logger
import config

logger = get_logger(__name__)


class DataProcessor:
    """Process and analyze Revolico listing data."""
    
    def __init__(self, exchange_rate: dict = None):
        """
        Initialize the data processor.
        
        Args:
            exchange_rate: Dictionary of currency rates (default: config.EXCHANGE_RATES)
        """
        self.exchange_rate = exchange_rate or config.EXCHANGE_RATES
        logger.info(f"Initialized DataProcessor with rates: {self.exchange_rate}")

    def clean_price(self, price_str: str) -> tuple:
        """
        Clean and extract price and currency from a raw price string.
        
        Args:
            price_str: Raw price string (e.g., "150 USD", "40.000 CUP")
            
        Returns:
            Tuple of (price_float, currency_string)
        """
        if not price_str or not isinstance(price_str, str):
            return None, None
        
        original = price_str
        currency = None
        
        # Detect currency
        for curr in ['USD', 'CUP', 'MLC']:
            if curr in price_str:
                currency = curr
                break
        
        if not currency:
            logger.debug(f"No currency detected in: {price_str}")
            return None, None
        
        # Remove currency words and extra whitespace
        price_str = re.sub(r'\bUSD\b|\bCUP\b|\bMLC\b', '', price_str).strip()
        
        # Handle separators: dots as thousands, commas as decimals (European style)
        # But also handle US style: dots as thousands, no decimal
        if ',' in price_str and '.' in price_str:
            # European style: 1.234,56
            price_str = price_str.replace('.', '').replace(',', '.')
        elif ',' in price_str:
            # Comma only: treat as decimal
            price_str = price_str.replace(',', '.')
        else:
            # Dots only: remove (they're thousands separators)
            price_str = price_str.replace('.', '')
        
        # Remove non-numeric characters except decimal point
        price_str = re.sub(r'[^\d.]', '', price_str)
        
        try:
            price = float(price_str)
            
            # Validate price range
            if price < config.MIN_PRICE or price > config.MAX_PRICE:
                logger.warning(f"Price {price} outside valid range [{config.MIN_PRICE}, {config.MAX_PRICE}]")
                return None, currency
            
            return price, currency
        except ValueError as e:
            logger.warning(f"Could not parse price from '{original}': {e}")
            return None, None

    def process_data(self, data: list[dict]) -> pd.DataFrame:
        """
        Process raw listing data into analyzed DataFrame.
        
        Args:
            data: List of listing dictionaries
            
        Returns:
            Processed DataFrame with price analysis and labels
        """
        if not data:
            logger.warning("No data to process. Returning empty DataFrame.")
            return pd.DataFrame(columns=[
                'titulo', 'precio_raw', 'precio_limpio', 'currency', 'price_usd', 'label', 'url'
            ])
        
        logger.info(f"Processing {len(data)} listings")
        df = pd.DataFrame(data)
        
        # Validate required columns
        if 'precio_raw' not in df.columns:
            logger.error(f"Missing 'precio_raw' column. Available: {df.columns.tolist()}")
            return pd.DataFrame(columns=[
                'titulo', 'precio_raw', 'precio_limpio', 'currency', 'price_usd', 'label', 'url'
            ])
        
        # Clean prices
        df[['precio_limpio', 'currency']] = df['precio_raw'].apply(self.clean_price).apply(pd.Series)
        
        # Convert to numeric
        df['precio_limpio'] = pd.to_numeric(df['precio_limpio'], errors='coerce')
        
        # Filter out rows without valid prices
        initial_count = len(df)
        df = df.dropna(subset=['precio_limpio'])
        removed = initial_count - len(df)
        if removed > 0:
            logger.info(f"Removed {removed} listings with invalid prices")
        
        if df.empty:
            logger.warning("No valid prices found after cleaning.")
            return pd.DataFrame(columns=[
                'titulo', 'precio_raw', 'precio_limpio', 'currency', 'price_usd', 'label', 'url'
            ])
        
        # Convert to USD
        df['price_usd'] = df.apply(
            lambda row: row['precio_limpio'] / self.exchange_rate.get(row['currency'], 1)
            if row['currency'] in self.exchange_rate else row['precio_limpio'],
            axis=1
        )
        
        # Filter by price range in USD
        df = df[(df['price_usd'] >= config.MIN_PRICE) & (df['price_usd'] <= config.MAX_PRICE)]
        
        if df.empty:
            logger.warning("No listings within valid price range.")
            return pd.DataFrame(columns=[
                'titulo', 'precio_raw', 'precio_limpio', 'currency', 'price_usd', 'label', 'url'
            ])
        
        # Calculate statistics
        mean_price = df['price_usd'].mean()
        std_price = df['price_usd'].std()
        
        logger.info(f"Price Statistics: Mean=${mean_price:.2f}, Std=${std_price:.2f}")
        
        # Assign labels based on thresholds
        def get_label(price_usd):
            if pd.isna(price_usd):
                return '✅ MERCADO'
            deal_threshold = mean_price - config.DEAL_THRESHOLD * std_price
            scam_threshold = mean_price * config.SCAM_THRESHOLD
            
            if price_usd < deal_threshold:
                return '🔥 GANGA'
            elif price_usd < scam_threshold:
                return '⚠️ POSIBLE ESTAFA'
            else:
                return '✅ MERCADO'
        
        df['label'] = df['price_usd'].apply(get_label)
        
        # Log summary
        deals = (df['label'] == '🔥 GANGA').sum()
        scams = (df['label'] == '⚠️ POSIBLE ESTAFA').sum()
        normal = (df['label'] == '✅ MERCADO').sum()
        logger.info(f"Labels: {deals} gangas, {scams} estafas, {normal} normales")
        
        # Select and order columns
        df = df[['titulo', 'precio_raw', 'precio_limpio', 'currency', 'price_usd', 'label', 'url']]
        
        return df


if __name__ == "__main__":
    # Test
    sample_data = [
        {'titulo': 'Car 1', 'precio_raw': '150 USD', 'url': 'http://example.com'},
        {'titulo': 'Car 2', 'precio_raw': '40.000 CUP', 'url': 'http://example.com'},
        {'titulo': 'Car 3', 'precio_raw': '200 USD', 'url': 'http://example.com'}
    ]
    processor = DataProcessor()
    df = processor.process_data(sample_data)
    print(df)