# Terminusa - Crypto Tax Reporting System

## Project Overview
Terminusa is a comprehensive Crypto Tax Reporting System designed to help cryptocurrency traders and investors automate the process of tracking transactions across multiple exchanges, calculating gains and losses, and generating tax-ready reports. Leveraging APIs such as Etherscan and CoinGecko, along with AI-powered report generation via Together AI, Terminusa simplifies the complex task of crypto tax compliance.

## Features
- Aggregates transaction histories from Ethereum blockchain and exchanges.
- Calculates gains and losses for tax reporting.
- Generates CSV reports and AI-powered tax report templates.
- Admin panel for user management, subscription management, billing, analytics, and frontend settings.
- User registration, login, and profile management.
- Secure session-based API endpoints.
- Multi-factor authentication (MFA) support.
- Billing and subscription management (mock implementation).
- Comprehensive logging with rotating file handlers.
- Configurable via `config.toml`.

## Installation

### Prerequisites
- Python 3.8 or higher
- Git

### Setup Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd Taxy
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the application by editing `config.toml` with your API keys and company/client information.

## Configuration

The `config.toml` file contains important configuration settings:

```toml
[api_keys]
together_ai = "your_together_ai_api_key"
etherscan_api_key = "your_etherscan_api_key"

[coin_gecko]
base_url = "https://api.coingecko.com/api/v3"

[logging]
level = "DEBUG"
log_file = "logs/terminusa.log"

[Company]
name = "Your Company Name"

[Client]
full_name = "Client Full Name"

[Contact_Us]
email = "support@terminusa.com"

[agent_info]
Your_Name = "Terminusa Agent"
Your_Title = "Tax Specialist"
Your_Tax_Firm = "Ten Titanics Technologies"
```

Update the placeholders with your actual information.

## Usage

### Running the Main Application
Run the main script to start the tax reporting process:

```bash
python main.py
```

You will be prompted to enter a user ID (Ethereum wallet address) to fetch transactions and generate reports.

### API Endpoints

The backend provides several API endpoints under the `/api` prefix, including:

- User settings management (`/api/user/settings`)
- Billing and subscription info (`/api/billing/*`)
- Multi-factor authentication (`/api/mfa/*`)
- Report management (`/api/reports/*`)

Authentication is session-based; users must be logged in to access these endpoints.

## Folder Structure

```
c:/Projects/Taxy/
├── admin/                      # Admin panel backend and templates
├── logs/                       # Log files
├── reports/                    # Generated tax reports
├── templates/                  # Frontend HTML templates
├── api.py                      # API endpoints
├── auth.py                     # Authentication logic
├── config.toml                 # Configuration file
├── db.py                       # Database initialization and management
├── ethscan_api.py              # Ethereum transaction fetching
├── exchange_api.py             # Exchange API integrations
├── logger.py                   # Logging setup
├── main.py                     # Main application entry point
├── price_api.py                # Price fetching APIs
├── report_generator.py         # Report generation logic
├── tax_calculator.py           # Tax calculation logic
├── together_ai.py              # Together AI integration
├── ui.py                       # User interface logic
├── requirements.txt            # Python dependencies
└── .gitignore
```

## Logging

Logging is configured with rotating file handlers to limit log file size and keep backups. Logs are stored in the `logs/` directory with detailed debug-level information by default.

## Contact

For support or inquiries, please contact:

- Email: support@terminusa.com
- Company: User Company Name

## License

This project does not currently specify a license. Please contact the maintainers for licensing information.
