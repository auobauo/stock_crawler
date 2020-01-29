import configparser
import json
from bs4 import BeautifulSoup
import pandas as pd
import requests
import time

KEY_NAME = '股名'
INDEX_MONTH = 0
INDEX_INCOME_THIS_MONTH = 7

def get_month_list(year, season):
    l = []
    if season == 'Q1':
        return [ year+'/01', year+'/02', year+'/03']
    elif season == 'Q2':
        return [ year+'/04', year+'/05', year+'/06']
    elif season == 'Q3':
        return [ year+'/07', year+'/08', year+'/09']
    else :
        return [ year+'/10', year+'/11', year+'/12']
    
if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    stock_list = config['Target']['Number']
    stocks = json.loads(config.get("Target","Number"))
    stock_str_list = [str(s) for s in stocks]
    print("stocks: ")
    print(stock_str_list)

    start_time = config['FinancialReport']['start_season']
    end_time = config['FinancialReport']['end_season']

    [start_year, start_season] = start_time.split('/')
    [end_year, end_season] = end_time.split('/')

    season_str_list = ["Q1", "Q2", "Q3", "Q4"]
    month_query_strings = []

    if end_year == start_year:
        if season_str_list.index(end_season) < season_str_list.index(start_season):
            print("End season cannot be less than start season, please modify your config.")
            exit()
        else :
            if season_str_list.index(end_season) == season_str_list.index(start_season):
                month_query_strings = month_query_strings + get_month_list(start_year, start_season)
            else :
                for i in range(season_str_list.index(start_season), season_str_list.index(end_season)+1):
                    month_query_strings = month_query_strings + get_month_list(start_year, season_str_list[i])
    else :
        for i in range(season_str_list.index(start_season), season_str_list.index("Q4")+1):
            month_query_strings = month_query_strings + get_month_list(start_year, season_str_list[i])

        for year in range(int(start_year)+1, int(end_year)):
            for season in season_str_list:
                month_query_strings = month_query_strings + get_month_list(str(year), season)

        for i in range(season_str_list.index("Q1"), season_str_list.index(end_season)+1):
            month_query_strings = month_query_strings + get_month_list(end_year, season_str_list[i])

    df_all = pd.DataFrame([], columns=[KEY_NAME] + month_query_strings, index=stock_str_list)

    for stock in stock_str_list:
        url = 'https://goodinfo.tw/StockInfo/ShowSaleMonChart.asp?STOCK_ID=' + stock
        ## 使用假header
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}
        result = requests.get(url, headers=headers) 
        result.encoding = 'utf8'
        soup = BeautifulSoup(result.text, 'html.parser')
        name = soup.title.getText().split()[1]
        df_all.loc[stock][KEY_NAME] = name
        div = soup.find(id='divSaleMonChartDetail')
        tables = div.find_all('table')
        target_tab = tables[1]

        for tr in target_tab.findAll('tr'):
            tds = tr.findAll('td')
            if tds[INDEX_MONTH].getText() in month_query_strings:
                df_all.loc[stock][tds[INDEX_MONTH].getText()] = tds[INDEX_INCOME_THIS_MONTH].getText()

        print('--------------------df_all:')
        print(df_all)

        time.sleep(2)
        print("stock {} got".format(stock))

    df_all.to_csv("{}-{}歷史營收(億).csv".format(start_year, end_year))
