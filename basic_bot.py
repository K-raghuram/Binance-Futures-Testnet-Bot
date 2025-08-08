# Starter: Binance Futures Testnet Bot


from binance import Client
import logging
import time
from decimal import Decimal

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret, testnet=True)  # Force testnet to True
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        
    def ensure_test_balance(self):
        """Ensure we have test balance in futures account"""
        try:
            # Check futures account balance
            balance = self.client.futures_account_balance()
            usdt_balance = next((item for item in balance if item['asset'] == 'USDT'), None)
            
            if not usdt_balance or float(usdt_balance['balance']) < 100:
                self.logger.info("Insufficient test balance. Getting new test assets...")
                
                # Get test assets from Binance Futures Testnet website
                try:
                    # Note: You need to manually get test assets from:
                    # https://testnet.binancefuture.com/en/futures/BTCUSDT
                    # Click on "Get Assets" button in the testnet interface
                    print("\nIMPORTANT: Please follow these steps to get test assets:")
                    print("1. Go to https://testnet.binancefuture.com/en/futures/BTCUSDT")
                    print("2. Click on 'Get Assets' button in the top-right")
                    print("3. Wait a few seconds for the test assets to be credited")
                    input("\nPress Enter after you've gotten test assets...")
                    
                    # Verify the new balance
                    balance = self.client.futures_account_balance()
                    usdt_balance = next((item for item in balance if item['asset'] == 'USDT'), None)
                    if usdt_balance:
                        self.logger.info(f"New test balance: {usdt_balance['balance']} USDT")
                        return True
                except Exception as e:
                    self.logger.error(f"Error getting test assets: {e}")
                    return False
            else:
                self.logger.info(f"Current test balance: {usdt_balance['balance']} USDT")
                return True
        except Exception as e:
            self.logger.error(f"Error checking test balance: {e}")
            return False
        
    def check_and_prepare_futures_account(self):
        """Check and prepare futures account for trading"""
        try:
            # Enable futures if not already enabled
            try:
                self.client.futures_get_position_mode()
            except:
                self.logger.info("Enabling futures trading...")
                self.client.futures_create_order()  # This will enable futures trading
                
            # Get spot account balance
            spot_balance = self.client.get_asset_balance(asset='USDT')
            if spot_balance:
                spot_amount = float(spot_balance['free'])
                self.logger.info(f"Spot USDT balance: {spot_amount}")
                
                # If spot balance exists, transfer some to futures if futures balance is low
                futures_balance = self.client.futures_account_balance()
                futures_usdt = next((item for item in futures_balance if item['asset'] == 'USDT'), None)
                if futures_usdt:
                    futures_amount = float(futures_usdt['balance'])
                    self.logger.info(f"Futures USDT balance: {futures_amount}")
                    
                    if futures_amount < 10 and spot_amount > 10:  # If futures balance is low
                        transfer_amount = min(spot_amount - 1, 10)  # Keep some in spot
                        self.logger.info(f"Transferring {transfer_amount} USDT to futures account")
                        self.client.futures_account_transfer(
                            asset='USDT',
                            amount=transfer_amount,
                            type=1  # 1 for spot to futures, 2 for futures to spot
                        )
                        time.sleep(1)  # Wait for transfer to process
            
            return True
        except Exception as e:
            self.logger.error(f"Error preparing futures account: {e}")
            return False
            
    def check_futures_balance(self):
        """Check futures account balance"""
        try:
            balance = self.client.futures_account_balance()
            usdt_balance = next((item for item in balance if item['asset'] == 'USDT'), None)
            if usdt_balance:
                return float(usdt_balance['balance'])
            return 0
        except Exception as e:
            self.logger.error(f"Error checking futures balance: {e}")
            return 0
        
    def get_market_price(self, symbol):
        """Get current market price for a symbol"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            self.logger.error(f"Error getting market price: {e}")
            return None
            
    def get_symbol_precision(self, symbol):
        """Get price and quantity precision for a symbol"""
        try:
            info = self.client.futures_exchange_info()
            for s in info['symbols']:
                if s['symbol'] == symbol:
                    price_precision = 0
                    qty_precision = 0
                    for filter in s['filters']:
                        if filter['filterType'] == 'PRICE_FILTER':
                            price_precision = str(float(filter['tickSize']))[::-1].find('.')
                        elif filter['filterType'] == 'LOT_SIZE':
                            qty_precision = str(float(filter['stepSize']))[::-1].find('.')
                    return price_precision, qty_precision
            return None, None
        except Exception as e:
            self.logger.error(f"Error getting symbol precision: {e}")
            return None, None

    def place_market_order(self, symbol, side, quantity):
        try:
            # Check current position mode
            try:
                position_mode = self.client.futures_get_position_mode()
                self.logger.info(f"Current position mode: {position_mode}")
            except Exception as e:
                self.logger.error(f"Error getting position mode: {e}")
                return None
                
            # Check for existing positions
            positions = self.client.futures_position_information()
            active_positions = [p for p in positions if float(p['positionAmt']) != 0]
            
            if not active_positions:
                # Only try to change position mode if there are no active positions
                try:
                    self.client.futures_change_position_mode(dualSidePosition=True)
                    self.logger.info("Hedge Mode enabled")
                except Exception as e:
                    if "No need to change position side" not in str(e):
                        self.logger.warning(f"Could not change to hedge mode: {e}")
            else:
                self.logger.info("Active positions exist, keeping current position mode")
            
            # Format quantity with correct precision
            _, qty_precision = self.get_symbol_precision(symbol)
            if qty_precision is not None:
                quantity = float(Decimal(str(quantity)).quantize(Decimal(f'0.{"0" * qty_precision}')))
            
            # Place the order with reduced margin mode
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity,
                reduceOnly=False,  # Allow new positions
                newOrderRespType='RESULT'  # Get full order response
            )
            self.logger.info(f"Market order placed: {order}")
            
            # Wait for order to be processed
            time.sleep(2)
            
            # Verify the position
            positions = self.client.futures_position_information(symbol=symbol)
            position_found = False
            for pos in positions:
                if float(pos['positionAmt']) != 0:
                    self.logger.info(f"Position verified: {pos}")
                    position_found = True
                    break
            
            if not position_found:
                self.logger.warning("Order placed but position not found. Checking order status...")
                # Check order status
                order_status = self.client.futures_get_order(symbol=symbol, orderId=order['orderId'])
                self.logger.info(f"Order status: {order_status}")
                
            return order
        except Exception as e:
            self.logger.error(f"Error placing market order: {e}")
            return None

    def place_limit_order(self, symbol, side, quantity, price, retries=3):
        attempt = 0
        while attempt < retries:
            try:
                # Check current position mode
                try:
                    position_mode = self.client.futures_get_position_mode()
                    self.logger.info(f"Current position mode: {position_mode}")
                except Exception as e:
                    self.logger.error(f"Error getting position mode: {e}")
                    return None
                
                # Check for existing positions
                positions = self.client.futures_position_information()
                active_positions = [p for p in positions if float(p['positionAmt']) != 0]
                
                if not active_positions:
                    # Only try to change position mode if there are no active positions
                    try:
                        self.client.futures_change_position_mode(dualSidePosition=True)
                        self.logger.info("Hedge Mode enabled")
                    except Exception as e:
                        if "No need to change position side" not in str(e):
                            self.logger.warning(f"Could not change to hedge mode: {e}")
                else:
                    self.logger.info("Active positions exist, keeping current position mode")
                    
                # Format price and quantity with correct precision
                price_precision, qty_precision = self.get_symbol_precision(symbol)
                if price_precision is not None and qty_precision is not None:
                    price = float(Decimal(str(price)).quantize(Decimal(f'0.{"0" * price_precision}')))
                    quantity = float(Decimal(str(quantity)).quantize(Decimal(f'0.{"0" * qty_precision}')))
                
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='LIMIT',
                    quantity=quantity,
                    price=price,
                    timeInForce='GTC'
                )
                self.logger.info(f"Limit order placed: {order}")
                
                # Verify the order exists
                time.sleep(1)  # Wait for order to process
                open_orders = self.client.futures_get_open_orders(symbol=symbol)
                for open_order in open_orders:
                    if open_order['orderId'] == order['orderId']:
                        self.logger.info(f"Order verified in open orders: {open_order}")
                        return order
                
                self.logger.warning("Order placed but not found in open orders")
                return order
            except Exception as e:
                attempt += 1
                self.logger.warning(f"Attempt {attempt} failed: {e}")
                time.sleep(2)
        self.logger.error("Max retries reached. Could not place limit order.")
        return None

    def place_stop_limit_order(self, symbol, side, quantity, price, stop_price, retries=3):
        attempt = 0
        while attempt < retries:
            try:
                # Check current position mode
                try:
                    position_mode = self.client.futures_get_position_mode()
                    self.logger.info(f"Current position mode: {position_mode}")
                except Exception as e:
                    self.logger.error(f"Error getting position mode: {e}")
                    return None
                
                # Check for existing positions
                positions = self.client.futures_position_information()
                active_positions = [p for p in positions if float(p['positionAmt']) != 0]
                
                if not active_positions:
                    # Only try to change position mode if there are no active positions
                    try:
                        self.client.futures_change_position_mode(dualSidePosition=True)
                        self.logger.info("Hedge Mode enabled")
                    except Exception as e:
                        if "No need to change position side" not in str(e):
                            self.logger.warning(f"Could not change to hedge mode: {e}")
                else:
                    self.logger.info("Active positions exist, keeping current position mode")
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='STOP_MARKET',
                    stopPrice=stop_price,
                    closePosition=False,
                    quantity=quantity,
                    price=price,
                    timeInForce='GTC'
                )
                self.logger.info(f"Stop-limit order placed: {order}")
                return order
            except Exception as e:
                attempt += 1
                self.logger.warning(f"Attempt {attempt} failed: {e}")
                time.sleep(2)
        self.logger.error("Max retries reached. Could not place stop-limit order.")
        return None





