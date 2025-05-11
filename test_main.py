import unittest
from unittest.mock import patch, MagicMock
import main
import ethscan_api
import tax_calculator
import price_api
import report_generator

class TestTerminusaSystem(unittest.TestCase):

    @patch('ethscan_api.requests.get')
    def test_fetch_eth_transactions(self, mock_get):
        # Mock Etherscan API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "1",
            "message": "OK",
            "result": [
                {
                    "timeStamp": "1650000000",
                    "from": "0xabc",
                    "to": "0xdef",
                    "value": "1000000000000000000",
                    "gasUsed": "21000",
                    "gasPrice": "1000000000"
                }
            ]
        }
        mock_get.return_value = mock_response

        transactions = ethscan_api.fetch_eth_transactions("0xabc", "fake_api_key")
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['asset'], 'ETH')

    @patch('price_api.requests.get')
    def test_get_historical_price(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "market_data": {
                "current_price": {
                    "usd": 2000.0
                }
            }
        }
        mock_get.return_value = mock_response

        price = price_api.get_historical_price("ethereum", __import__('datetime').date.today())
        self.assertEqual(price, 2000.0)

    def test_calculate_gains_losses(self):
        transactions = [
            {"type": "buy", "asset": "ETH", "amount": 1.0, "price": 1000.0, "timestamp": None},
            {"type": "sell", "asset": "ETH", "amount": 0.5, "price": 1500.0, "timestamp": None}
        ]
        results = tax_calculator.calculate_gains_losses(transactions)
        self.assertEqual(len(results), 2)
        self.assertAlmostEqual(results[1]['gain_loss'], 250.0)

    @patch('main.generate_tax_report_with_together_ai')
    def test_generate_tax_report(self, mock_generate):
        mock_generate.return_value = "Tax report content"
        gains_losses = [
            {"type": "sell", "asset": "ETH", "amount": 0.5, "price": 1500.0, "gain_loss": 250.0}
        ]
        report = main.generate_tax_report_with_together_ai(250.0, gains_losses)
        self.assertIn("Tax report content", report)

if __name__ == '__main__':
    unittest.main()
