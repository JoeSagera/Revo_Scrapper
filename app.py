import streamlit as st
import pandas as pd
from src.processor import process_data
from src.scraper import scrape_revolico
import asyncio

st.title("Revolico Deals Finder")

query = st.text_input("Search Query", "car")

if st.button("Scrape and Process"):
    with st.spinner("Scraping..."):
        data = asyncio.run(scrape_revolico(query))
    
    with st.spinner("Processing..."):
        df = process_data(data)
    
    # Highlight deals and scams
    def highlight(row):
        if row['is_deal']:
            return ['background-color: green'] * len(row)
        elif row['is_scam']:
            return ['background-color: red'] * len(row)
        else:
            return [''] * len(row)
    
    st.dataframe(df.style.apply(highlight, axis=1))

if __name__ == "__main__":
    main()