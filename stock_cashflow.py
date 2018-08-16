# 出来高上位50の寄り値と現値を比較し、資金の流出を測る
import pandas as pd 
import requests 
from bs4 import BeautifulSoup
from time import sleep


def make_top50():
	ranking = pd.read_html('https://info.finance.yahoo.co.jp/ranking/?kd=31&mk=1&tm=d&vl=a')[0]
	ranking.index = ranking['コード']
	ranking = ranking.iloc[:-1, [2,3,4,5,8]]

	ranking.columns = ['市場', '名称', '取引時間', '価格', '売買代金']

	return ranking

def make_price(df):
	three_prices = {}

	for code in df.index:
		r = requests.get('https://stocks.finance.yahoo.co.jp/stocks/detail/?code={}.T'.format(code))
		soup = BeautifulSoup(r.text, 'lxml')
		prices = soup.find_all('dd', class_='ymuiEditLink mar0')
		yester_p = float(prices[0].contents[0].text.replace(',', ''))
		open_p = float(prices[1].contents[0].text.replace(',', ''))
		open_time = prices[1].contents[1].text
		high_p = float(prices[2].contents[1].text.replace(',', ''))
		high_time = prices[2].contents[2].text
		low_p = float(prices[3].contents[1].text.replace(',', ''))
		low_time = prices[3].contents[2].text
            
		three_prices['{}'.format(code)]  = [yester_p, open_p, open_time, high_p, high_time, low_p, low_time]
            
		sleep(1)
        
	three_prices = pd.DataFrame(three_prices).T 
	three_prices.columns = ['前日終値', '寄値', '寄り時間', '高値', '高値時間', '安値', '安値時間']  

	return three_prices

def make_data():
	df = make_top50()
	df1 = make_price(df)
	df2 = pd.concat([df, df1], axis=1)
	df2 = df2.sort_values(['売買代金'], ascending=False)
	df2['寄り比'] = pd.to_numeric(df2['価格']) - pd.to_numeric(df2['寄値'])
	df2['寄り比率'] = (pd.to_numeric(df2['価格']) - pd.to_numeric(df2['寄値'])) / pd.to_numeric(df2['寄値']) * 100

	return df2
