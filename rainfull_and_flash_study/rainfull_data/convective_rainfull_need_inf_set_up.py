import pandas as pd
import glob
import re
from tqdm import tqdm
import importset
from datetime import datetime, timedelta
year = '2021' #年分
month = '06' #月份
data_top_path = "C:/Users/steve/python_data"


##建立資料夾
file_path = f"{data_top_path}/研究所/雨量資料/對流性降雨data/{year}/{month}/"
importset.fileset(file_path)
## 讀取每月資料


month_path = f"{data_top_path}/研究所/雨量資料/降雨data/{year}/{month}/*"
result  =glob.glob(month_path)
for rain_path in result:
    # print(rain_path)
    time = rain_path.split('/')[-1].split('\\')[-1].split('.')[0]
    # print(time)
    rain_datas = pd.read_csv(rain_path)
    convenctive_rainfull_data = rain_datas[rain_datas['rain data'] >= 10]
    if not convenctive_rainfull_data.empty:
        print(time)
        print(convenctive_rainfull_data)
        save_path = f"{data_top_path}/研究所/雨量資料/對流性降雨data/{year}/{month}/{time}.csv"
        pd.DataFrame(convenctive_rainfull_data).to_csv(save_path,index=False)