import math
from datetime import datetime, timedelta
from tqdm import tqdm ##跑進度條的好玩東西
import pandas as pd
import time as T
import glob
import os

year = '2021' #年分
month = '06' #月份
data_top_path = "C:/Users/steve/python_data"
alpha = 2 #統計檢定
dis = 36 #半徑


start_time = T.time()

##建立資料夾
def file_set():
    file_path = data_top_path + "/研究所/閃電資料/lighting_jump/" + month
    if not os.path.exists(file_path):
            os.makedirs(file_path)
            print(file_path + " 已建立")
file_set()

## 讀取閃電資料
month_path = data_top_path + "/研究所/閃電資料/依測站分類/"+str(dis)+"km/"+year+"/"+month+"/**.csv"
result  =glob.glob(month_path)

for station_path in result:
    # print(station_path)

    station_name = station_path[67:73]
    print(station_name)

    data = pd.read_csv(station_path)
    # print(data)
    data['yyyymmddHHMM'] = pd.to_datetime(data["yyyymmddHHMM"] ,format='%Y%m%d%H%M')
    data['if_lj_time_yyyymmddHHMM'] = data['yyyymmddHHMM'] + pd.Timedelta(minutes=10)

    ##計算某個SR裡的數值
    def count_funtion(SR_time_late,row):
        start_time = row['yyyymmddHHMM'] + pd.Timedelta(minutes=int(SR_time_late)-1)
        end_time = start_time + pd.Timedelta(minutes=5)

        return ((data['yyyymmddHHMM'] >= start_time) & (data['yyyymmddHHMM'] < end_time)).sum()

    #建立SR1~6
    for SR in tqdm(range(1,7),desc='建立SR1~6'):
        data['SR' + str(SR)] = data.apply(lambda row: count_funtion(SR, row), axis=1)

    #計算mean and std
    data['mean'] = data[['SR1', 'SR2', 'SR3', 'SR4', 'SR5']].mean(axis=1)
    data['std'] = data[['SR1', 'SR2', 'SR3', 'SR4', 'SR5']].std(axis=1)
    # print(data)

    ##統計計算(mean+2std)
    def statistics(a,row):
        if row['SR6'] > row['mean'] + a*row['std']:
            return 1
        else:
            return 0
    data['lighting_jump_or_not'] = data.apply(lambda row: statistics(alpha, row), axis=1)
    # print(data['if_lj_time_yyyymmddHHMM'][data['lighting_jump_or_not'] == 1])

    ##挑選存檔部分(if_lj_time_yyyymmddHHMM)

    data_to_save = {
        'LJ_time' : data['if_lj_time_yyyymmddHHMM'][data['lighting_jump_or_not'] == 1]
    }
    pd.DataFrame(data_to_save).to_csv(data_top_path + "/研究所/閃電資料/lighting_jump/"  + month + '/' + station_name + '.csv',index=False)

end_time = T.time()
# 計算執行時間
elapsed_time = end_time - start_time

# 將執行時間轉換為小時、分鐘和秒
hours, rem = divmod(elapsed_time, 3600)
minutes, seconds = divmod(rem, 60)

# 打印執行時間
print('程式執行了{}小時{}分{}秒'.format(int(hours), int(minutes), int(seconds)))