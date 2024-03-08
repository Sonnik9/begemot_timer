import os
from dotenv import load_dotenv
load_dotenv()

class PARAMS():
    def __init__(self) -> None:
        self.init_all()
        # pass
    
    def init_keys(self):        
        self.api_key  = os.getenv(f"BINGX_API_PUBLIC_KEY", "")
        self.api_secret = os.getenv(f"BINGX_API_PRIVATE_KEY", "") 

    def init_default_params(self):
        self.SOLI_DEO_GLORIA = 'Soli Deo Gloria!'
        self.symbol = None #usdt only!!! 
        # self.order_time = None # "2024-03-04 12:00:00", ASTO 10:00 (UTC)?   
        self.set_list = [("ARB-USDT", "2024-03-08 23:41:00")]    
        self.depo = 10
        self.sell_mode = 'm100' # t100 -- timer on all qty, m -- manual, tm -- mix, m100 -- manual on all qty, l -- limit grid, l100 -- 1 limit order
        self.for_auto_qnt_mult = 0.5        
        # //////////////////////////////////////////////////////////////////////
        self.pre_start_flag = False
        self.pre_start_pause = 60 
        self.t100_mode_pause = 180
        self.tm_mode_pause = 1
        attempts_number = 3        
        self.iter_list = list(range(1, attempts_number + 1))  

    def init_all(self):
        self.init_keys()
        self.init_default_params()


         