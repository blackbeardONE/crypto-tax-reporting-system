import requests
import logging
from datetime import datetime

logger = logging.getLogger('terminusa_logger')

ETHERSCAN_API_URL = "https://api.etherscan.io/api"

def fetch_eth_transactions(address, api_key):
    """
    Fetch Ethereum transactions for a given address using Etherscan API.
    
    Args:
        address (str): Ethereum wallet address
        api_key (str): Etherscan API key
    
    Returns:
        list of dict: List of transactions in system format:
            - exchange: 'Etherscan'
            - timestamp: datetime
            - type: 'buy' or 'sell' (based on whether address is sender or receiver)
            - asset: 'ETH'
            - amount: float
            - price: float (price per ETH in USD at transaction time, set to None here)
            - fee: float (gas used * gas price in ETH, converted to USD if possible, else None)
    """
    logger.info(f"Fetching Ethereum transactions for address {address} from Etherscan...")
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": api_key
    }
    try:
        response = requests.get(ETHERSCAN_API_URL, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data["status"] != "1":
                logger.warning(f"No transactions found or error: {data.get('message')}")
                return []
            txs = data["result"]
            transactions = []
            for tx in txs:
                timestamp = datetime.fromtimestamp(int(tx["timeStamp"]))
                from_addr = tx["from"].lower()
                to_addr = tx["to"].lower() if tx["to"] else None
                value_eth = int(tx["value"]) / 1e18
                gas_used = int(tx["gasUsed"])
                gas_price = int(tx["gasPrice"]) / 1e18
                fee_eth = gas_used * gas_price
                # Determine type
                if from_addr == address.lower():
                    tx_type = "sell"
                    amount = value_eth
                elif to_addr == address.lower():
                    tx_type = "buy"
                    amount = value_eth
                else:
                    continue  # Skip irrelevant tx
                transactions.append({
                    "exchange": "Etherscan",
                    "timestamp": timestamp,
                    "type": tx_type,
                    "asset": "ETH",
                    "amount": amount,
                    "price": None,  # Price fetching can be added later
                    "fee": None  # Fee conversion to USD can be added later
                })
            logger.info(f"Fetched {len(transactions)} Ethereum transactions.")
            return transactions
        else:
            logger.error(f"Error fetching transactions: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"Exception fetching Ethereum transactions: {e}")
        return []
