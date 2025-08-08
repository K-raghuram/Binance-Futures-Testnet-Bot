### README.md

```
# Binance Futures Testnet Bot with Retry Logic & Advanced Orders

A Python bot for automated trading on Binance Futures Testnet with advanced order types and safety features.

## Features
- Market orders with position verification
- Limit orders with retry logic
- Stop-limit orders with retry logic
- Automatic test balance management
- Price precision handling
- Position mode management
- Real-time market price display

## Setup

### Prerequisites
1. Python 3.6 or higher
2. Git Bash
3. Binance Futures Testnet account

### Installation Steps
1. Clone repository and enter directory
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create and activate virtual environment
   ```bash
   python -m venv venv
   source venv/Scripts/activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

### API Configuration
1. Get Binance Futures Testnet API Keys
   * Visit https://testnet.binancefuture.com/
   * Create an account if needed
   * Go to API Management
   * Generate new API key and secret

2. Set up environment variables
   ```bash
   # Create and edit .env file
   cp .env.example .env
   ```

3. Add your API keys to .env
   ```plaintext
   BINANCE_API_KEY=your_testnet_api_key
   BINANCE_API_SECRET=your_testnet_api_secret
   ```

### Running the Bot
1. Activate virtual environment (if not already activated)
   ```bash
   source venv/Scripts/activate
   ```

2. Start the bot
   ```bash
   python bot.py
   ```

### Troubleshooting
1. Reset virtual environment
   ```bash
   deactivate
   rm -rf venv
   python -m venv venv
   source venv/Scripts/activate
   pip install -r requirements.txt
   ```

2. Verify installations
   ```bash
   python --version  # Should be 3.6+
   pip list  # Should show python-binance
   ```

## Workflow

### Trading Flow
1. Initial Setup
   * Bot checks for sufficient test balance
   * Guides you to get test assets if balance is low
   * Verifies futures trading is enabled
   * Shows current futures account balance

2. Trading Process
   a. Choose Order Type
      * Market Order: Immediate execution at current price
      * Limit Order: Set your desired price
      * Stop-Limit Order: Set trigger and limit prices

   b. Enter Trading Details
      * Symbol (e.g., BTCUSDT)
      * Shows current market price
      * Position side (BUY/SELL)
      * Quantity (with precision validation)
      * Price (for limit orders)
      * Stop price (for stop-limit orders)

   c. Order Execution
      * Validates input parameters
      * Formats quantity and price to match exchange requirements
      * Places order with retry mechanism
      * Verifies order placement
      * Shows position/order status

3. Safety Features
- Test-only mode (no real funds at risk)
- Automatic position mode handling
- Price and quantity precision validation
- Order verification and status checking
- Multiple retry attempts for limit orders
- Position and balance verification

## Supported Order Types

### Market Orders
- Immediate execution
- Shows entry price and position details
- Verifies position after execution

### Limit Orders
- Set your desired entry price
- Stays active until filled or cancelled
- Retries on placement failure
- Verifies order in open orders

### Stop-Limit Orders
- Set trigger price and limit price
- Activates when trigger price is hit
- Verifies order placement
- Shows order status

## Common Issues & Solutions

1. "Invalid quantity" error:
   - Each symbol has specific quantity requirements
   - Bot shows valid quantity ranges before input
   - Use the displayed step size

2. Position Mode errors:
   - Bot automatically handles position mode
   - Warns if mode can't be changed due to open positions
   - Continues with current mode if positions exist

3. Balance issues:
   - Shows how to get more test assets
   - Guides through the process
   - Verifies new balance after funding

## Error Handling
- Retries failed limit orders
- Validates all inputs
- Provides clear error messages
- Shows detailed order status
- Verifies order execution

## Best Practices
1. Always check current market price before placing orders
2. Start with small test quantities
3. Monitor position status after order execution
4. Use limit orders to get better entry prices
5. Verify balance and positions regularly
```

### .gitignore

```
.env
__pycache__/
```
