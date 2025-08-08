### bot.py

import os
from dotenv import load_dotenv
from basic_bot import BasicBot

load_dotenv()

API_KEY = os.getenv('BINANCE_API_KEY')
API_SECRET = os.getenv('BINANCE_API_SECRET')

bot = BasicBot(API_KEY, API_SECRET, testnet=True)

print("\nChecking test balance...")
if not bot.ensure_test_balance():
    print("Failed to verify test balance. Please make sure you have test assets.")
    exit(1)

print("\nTESTNET MODE: All trades will use test money, not real funds.")
futures_balance = bot.check_futures_balance()
print(f"\nCurrent futures account balance: {futures_balance} USDT")
if futures_balance <= 0:
    print("Insufficient futures balance. Please transfer funds to futures account.")
    exit(1)

print("\n1. Market Order\n2. Limit Order\n3. Stop-Limit Order")
choice = input("Choose order type: ")

symbol = input("Enter symbol (e.g., BTCUSDT): ").upper()

# Get and show current market price
current_price = bot.get_market_price(symbol)
if current_price:
    print(f"\nCurrent {symbol} price: {current_price}")
else:
    print(f"Could not get current price for {symbol}")
    exit(1)

side = input("\nEnter side (BUY/SELL): ").upper()
quantity = float(input("Enter quantity: "))

if choice == '1':
    print(f"\nPlacing market order at current price: {current_price}")
    order = bot.place_market_order(symbol, side, quantity)
elif choice == '2':
    print(f"\nCurrent market price: {current_price}")
    price = float(input("Enter limit price: "))
    order = bot.place_limit_order(symbol, side, quantity, price)
elif choice == '3':
    print(f"\nCurrent market price: {current_price}")
    price = float(input("Enter limit price: "))
    stop_price = float(input("Enter stop price: "))
    order = bot.place_stop_limit_order(symbol, side, quantity, price, stop_price)
else:
    print("Invalid choice")
    exit(1)

# Verify order status
if order:
    print("\nOrder placed successfully!")
    
    # Check position for market orders
    if choice == '1':
        position = bot.client.futures_position_information(symbol=symbol)
        for pos in position:
            if float(pos['positionAmt']) != 0:
                print(f"\nPosition opened:")
                print(f"Amount: {pos['positionAmt']}")
                print(f"Entry Price: {pos['entryPrice']}")
                print(f"Unrealized PnL: {pos['unRealizedProfit']}")
                break
    
    # Check open orders for limit and stop-limit orders
    if choice in ['2', '3']:
        open_orders = bot.client.futures_get_open_orders(symbol=symbol)
        if open_orders:
            print("\nOpen orders:")
            for order in open_orders:
                print(f"Order ID: {order['orderId']}")
                print(f"Type: {order['type']}")
                print(f"Side: {order['side']}")
                print(f"Price: {order['price']}")
                print(f"Quantity: {order['origQty']}")
else:
    print("Invalid choice")

