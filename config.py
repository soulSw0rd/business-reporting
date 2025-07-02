# Configuration de l'application CryptoTrader Dashboard

# API Settings
API_BASE_URL = "http://127.0.0.1:8000"
API_TIMEOUT = 10

# Data Settings
DATA_FOLDER = "data/processed"
CACHE_TTL = 300  # 5 minutes

# Streamlit Settings
PAGE_TITLE = "CryptoTrader Dashboard"
PAGE_ICON = "₿"
LAYOUT = "wide"

# Crypto Settings
DEFAULT_CRYPTOS = ["BTC", "ETH", "ADA", "SOL", "DOT"]
MAX_CRYPTOS_DISPLAY = 10

# Trading Settings
DEFAULT_PORTFOLIO_VALUE = 10000
REBALANCE_OPTIONS = ["Jamais", "Mensuel", "Trimestriel", "Annuel"]

# API Endpoints
ENDPOINTS = {
    "health": "/health",
    "top_traders": "/top-traders",
    "market_data": "/market",
    "scrape_trigger": "/scrape"
}

# Colors for styling
COLORS = {
    "positive": "#00d4aa",
    "negative": "#ff6b6b", 
    "neutral": "#ffd93d",
    "primary": "#FFD700",
    "background": "#f0f2f6"
}
