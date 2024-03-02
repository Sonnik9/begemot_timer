import hmac
from hashlib import sha256
import requests
import time
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
