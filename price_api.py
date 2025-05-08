import requests
import logging
from datetime import datetime

logger = logging.getLogger('terminusa_logger')

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

def get_historical_price(asset_symbol, date):
    """
    Fetch historical price in USD for a given asset symbol on a specific date.
    
    Args:
        asset_symbol (str): Cryptocurrency symbol, e.g., 'bitcoin', 'ethereum'
        date (datetime.date): Date for which to fetch the price
    
    Returns:
        float or None: Price in USD if found, else None
    """
    logger.info(f"Fetching historical price for {asset_symbol} on {date.isoformat()}")
    try:
        # CoinGecko expects date in dd-mm-yyyy format
        date_str = date.strftime("%d-%m-%Y")
        url = f"{COINGECKO_API_URL}/coins/{asset_symbol}/history"
        params = {"date": date_str, "localization": "false"}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            market_data = data.get("market_data", {})
            current_price = market_data.get("current_price", {})
            price_usd = current_price.get("usd")
            if price_usd:
                logger.info(f"Price for {asset_symbol} on {date_str} is {price_usd} USD")
                return price_usd
            else:
                logger.warning(f"No USD price found for {asset_symbol} on {date_str}")
                return None
        else:
            logger.error(f"Error fetching price: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Exception fetching historical price: {e}")
        return None
