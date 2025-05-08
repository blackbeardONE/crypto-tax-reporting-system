import os
import sys
import toml
from ethscan_api import fetch_eth_transactions
from logger import setup_logger
from tax_calculator import calculate_gains_losses
from report_generator import generate_csv_report, generate_text_summary
from together_ai import generate_text
from db import init_db

def generate_terminusa_report_with_together_ai(total_gain_loss, gains_losses, api_key, agent_info=None, company_info=None, client_info=None, contact_info=None):
    """
    Generate a tax report template using Together AI.
    
    Args:
        total_gain_loss (float): Total gain or loss amount
        gains_losses (list): List of transactions with gain/loss info
        api_key (str): Together AI API key
        agent_info (dict): Agent information with keys Your_Name, Your_Title, Your_Tax_Firm
        company_info (dict): Company information with key 'name'
        client_info (dict): Client information with key 'full_name'
        contact_info (dict): Contact information with key 'email'
    
    Returns:
        str: Generated tax report text
    """
    system_instruction = (
        "You are a Tax Professional specializing in cryptocurrency and blockchain taxation. "
        "Create a crypto tax report for the client using the data provided. "
        "Include the following information in the report template exactly as given:\n"
        "Company Name: User Company Name\n"
        "Client Full Name: User Full Name\n"
        "Contact Email: support@terminusa.com\n"
        "Agent Name: Terminusa Agent\n"
        "Agent Title: Tax Specialist\n"
        "Agent Tax Firm: Ten Titanics Technologies\n"
        "Strictly follow the template below without deviation:\n\n"
        "=== TEMPLATE START ===\n"
        "Dear {client_name} ({company_name}),\n\n"
        "Total Gain/Loss: {total_gain_loss}\n\n"
        "Transactions:\n"
        "{transactions}\n\n"
        "Sincerely,\n"
        "{agent_name}\n"
        "{agent_title}\n"
        "{agent_firm}\n\n"
        "For questions and other concerns, please contact us at {contact_email}.\n"
        "<Date and Time>\n"
        "=== TEMPLATE END ==="
    )
    greeting = f"Dear {client_info.get('full_name', 'Client')} ({company_info.get('name', 'Company')})"
    contact_line = f"For questions and other concerns, please contact us at {contact_info.get('email', 'support@terminusa.com')}."
    prompt = system_instruction.format(
        client_name=client_info.get('full_name', 'Client'),
        company_name=company_info.get('name', 'Company'),
        total_gain_loss=total_gain_loss,
        transactions=gains_losses,
        agent_name=agent_info.get('Your_Name', 'Terminusa Agent'),
        agent_title=agent_info.get('Your_Title', 'Tax Specialist'),
        agent_firm=agent_info.get('Your_Tax_Firm', 'Ten Titanics Technologies'),
        contact_email=contact_info.get('email', 'support@terminusa.com')
    )
    return generate_text(api_key=api_key, prompt=prompt)

logger = setup_logger()

def main():
    logger.info("Starting Terminusa Crypto Tax Reporting System")
    # Initialize the database tables
    init_db()
    # Load config
    with open("config.toml", "r", encoding="utf-8") as f:
        raw_config = f.read()
    logger.debug(f"Raw config.toml content:\\n{raw_config}")

    config = toml.loads(raw_config)
    logger.info("Loaded configuration from config.toml")
    logger.debug(f"Config api_keys section: {config.get('api_keys')}")

    try:
        user_id = input("Enter user ID to fetch transactions: ")
        # For demonstration, treat user_id as Ethereum address for real fetch
        etherscan_api_key = config.get("api_keys", {}).get("etherscan_api_key")
        together_ai_key = config.get("api_keys", {}).get("together_ai")
        agent_info = config.get("agent_info", {})
        if not etherscan_api_key:
            logger.warning("No Etherscan API key found in config.toml, using mock data.")
            from exchange_api import fetch_mock_transactions
            transactions = fetch_mock_transactions(user_id)
        else:
            transactions = fetch_eth_transactions(user_id, etherscan_api_key)

        logger.info(f"Fetching transactions for user {user_id} from exchanges...")
        logger.info(f"Fetched {len(transactions)} transactions.")

        if not transactions:
            logger.warning("No transactions found for user. Report generation aborted.")
            print("\n⚠️ No transactions found for this wallet address. Cannot generate report.")
            return

        logger.info("Calculating gains and losses from transactions...")
        gains_losses = calculate_gains_losses(transactions)
        for gl in gains_losses:
            logger.debug(f"{gl['type'].capitalize()} {gl['amount']} {gl['asset']} at {gl['price']} USD, Gain/Loss: {gl.get('gain_loss', 0)}")

        total_gain_loss = sum(gl.get("gain_loss", 0) for gl in gains_losses)
        logger.info(f"Total Gain/Loss: {total_gain_loss}")

        # Aggregate gains/losses per asset for CSV report
        gains_losses_per_asset = {}
        for gl in gains_losses:
            asset = gl.get("asset")
            gain_loss = gl.get("gain_loss", 0)
            gains_losses_per_asset[asset] = gains_losses_per_asset.get(asset, 0) + gain_loss

        # Generate CSV report
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = f"reports/tax_report_{timestamp}.csv"
        report_data = {
            "gains_losses_per_asset": gains_losses_per_asset,
            "total_gain_loss": total_gain_loss
        }
        generate_csv_report(report_data, csv_path)
        logger.info(f"CSV report generated at: {csv_path}")

        # Generate text summary
        summary = generate_text_summary(gains_losses)
        logger.info("Generated text summary of gains/losses.")
        print("\\nCrypto Tax Report Summary")
        print("=========================")
        print(summary)

        # Generate tax report template using Together AI
        logger.info("Sending request to Together AI API...")
        company_info = config.get("Company", {})
        client_info = config.get("Client", {})
        contact_info = config.get("Contact_Us", {})
        # Format transactions for report template
        formatted_transactions = []
        for tx in gains_losses:
            timestamp = tx.get("timestamp")
            if timestamp:
                timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                timestamp_str = "N/A"
            asset = tx.get("asset", "N/A")
            tx_type = tx.get("type", "N/A").capitalize()
            currency = "USD"
            amount = tx.get("amount", 0)
            price = tx.get("price", 0)
            formatted_transactions.append(f"- {timestamp_str} {asset} {tx_type} {currency} {amount} {price}")
        transactions_str = "\n".join(formatted_transactions)

        # Include currency in total gain/loss
        total_gain_loss_str = f"{total_gain_loss:.2f} USD"

        tax_report = generate_terminusa_report_with_together_ai(total_gain_loss_str, transactions_str, together_ai_key, agent_info, company_info, client_info, contact_info)
        logger.info("Received response from Together AI API.\\n")
        print("\\nGenerated Tax Report Template:\\n")
        print(tax_report)

        logger.info("Terminusa system completed successfully.")

    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"\\n⚠️ ERROR: {e}")

if __name__ == "__main__":
    main()
