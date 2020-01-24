from datetime import datetime
import json
import configparser
from urllib.request import urlopen
import pandas as pd
config = configparser.ConfigParser()
config.read('config.ini')

stock_list = config['Target']['Number']
stocks = json.loads(config.get("Target","Number"))
stock_list_in_url = '|'.join('tse_{}.tw'.format(stock) for stock in stocks) 

#print(stock_list_in_url)

query_url = "http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch="+ stock_list_in_url
#print(query_url)
data = json.loads(urlopen(query_url).read())
# 過濾出有用到的欄位
columns = ['c','n','z','tv','v','o','h','l','y']
df = pd.DataFrame(data['msgArray'], columns=columns)
df.columns = ['股票代號','公司簡稱','當盤成交價','當盤成交量','累積成交量','開盤價','最高價','最低價','昨收價']

print(df)

filename_to_save = "stock_info_{}.csv".format(datetime.date(datetime.today()).isoformat())

df.to_csv(filename_to_save)

print("saved to {}".format(filename_to_save))
