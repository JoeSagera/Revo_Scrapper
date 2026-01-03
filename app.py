"""Advanced Streamlit UI for Revolico Deals Finder."""
import streamlit as st
import pandas as pd
import numpy as np
from src.processor import DataProcessor
from src.scraper import scrape_revolico
import config
from logger import get_logger

logger = get_logger(__name__)


def setup_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="🔥 Revolico Deals Finder",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main {
            padding-top: 2rem;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
        }
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 16px;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)


def render_advanced_sidebar():
    """Render advanced sidebar with organized settings."""
    with st.sidebar:
        # Logo and title
        st.markdown("## 🔥 **REVOLICO DEALS**")
        st.markdown("*Find the best deals. Avoid scams.*")
        st.divider()
        
        # Main search section
        st.markdown("### 🔍 Search Settings")
        query = st.text_input(
            "What are you looking for?",
            value="car",
            placeholder="e.g., car, motorcycle, house",
            help="Enter your search query"
        )
        
        max_pages = st.slider(
            "Pages to scrape",
            min_value=1,
            max_value=5,
            value=1,
            help="More pages = longer scraping"
        )
        
        # Advanced filters
        st.markdown("### 🎯 Price Filters")
        
        col1, col2 = st.columns(2)
        with col1:
            min_price = st.number_input(
                "Min Price (USD)",
                value=float(config.MIN_PRICE),
                min_value=0.0,
                step=10.0
            )
        with col2:
            max_price = st.number_input(
                "Max Price (USD)",
                value=float(config.MAX_PRICE),
                min_value=100.0,
                step=1000.0
            )
        
        # Deal detection settings
        st.markdown("### 💡 Deal Detection")
        
        deal_threshold = st.slider(
            "Ganga Sensitivity",
            min_value=0.5,
            max_value=3.0,
            value=config.DEAL_THRESHOLD,
            step=0.1,
            help="Lower = more deals detected"
        )
        
        scam_threshold = st.slider(
            "Scam Sensitivity",
            min_value=0.1,
            max_value=0.8,
            value=config.SCAM_THRESHOLD,
            step=0.05,
            help="Lower = more scams detected"
        )
        
        # Currency settings
        st.markdown("### 💱 Exchange Rate")
        exchange_rate = st.number_input(
            "CUP to USD Rate",
            value=float(config.EXCHANGE_RATES["CUP"]),
            min_value=1.0,
            step=10.0,
            help="1 USD = ? CUP"
        )
        
        st.divider()
        
        # Test/Mock mode
        st.markdown("### 🧪 Test Mode")
        use_mock_data = st.checkbox(
            "Use Mock Data (for testing)",
            value=False,
            help="Use sample data instead of scraping. Useful when Cloudflare blocks."
        )
        
        # Advanced options
        if st.checkbox("⚙️ Advanced Options", value=False):
            st.markdown("### Debug Settings")
            log_level = st.selectbox("Log Level", ["INFO", "DEBUG", "WARNING"])
        else:
            log_level = "INFO"
        
        return {
            "query": query,
            "max_pages": max_pages,
            "min_price": min_price,
            "max_price": max_price,
            "deal_threshold": deal_threshold,
            "scam_threshold": scam_threshold,
            "exchange_rate": exchange_rate,
            "log_level": log_level,
            "use_mock_data": use_mock_data
        }


def render_header():
    """Render impressive header."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
            # 🔥 Revolico Deals Finder
            ### Find the best deals. Avoid scams.
            *Scrape, analyze, and profit from Revolico listings*
            """)
    
    with col2:
        st.metric("Status", "Ready ✅", delta="Online")


