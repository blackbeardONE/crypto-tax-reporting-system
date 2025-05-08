import csv
import os
import logging
from datetime import datetime

logger = logging.getLogger('terminusa_logger')

def generate_csv_report(gains_losses_summary, output_dir="reports"):
    """
    Generate a CSV report of gains and losses.
    
    Args:
        gains_losses_summary (dict): Output from calculate_gains_losses function
        output_dir (str): Directory to save the report
    
    Returns:
        str: Path to the generated CSV file
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tax_report_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, mode='w', newline='') as csvfile:
            fieldnames = ['Asset', 'Gain/Loss (USD)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for asset, gain_loss in gains_losses_summary.get("gains_losses_per_asset", {}).items():
                writer.writerow({'Asset': asset, 'Gain/Loss (USD)': f"{gain_loss:.2f}"})
            
            writer.writerow({})
            writer.writerow({'Asset': 'Total', 'Gain/Loss (USD)': f"{gains_losses_summary.get('total_gain_loss', 0):.2f}"})
        
        logger.info(f"CSV report generated at {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error generating CSV report: {e}")
        return None

def generate_text_summary(gains_losses_list):
    """
    Generate a text summary of gains and losses.
    
    Args:
        gains_losses_list (list): List of transactions with gain/loss info
    
    Returns:
        str: Text summary
    """
    lines = []
    lines.append("Crypto Tax Report Summary")
    lines.append("=========================")
    
    # Aggregate gain/loss per asset
    gains_losses_per_asset = {}
    total_gain_loss = 0.0
    for tx in gains_losses_list:
        asset = tx.get("asset")
        gain_loss = tx.get("gain_loss", 0.0)
        gains_losses_per_asset[asset] = gains_losses_per_asset.get(asset, 0.0) + gain_loss
        total_gain_loss += gain_loss
    
    for asset, gain_loss in gains_losses_per_asset.items():
        lines.append(f"{asset}: {gain_loss:.2f} USD")
    
    lines.append("-------------------------")
    lines.append(f"Total Gain/Loss: {total_gain_loss:.2f} USD")
    
    summary = "\n".join(lines)
    logger.info("Generated text summary of gains/losses.")
    return summary
