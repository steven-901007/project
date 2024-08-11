import pandas as pd


year = '2021' #年分
month = '06' #月份
# data_top_path = "C:/Users/steve/python_data"
data_top_path = "C:/Users/steven.LAPTOP-8A1BDJC6/OneDrive/桌面"
dis = 36

station = '466920'


tg_station_data_path = f"C:/Users/steve/python_data/研究所/雨量資料/{year}測站資料.csv"

data_path = f"{data_top_path}/研究所/雨量資料/{str(dis)}km個案分析/{month}/{station}/{station}_rain_data.xlsx"
datas = pd.read_excel(data_path)
print(datas)