def render_search_and_actions(settings):
    """Render search bar with action buttons."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        scrape_button = st.button(
            "🚀 Scrape & Analyze",
            use_container_width=False,
            type="primary"
        )
    
    with col2:
        if st.button("💾 Export Results", use_container_width=False):
            if 'df_results' in st.session_state and not st.session_state.df_results.empty:
                csv = st.session_state.df_results.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    f"revolico_{settings['query']}.csv",
                    "text/csv",
                    use_container_width=False
                )
            else:
                st.warning("No results to export")
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=False):
            if 'df_results' in st.session_state:
                st.rerun()
    
    with col4:
        if st.button("🗑️ Clear All", use_container_width=False):
            if 'df_results' in st.session_state:
                del st.session_state.df_results
            st.rerun()
    
    return scrape_button


def render_summary_section(df):
    """Render enhanced summary with KPIs."""
    if df.empty:
        st.info("📊 Run a search to see statistics")
        return
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    try:
        avg_price = df['price_usd'].mean()
        median_price = df['price_usd'].median()
        total_ads = len(df)
        num_deals = (df['label'] == '🔥 GANGA').sum()
        num_scams = (df['label'] == '⚠️ POSIBLE ESTAFA').sum()
        
        with col1:
            st.metric(
                "💰 Average",
                f"${avg_price:.2f}",
                delta=f"±${df['price_usd'].std():.2f}"
            )
        
        with col2:
            st.metric(
                "📊 Median",
                f"${median_price:.2f}",
                delta=f"{(num_deals/total_ads*100):.1f}% deals"
            )
        
        with col3:
            st.metric(
                "📋 Total",
                total_ads,
                delta="listings"
            )
        
        with col4:
            st.metric(
                "🔥 Gangas",
                num_deals,
                delta=f"{(num_deals/total_ads*100):.1f}%"
            )
        
        with col5:
            st.metric(
                "⚠️ Scams",
                num_scams,
                delta=f"{(num_scams/total_ads*100):.1f}%"
            )
    except Exception as e:
        st.error(f"Error rendering summary: {e}")


def render_advanced_filters(df):
    """Render advanced filtering options."""
    if df.empty:
        return df
    
    st.markdown("### 🔎 Advanced Filters")
    
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        label_filter = st.multiselect(
            "Filter by Label",
            options=df['label'].unique(),
            default=df['label'].unique(),
            help="Filter listings by their classification"
        )
    
    with filter_col2:
        currency_filter = st.multiselect(
            "Filter by Currency",
            options=df['currency'].unique() if 'currency' in df.columns else ['USD'],
            default=df['currency'].unique() if 'currency' in df.columns else ['USD'],
            help="Filter by original currency"
        )
    
    with filter_col3:
        price_range = st.slider(
            "Price Range (USD)",
            min_value=float(df['price_usd'].min()),
            max_value=float(df['price_usd'].max()),
            value=(float(df['price_usd'].min()), float(df['price_usd'].max())),
            step=10.0
        )
    
    with filter_col4:
        sort_option = st.selectbox(
            "Sort by",
            ["Price (Low to High)", "Price (High to Low)", "Title (A-Z)", "By Label"]
        )
    
    # Apply filters
    filtered_df = df[df['label'].isin(label_filter)]
    filtered_df = filtered_df[filtered_df['currency'].isin(currency_filter)] if 'currency' in filtered_df.columns else filtered_df
    filtered_df = filtered_df[
        (filtered_df['price_usd'] >= price_range[0]) & 
        (filtered_df['price_usd'] <= price_range[1])
    ]
    
    # Apply sorting
    if sort_option == "Price (Low to High)":
        filtered_df = filtered_df.sort_values('price_usd')
    elif sort_option == "Price (High to Low)":
        filtered_df = filtered_df.sort_values('price_usd', ascending=False)
    elif sort_option == "Title (A-Z)":
        filtered_df = filtered_df.sort_values('titulo')
    else:  # By Label
        label_order = {'🔥 GANGA': 0, '⚠️ POSIBLE ESTAFA': 1, '✅ MERCADO': 2}
        filtered_df['label_order'] = filtered_df['label'].map(label_order)
        filtered_df = filtered_df.sort_values('label_order').drop('label_order', axis=1)
    
    return filtered_df


def render_results_table(df):
    """Render beautiful results table with styling."""
    if df.empty:
        st.info("📊 No results to display")
        return
    
    st.markdown("### 📋 Results Table")
    
    # Prepare display dataframe
    display_df = df.copy()
    display_df['Price'] = display_df['price_usd'].apply(lambda x: f"${x:.2f}")
    display_df['Title'] = display_df['titulo'].apply(lambda x: x[:50] + "..." if len(x) > 50 else x)
    
    # Select columns to display
    display_cols = ['Title', 'Price', 'currency', 'label']
    display_data = display_df[display_cols].copy()
    
    # Display with styling
    st.dataframe(
        display_data,
        use_container_width=False,
        height=500,
        column_config={
            "Title": st.column_config.TextColumn(width="large"),
            "Price": st.column_config.TextColumn(width="small"),
            "currency": st.column_config.TextColumn(width="small"),
            "label": st.column_config.TextColumn(width="medium")
        }
    )
    
    # Show more details on expand
    with st.expander("📍 Show Full Listings"):
        st.dataframe(df, use_container_width=False, height=400)


def render_analytics(df):
    """Render analytics and charts."""
    if df.empty:
        return
    
    st.markdown("### 📈 Analytics & Charts")
    
    tab1, tab2, tab3 = st.tabs(["📊 Distribution", "💹 Price Trends", "🏷️ Categories"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            label_counts = df['label'].value_counts()
            st.bar_chart(label_counts)
        with col2:
            currency_counts = df['currency'].value_counts() if 'currency' in df.columns else pd.Series()
            if not currency_counts.empty:
                st.bar_chart(currency_counts)
    
    with tab2:
        sorted_prices = df['price_usd'].sort_values().reset_index(drop=True)
        st.line_chart(sorted_prices, height=400)
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Min Price", f"${df['price_usd'].min():.2f}")
        with col2:
            st.metric("Max Price", f"${df['price_usd'].max():.2f}")
        
        st.markdown("**Top 5 Best Deals:**")
        deals_df = df[df['label'] == '🔥 GANGA'].nsmallest(5, 'price_usd')[['titulo', 'price_usd', 'label']]
        for idx, (_, row) in enumerate(deals_df.iterrows(), 1):
            st.write(f"{idx}. {row['titulo'][:60]} - **${row['price_usd']:.2f}**")


def main():
    """Main application function."""
    setup_page()
    
    # Sidebar with settings
    settings = render_advanced_sidebar()
    
    # Main content area
    render_header()
    st.divider()
    
    # Search and action buttons
    scrape_button = render_search_and_actions(settings)
    
    # Perform scraping if button clicked
    if scrape_button:
        # Check if user wants mock data
        if settings.get('use_mock_data', False):
            st.info("📊 Loading mock data for testing...")
            from src.processor import get_mock_listings
            data = get_mock_listings(count=20)
            st.success(f"✅ Loaded {len(data)} mock listings")
        else:
            with st.spinner("🌐 Scraping Revolico..."):
                data = None
                error_occurred = False
                
                try:
                    logger.info(f"Scraping real data for: {settings['query']}")
                data = scrape_revolico(settings['query'], max_pages=settings['max_pages'])
                logger.info(f"Got {len(data) if data else 0} listings")
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Scraping error: {error_msg}", exc_info=True)
                
                st.error(f"❌ Scraping failed")
                st.warning(f"**Error Details:**\n\n{error_msg}")
                st.info("**Solution:**\n\n"
                       "This is a known issue with Python 3.14 and Cloudflare protection.\n\n"
                       "**Options:**\n"
                       "1. **Downgrade Python** to 3.13 or earlier\n"
                       "2. **Use Mock Data** - Switch to test mode in sidebar\n"
                       "3. **Use a Proxy API** - Services like ScraperAPI can bypass Cloudflare\n\n"
                       "⚠️ Real-time scraping requires either:\n"
                       "- Python < 3.14 (to use browser automation)\n"
                       "- A paid Cloudflare bypass service")
                error_occurred = True
                
                # Offer alternative: use mock data
                st.divider()
                st.markdown("### 🔄 Alternative: Test with Mock Data")
                if st.button("Switch to Mock Data Mode"):
                    st.info("Set 'Use Mock Data' toggle in the sidebar to enable test mode")
                return
        
        if not data:
            st.warning("⚠️ No listings found. Try a different search term.")
            return
        
        # Process data
        with st.spinner("⚙️ Processing data..."):
            try:
                processor = DataProcessor(
                    exchange_rate={'CUP': settings['exchange_rate'], 'USD': 1, 'MLC': 1}
                )
                df_results = processor.process_data(data)
                
                st.session_state.df_results = df_results
                st.success(f"✅ Processed {len(df_results)} listings")
                logger.info(f"Processed {len(df_results)} valid listings")
            except Exception as e:
                st.error(f"❌ Processing error: {e}")
                logger.error(f"Processing error: {e}", exc_info=True)
                return
    
    # Display results if available
    if 'df_results' in st.session_state and not st.session_state.df_results.empty:
        st.divider()
        
        # Summary section
        render_summary_section(st.session_state.df_results)
        
        st.divider()
        
        # Advanced filters
        filtered_df = render_advanced_filters(st.session_state.df_results)
        
        st.divider()
        
        # Results table
        render_results_table(filtered_df)
        
        st.divider()
        
        # Analytics
        render_analytics(st.session_state.df_results)


if __name__ == "__main__":
    main()