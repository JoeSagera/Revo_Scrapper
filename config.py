"""Configuration settings for Revolico scraper."""
import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = PROJECT_ROOT / "logs" / "scraper.log"

# Scraper settings
REVOLICO_BASE_URL = "https://www.revolico.com"
REVOLICO_SEARCH_URL = f"{REVOLICO_BASE_URL}/search.html"
DEFAULT_SEARCH_QUERY = "car"
SCRAPER_TIMEOUT = 30000  # milliseconds
SCRAPER_HEADLESS = True
REQUEST_DELAY_MIN = 2  # seconds
REQUEST_DELAY_MAX = 5  # seconds
USER_AGENT_ROTATION = True

# Price processing
EXCHANGE_RATES = {
    "CUP": 350,  # 1 USD = 350 CUP
    "USD": 1,
    "MLC": 1,   # Assume MLC = USD for now
}
MIN_PRICE = 0.1  # Filter out prices below this
MAX_PRICE = 1000000  # Filter out prices above this

# Deal detection thresholds
DEAL_THRESHOLD = 1.5  # 1.5 * std below mean = deal
SCAM_THRESHOLD = 0.4  # 40% of mean or lower = scam

# Data storage
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_FILE = DATA_DIR / "results.json"
CACHE_DIR = PROJECT_ROOT / ".cache"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
LOG_FILE.parent.mkdir(exist_ok=True)

# Streamlit settings
STREAMLIT_PAGE_WIDTH = "wide"
STREAMLIT_THEME = "light"
STREAMLIT_MAX_ITEMS_DISPLAY = 100
