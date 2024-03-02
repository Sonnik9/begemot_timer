import datetime
import json
import logging, os, inspect
logging.basicConfig(filename='log.log', level=logging.INFO)
current_file = os.path.basename(__file__)

class UTILS():
    def __init__(self) -> None:
        pass

    def json_writer(self, symbol, response_data_list):
        try:
            with open(f"{symbol}trading_data.json", "w") as f:
                json.dump(response_data_list, f, indent=4)
        except Exception as ex:
            logging.exception(
                f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}")

    def milliseconds_to_datetime(self, milliseconds):
        seconds, milliseconds = divmod(milliseconds, 1000)
        time = datetime.datetime.utcfromtimestamp(seconds)
        milliseconds_str = str(milliseconds).zfill(3)
        return time.strftime('%Y-%m-%d %H:%M:%S') + '.' + milliseconds_str
        
    def show_trade_time(self, response_data_list):
        result_time = ''
        for d in response_data_list:
            try:
                formatted_time = self.milliseconds_to_datetime(d['data']['transactTime'])               
                form_time = f"{d['data']['status']}___{d['data']['side']}: {formatted_time}" 
                result_time += form_time + '\n'                    
            except Exception as ex:
                logging.exception(
                    f"An error occurred in file '{current_file}', line {inspect.currentframe().f_lineno}: {ex}") 
                # print(ex)
        return result_time

