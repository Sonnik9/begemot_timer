import hmac
from hashlib import sha256
import requests
import time
import pandas as pd
from init_params import PARAMS

class BINGX_API(PARAMS):
    def __init__(self):
        super().__init__()
    # POST ////////////////////////////////////////////////////////////////////
    def get_query_str(self, symbol, side, qnt):
        base_url = "https://open-api.bingx.com/openApi/spot/v1/trade/order"
        timestamp = int(time.time() * 1000)        
        qty_var = 'quoteOrderQty' if side == 'BUY' else 'quantity'
        query_string = f"symbol={symbol}&side={side}&type=MARKET&{qty_var}={qnt}&timestamp={timestamp}"
        signature = hmac.new(self.api_secret.encode("utf-8"), query_string.encode("utf-8"), digestmod=sha256).hexdigest()
        return f"{base_url}?{query_string}&signature={signature}"

    def place_market_order(self, symbol, side, qnt):               
        url = self.get_query_str(symbol, side, qnt)            
        return requests.post(url, headers={'X-BX-APIKEY': self.api_key})
    # /////////////////////////////////////////////////////////////////////////

    def get_url_limit_query(self, symbol, side, qnt, target_price):
        base_url = "https://open-api.bingx.com/openApi/spot/v1/trade/order"
        timestamp = int(time.time() * 1000)
        query_string = f"symbol={symbol}&side={side}&type=LIMIT&quantity={qnt}&price={target_price}&timestamp={timestamp}"
        signature = hmac.new(self.api_secret.encode("utf-8"), query_string.encode("utf-8"), digestmod=sha256).hexdigest()
        return f"{base_url}?{query_string}&signature={signature}"
    
    def place_limit_order(self, symbol, side, qnt, target_price):
        try:                
            url = self.get_url_limit_query(symbol, side, qnt, target_price)
            return requests.post(url, headers={'X-BX-APIKEY': self.api_key})
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_current_price(self, symbol):
        url = f"https://open-api.bingx.com/openApi/spot/v1/ticker/price?symbol={symbol}"
        try:
            response = requests.get(url)
            data = response.json() 
            # print(data)           
            return float(data['data'][0]['trades'][0]['price'])
        except Exception as ex:
            print(ex)
            return None  

    def get_klines(self, symbol, interval='1m', limit=5):    
        url = f'https://open-api.bingx.com/openApi/spot/v2/market/kline?symbol={symbol}&interval={interval}&limit={limit}'
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f'Failed to fetch data. Status code: {response.status_code}')
                return pd.DataFrame()
            data = response.json()            
            data = pd.DataFrame(data['data'], columns=['Time', 'Open', 'High', 'Low', 'Close', 'hz1', 'hz2', 'Volume'])            
            data['Time'] = pd.to_datetime(data['Time'].astype(int), unit='ms')
            data.set_index('Time', inplace=True)
            return data.astype(float)
        except Exception as ex:
            print(ex)
            return     


# api = BINGX_API()
# # print(api.get_klines(symbol='ASTO-USDT'))
# print(api.get_current_price(symbol='ASTO-USDT'))
