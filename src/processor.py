import pandas as pd
import numpy as np
import re

class DataProcessor:
    def __init__(self, exchange_rate=350):
        self.exchange_rate = exchange_rate

    def clean_price(self, price_str):
        if not price_str:
            return None, None
        currency = None
        if 'USD' in price_str:
            currency = 'USD'
        elif 'CUP' in price_str:
            currency = 'CUP'
        elif 'MLC' in price_str:
            currency = 'MLC'
        # Remove currency words
        price_str = re.sub(r'\bUSD\b|\bCUP\b|\bMLC\b', '', price_str).strip()
        # Handle separators: if comma present, treat as decimal, else dots as thousands
        if ',' in price_str:
            price_str = price_str.replace('.', '').replace(',', '.')
        else:
            price_str = price_str.replace('.', '')
        try:
            price = float(price_str)
            return price, currency
        except ValueError:
            return None, None

    def process_data(self, data: list[dict]) -> pd.DataFrame:
        df = pd.DataFrame(data)
        # Clean price
        df[['precio_limpio', 'currency']] = df['precio_raw'].apply(self.clean_price).apply(pd.Series)
        # Convert to USD
        df['price_usd'] = df.apply(lambda row: row['precio_limpio'] / self.exchange_rate if row['currency'] == 'CUP' else row['precio_limpio'], axis=1)
        # Statistics
        mean_price = df['price_usd'].mean()
        std_price = df['price_usd'].std()
        # Label
        def get_label(price_usd):
            if price_usd < (mean_price - 1.5 * std_price):
                return '🔥 GANGA'
            elif price_usd < (mean_price * 0.4):
                return '⚠️ POSIBLE ESTAFA'
            else:
                return '✅ MERCADO'
        df['label'] = df['price_usd'].apply(get_label)
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