import streamlit as st
import pandas as pd
from src.processor import DataProcessor
from src.scraper import scrape_revolico
import asyncio

def main():
    st.title("Revolico Deals Finder")

    # Sidebar for exchange rate
    exchange_rate = st.sidebar.number_input("Exchange Rate (CUP to USD)", value=350, min_value=1)

    query = st.text_input("Search Query", "car")

    if st.button("Scrape & Analyze"):
        with st.spinner("Scraping..."):
            data = asyncio.run(scrape_revolico(query))
        
        with st.spinner("Processing..."):
            processor = DataProcessor(exchange_rate=exchange_rate)
            df = processor.process_data(data)
        
        # Summary Card
        avg_price = df['price_usd'].mean()
        total_ads = len(df)
        num_deals = (df['label'] == '🔥 GANGA').sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Price (USD)", f"{avg_price:.2f}")
        with col2:
            st.metric("Total Ads Found", total_ads)
        with col3:
            st.metric("Number of Deals", num_deals)
        
        # Highlighting function
        def highlight(row):
            if row['label'] == '🔥 GANGA':
                return ['background-color: green'] * len(row)
            elif row['label'] == '⚠️ POSIBLE ESTAFA':
                return ['background-color: red'] * len(row)
            else:
                return [''] * len(row)
        
        st.dataframe(df.style.apply(highlight, axis=1))

if __name__ == "__main__":
    main()