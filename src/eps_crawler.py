import configparser
from urllib.request import urlopen
import json
import pandas as pd
import os
import time
import requests
import zipfile

KEY_CODE = 'Code'
KEY_NAME = 'Name'
KEY_EPS_THIS_SEASON = 'Eps_this_season'

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
    season_query_strings = []

    if end_year < start_year:
        print("End year cannot be less than start year, please modify your config.")
        exit()

    if end_year == start_year:
        if season_str_list.index(end_season) < season_str_list.index(start_season):
            print("End season cannot be less than start season, please modify your config.")
            exit()
        else :
            if season_str_list.index(end_season) == season_str_list.index(start_season):
                season_query_strings.append(start_year+start_season)
            else :
                for i in range(season_str_list.index(start_season), season_str_list.index(end_season)+1):
                    season_query_strings.append(start_year+season_str_list[i])
    else :
        for i in range(season_str_list.index(start_season), season_str_list.index("Q4")+1):
            season_query_strings.append(start_year+season_str_list[i])

        for year in range(int(start_year)+1, int(end_year)):
            for season in season_str_list:
                season_query_strings.append(str(year)+season)

        for i in range(season_str_list.index("Q1"), season_str_list.index(end_season)+1):
            season_query_strings.append(end_year+season_str_list[i])

    df_all = pd.DataFrame([], columns=[KEY_NAME] + season_query_strings, index=stock_str_list)

    for season_str in season_query_strings:
        # check whether the financial info zipfile of this season exists
        filename = './' + season_str + '_C05001.zip'
        exist = os.path.isfile(filename)
        if not exist:
            url = 'https://www.twse.com.tw/statistics/count?url=/staticFiles/inspection/inspection/05/001/{}.zip'.format(season_str+'_C05001')
            resp = requests.get(url)
            if resp.status_code == requests.codes.ok:
                print(season_str + '_C05001.zip' + ' downloaded.')
                with open(filename, 'wb') as f:
                    f.write(resp.content)
                time.sleep(2)
            else :
                print(season_str + '_C05001.zip' + ' download failed.')
        else:
            print(season_str + '_C05001.zip' + ' already exists.')

    for season_str in season_query_strings:
        # check whether the financial zip file is extracted
        filename = './' + season_str + '.xls'
        exist = os.path.isfile(filename)
        if not exist:
            zip_filename = './' + season_str + '_C05001.zip'
            with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                print('extract file ' + zip_filename)
                zip_ref.extractall('./')
        else : 
            print('excel file ' + filename + 'already exits')
        
        excel_filename = './' + season_str + '.xls'
        df = pd.read_excel (excel_filename)
        df = df.rename(columns={'Unnamed: 0':KEY_CODE, 'Unnamed: 1':KEY_NAME, 'Unnamed: 13':KEY_EPS_THIS_SEASON})
        print("xls read: " + excel_filename)
        results = df.loc[df[KEY_CODE].isin(stock_str_list)]
#        print(results.loc[:, [KEY_CODE, KEY_NAME, KEY_EPS_THIS_SEASON]])
        for index, row in results.iterrows():
            df_all.loc[row[KEY_CODE]][season_str] = row[KEY_EPS_THIS_SEASON]
            df_all.loc[row[KEY_CODE]][KEY_NAME] = row[KEY_NAME]

#    print(df_all)
    df_all.to_csv('EPS_from_{}_to_{}.csv'.format(season_query_strings[0], season_query_strings[-1]))
#        exit()
