import sched
import time
from api_bingX import BINGX_API
from utils import UTILS
import logging, os, inspect
logging.basicConfig(filename='log.log', level=logging.INFO)
current_file = os.path.basename(__file__)

class TEMPLATES(BINGX_API, UTILS):
    def __init__(self) -> None:
        super().__init__()

    def sell_limit_temp(self, qnt_to_sell, target_price):  
        response_data_list = []
        try:            
            response = None                         
            response = self.place_limit_order(self.symbol, 'SELL', qnt_to_sell, target_price)
            response = response.json()
            response_data_list.append(response)
            if response.get("code") == 0 and response["data"]["status"] == 'PENDING': 
                print('The sell LIMIT order was created succesfully!')                               
        except Exception as ex:            
            logging.exception(
                f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
        return response_data_list

    def sell_market_temp(self, symbol, sell_qnt):
        response_data_list = [] 
        sell_success_flag = False             
        for _ in self.iter_list:  
            try:            
                response = None 
                response = self.place_market_order(symbol, 'SELL', sell_qnt)
                try:
                    response = response.json()                                
                    response_data_list.append(response)   
                except Exception as ex:
                    response_data_list.append({'Error': f"Unable to convert response to json. Status: {response.status_code}"}) 
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")                                      
                try:
                    if response.get("code") == 0 and response["data"]["status"] == 'FILLED': 
                        print('The sell order was fulfilled succesfully!') 
                        sell_success_flag = True                                                        
                        break                                              
                except Exception as ex:                    
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}") 
                print("Some problems with placing the sell order")                 
                time.sleep(0.05)           
            except Exception as ex:                
                logging.exception(
                    f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                 
        return response_data_list, sell_success_flag
    
    def buy_market_temp(self, symbol, depo):
        response_data_list = []
        response_success_list = []
        try:                                   
            response = self.place_market_order(symbol, 'BUY', depo)                
            response = response.json()                            
            response_data_list.append(response)                   
            if response.get("code") == 0 and response["data"]["status"] == 'FILLED': 
                response_success_list.append(response) 
                print('The buy order was fulfilled successfully!')                                                 
        except Exception as ex:                
            logging.exception(
                f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")       
        return response_data_list, response_success_list

class STRATEGY(TEMPLATES):
    def __init__(self) -> None:
        super().__init__()

    def t100_mode(self, qnt_to_sell_start, response_data_list):
        try:
            time.sleep(self.t100_mode_pause)                
            qnt_to_sell = int(qnt_to_sell_start)                    
            response_data_list_item, _ = self.sell_market_temp(self.symbol, qnt_to_sell)            
            response_data_list += response_data_list_item                     
        except Exception as ex:                
            logging.exception(
                f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}") 
        return response_data_list

    def tm_mode(self, qnt_to_sell_start, response_data_list):
        try:
            time.sleep(self.tm_mode_pause)                
            qnt_to_sell = int(qnt_to_sell_start* self.for_auto_qnt_mult)                    
            response_data_list_item, _ = self.sell_market_temp(self.symbol, qnt_to_sell)
            response_data_list += response_data_list_item 
            self.json_writer(self.symbol, response_data_list)                   
            input(f"Are you sure you want to sell all left {self.symbol}? If yes, tub Enter",)                    
            response_data_list_item, _ = self.sell_market_temp(self.symbol, qnt_to_sell)
            response_data_list += response_data_list_item                  
        except Exception as ex:                
            logging.exception(
                f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}") 
        return response_data_list        

    def m100_mode(self, qnt_to_sell_start, response_data_list):
        try:
            qnt_to_sell = int(qnt_to_sell_start)
            input(f"Are you sure you want to sell all left {self.symbol}? If yes, tub Enter",)                    
            response_data_list_item, _ = self.sell_market_temp(self.symbol, qnt_to_sell)
            response_data_list += response_data_list_item            
        except Exception as ex:                
            logging.exception(
                f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}") 
        return response_data_list

    def m_mode(self, qnt_to_sell_start, response_data_list):
        left_qnt = qnt_to_sell_start
        stop_selling = False                
        qnt_percent_pieces_left = 100
        while True:
            if not stop_selling:
                qnt_percent_pieces = input(f"Are you sure you want to sell {self.symbol}? If yes, tub a pieces qty (%) (e.g.: 1-100). Opposite tub enithing else for exit",)  
                try:                                      
                    qnt_percent_pieces = int(qnt_percent_pieces.strip())
                    qnt_percent_pieces_left = qnt_percent_pieces_left - qnt_percent_pieces
                    if qnt_percent_pieces_left < 0:
                        qnt_percent_pieces_left = qnt_percent_pieces_left + qnt_percent_pieces
                        print(f'Please enter a valid data. There are {qnt_percent_pieces_left} pieces left to sell')
                        continue                              
                except:
                    print('Selling session was deprecated. Have a nice day!')
                    return response_data_list
                try:
                    stop_selling = qnt_percent_pieces_left == 0        
                    qnt_multipliter = qnt_percent_pieces/100
                    qnt_to_sell = int(qnt_to_sell_start* qnt_multipliter)                           
                    print(f"qnt_to_sell: {qnt_to_sell}")
                    response_data_list_item, sell_success_flag = self.sell_market_temp(self.symbol, qnt_to_sell)
                    response_data_list += response_data_list_item  
                    self.json_writer(self.symbol, response_data_list)
                    if sell_success_flag:
                        left_qnt = left_qnt - qnt_to_sell  
                    else:
                        qnt_percent_pieces_left = qnt_percent_pieces_left + qnt_percent_pieces
                    print(f"Trere are {qnt_percent_pieces_left} pieces and {left_qnt} qty left to sell")                       
                except Exception as ex:                
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")                                   
                continue
            return response_data_list
    
    def l_mode(self, qnt_to_sell_start, response_data_list):
        try:
            time.sleep(60)
            target_list = []                
            klines = self.get_klines(self.symbol)
            hight = klines['High'].iloc[-1]            
            close_price = klines['Close'].iloc[-1]
            # ////////////////////////////////////////                
            price_precession = self.price_precession_extractor(close_price)
            print('#///////////////////////////////')
            if hight > close_price:
                qnt_to_sell = int(qnt_to_sell_start/2)
                addit_pices = (hight - close_price)*0.49
                target_list.append(round(close_price + addit_pices, price_precession))        
                target_list.append(round(hight* 0.98, price_precession))                    
            else:
                qnt_to_sell = int(qnt_to_sell_start)
                target_list.append(round(hight * 1.05, price_precession)) 

            for target_price in target_list:
                response_data_list += self.sell_limit_temp(qnt_to_sell, target_price)
        except Exception as ex:                
            logging.exception(
                f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")  
        return response_data_list
    
    def l100_mode(self, qnt_to_sell_start, response_data_list):
        try:            
            target_price = None                
            klines = self.get_klines(self.symbol)
            hight = klines['High'].iloc[-1]            
            close_price = klines['Close'].iloc[-1]
            # ////////////////////////////////////////                
            price_precession = self.price_precession_extractor(close_price)
            print('#///////////////////////////////')
            qnt_to_sell = int(qnt_to_sell_start)
            addit_pices = (hight - close_price)*0.49
            target_price = round(close_price + addit_pices, price_precession)      
            response_data_list += self.sell_limit_temp(qnt_to_sell, target_price)
        except Exception as ex:                
            logging.exception(
                f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")  
        return response_data_list

class CONTROLLER(STRATEGY):
    def __init__(self) -> None:
        super().__init__()

    def controller_func(self):
        response_data_list, response_success_list = [], []  
        self.pre_start_flag = self.sell_mode == 'l100'
        if self.pre_start_flag:
            time.sleep(self.pre_start_pause)       
        response_data_list, response_success_list = self.buy_market_temp(self.symbol, self.depo) 
        self.json_writer(self.symbol, response_data_list)              
        if len(response_success_list) != 0:            
            qnt_to_sell_start = 0               
            for fill in response_success_list:
                try:
                    qnt_to_sell_start += float(fill["data"]["executedQty"])
                except Exception as ex:                    
                    logging.exception(
                        f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")                    
            try:
                print(f"qnt_to_sell_start: {qnt_to_sell_start}")
                print(f"buy_price: {float(response_success_list[0]['data']['cummulativeQuoteQty'])/float(response_success_list[0]['data']['executedQty'])}") 
            except Exception as ex:                    
                logging.exception(
                    f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")
                
            if self.sell_mode == 't100':
                response_data_list = self.t100_mode(qnt_to_sell_start, response_data_list)
            elif self.sell_mode == 'tm':
                response_data_list = self.tm_mode(qnt_to_sell_start, response_data_list)    
            elif self.sell_mode == 'm100':
                response_data_list = self.m100_mode(qnt_to_sell_start, response_data_list)
            elif self.sell_mode == 'm':
                response_data_list = self.m_mode(qnt_to_sell_start, response_data_list)
            elif self.sell_mode == 'l':
                response_data_list = self.l_mode(qnt_to_sell_start, response_data_list)
            elif self.sell_mode == 'l100' or self.sell_mode == 'l1100':
                response_data_list = self.l100_mode(qnt_to_sell_start, response_data_list)
            result_time, response_data_list = self.show_trade_time(response_data_list) 
            self.json_writer(self.symbol, response_data_list)           
            print(result_time) 
            print(self.SOLI_DEO_GLORIA)           
        else:
            print('Some problems with placing buy market order...')

    def schedule_order_execution(self, order_time):
        print('God blass you Nik!')                
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enterabs(time.mktime(time.strptime(order_time, "%Y-%m-%d %H:%M:%S")), 1, self.controller_func)
        scheduler.run()

    def run(self):        
        for symbol, order_time in self.set_list:
            self.symbol = symbol
            self.schedule_order_execution(order_time)  

if __name__=="__main__":
    father = CONTROLLER() 
    father.run()
