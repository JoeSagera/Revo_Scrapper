import pandas as pd
import numpy as np

CUP_TO_USD_RATE = 350  # 1 USD = 350 CUP

def process_data(data: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(data)
    
    # Normalize prices: already floats, but ensure
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    # Convert to USD
    df['price_usd'] = df.apply(lambda row: row['price'] / CUP_TO_USD_RATE if row['currency'] == 'CUP' else row['price'], axis=1)
    
    # Calculate mean and std dev
    mean_price = df['price_usd'].mean()
    std_price = df['price_usd'].std()
    
    # Flag deals and scams
    df['is_deal'] = df['price_usd'] < (mean_price - std_price)
    df['is_scam'] = df['price_usd'] < (mean_price * 0.4)
    
    return df

if __name__ == "__main__":
    # Test
    sample_data = [
        {'title': 'Car 1', 'price': 150.0, 'currency': 'USD', 'url': 'http://example.com'},
        {'title': 'Car 2', 'price': 40000.0, 'currency': 'CUP', 'url': 'http://example.com'},
        {'title': 'Car 3', 'price': 200.0, 'currency': 'USD', 'url': 'http://example.com'}
    ]
    df = process_data(sample_data)
    print(df)