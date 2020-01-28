# !/usr/bin/python
# coding:utf-8

import configparser
import requests
import time
import json
from bs4 import BeautifulSoup
import pandas as pd

INDEX_YEAR = 0
INDEX_CASH_DIVIDEND = 3
INDEX_STOCK_DIVIDEND = 6
INDEX_EPS = 20

CODE_STR = 'Code'
KEY_NAME = 'Name'

KEY_CASH_DIVIDEND = '_現金股利'
KEY_STOCK_DIVIDEND = '_股票股利'

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    start_time = config['FinancialReport']['start_season']
    end_time = config['FinancialReport']['end_season']

    [start_year, start_season] = start_time.split('/')
    [end_year, end_season] = end_time.split('/')

    if end_year < start_year:
        print("End year cannot be less than start year, please modify your config.")
        exit()

    year_str_list = []
    df_column_list = []
    if end_year == start_year:
        df_column_list.append(start_year + KEY_CASH_DIVIDEND)
        df_column_list.append(start_year + KEY_STOCK_DIVIDEND)
    else :
        for y in range(int(start_year), int(end_year)+1):
            year_str_list.append(str(y))
            df_column_list.append(str(y) + KEY_CASH_DIVIDEND)
            df_column_list.append(str(y) + KEY_STOCK_DIVIDEND)

    stock_list = config['Target']['Number']
    stocks = json.loads(config.get("Target","Number"))
    stock_str_list = [str(s) for s in stocks]

    df_all = pd.DataFrame([], columns=[KEY_NAME] + df_column_list, index=stock_str_list)

    for stock in stock_str_list:
        url = 'https://goodinfo.tw/StockInfo/StockDividendPolicy.asp?STOCK_ID=' + stock
        ## 使用假header
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        result = requests.get(url, headers=headers) 
        result.encoding = 'utf8'
        soup = BeautifulSoup(result.text, 'html.parser')
        name = soup.title.getText().split()[1]
        div = soup.find(id='divDetail')
        tables = div.find_all('table')
        target_tab = tables[0]

        for tr in target_tab.findAll('tr'):
            tds = tr.findAll('td')
            if is_float(tds[INDEX_YEAR].getText()):
                year = tds[INDEX_YEAR].getText()
                if (int(year) <= int(end_year)) and (int(start_year) <= int(year)):
                    cash_dividend = tds[INDEX_CASH_DIVIDEND].getText()
                    stock_dividend = tds[INDEX_STOCK_DIVIDEND].getText()
                    eps = tds[INDEX_EPS].getText()
                    df_all.loc[stock][KEY_NAME] = name
                    df_all.loc[stock][year+KEY_CASH_DIVIDEND] = cash_dividend
                    df_all.loc[stock][year+KEY_STOCK_DIVIDEND] = stock_dividend

        print('--------------------df_all:')
        print(df_all)

        time.sleep(2)
        print("stock {} got".format(stock))

    df_all.to_csv("{}-{}歷年股利.csv".format(start_year, end_year))
