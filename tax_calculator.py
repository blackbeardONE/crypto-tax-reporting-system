import logging
from datetime import datetime
from price_api import get_historical_price

logger = logging.getLogger('terminusa_logger')

def calculate_gains_losses(transactions):
    """
    Calculate gains and losses from a list of transactions.
    
    Args:
        transactions (list of dict): Each dict contains keys:
            - type: 'buy' or 'sell'
            - asset: cryptocurrency symbol, e.g., 'BTC', 'ETH'
            - amount: float
            - price: float or None (price per unit in USD)
            - timestamp: datetime
    
    Returns:
        list of dict: Each dict includes original transaction data plus:
            - gain_loss: float, gain or loss in USD for sell transactions
    """
    results = []
    holdings = {}

    for tx in transactions:
        tx_type = tx.get("type")
        asset = tx.get("asset")
        amount = tx.get("amount")
        price = tx.get("price")
        timestamp = tx.get("timestamp")

        # If price is None, fetch historical price
        if price is None and timestamp is not None:
            date = timestamp.date()
            # Map asset symbol to CoinGecko id
            asset_map = {
                "BTC": "bitcoin",
                "ETH": "ethereum",
                # Add more mappings as needed
            }
            asset_id = asset_map.get(asset.upper())
            if asset_id:
                price = get_historical_price(asset_id, date)
            else:
                logger.warning(f"No price mapping found for asset {asset}")
                price = 0.0

        if price is None:
            price = 0.0

        if tx_type == "buy":
            # Add to holdings
            if asset not in holdings:
                holdings[asset] = []
            holdings[asset].append({"amount": amount, "price": price})
            results.append({**tx, "gain_loss": 0.0})
            logger.debug(f"Bought {amount} {asset} at {price} USD")
        elif tx_type == "sell":
            # Calculate gain/loss using FIFO
            gain_loss = 0.0
            amount_to_sell = amount
            if asset in holdings:
                while amount_to_sell > 0 and holdings[asset]:
                    lot = holdings[asset][0]
                    lot_amount = lot["amount"]
                    lot_price = lot["price"]
                    if lot_amount <= amount_to_sell:
                        gain_loss += lot_amount * (price - lot_price)
                        amount_to_sell -= lot_amount
                        holdings[asset].pop(0)
                    else:
                        gain_loss += amount_to_sell * (price - lot_price)
                        lot["amount"] -= amount_to_sell
                        amount_to_sell = 0
                if amount_to_sell > 0:
                    logger.warning(f"Sold more {asset} than held. Remaining amount: {amount_to_sell}")
            else:
                logger.warning(f"No holdings found for asset {asset} when selling.")
            results.append({**tx, "gain_loss": gain_loss})
            logger.debug(f"Sold {amount} {asset} at {price} USD, Gain/Loss: {gain_loss}")
        else:
            results.append({**tx, "gain_loss": 0.0})
            logger.warning(f"Unknown transaction type: {tx_type}")

    return results
