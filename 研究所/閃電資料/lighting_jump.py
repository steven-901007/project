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
    file_path = data_top_path + "/研究所/閃電資料/lighting_jump/半徑"+ str(dis) + 'km/' + year + '/'+ month
    if not os.path.exists(file_path):
            os.makedirs(file_path)
            print(file_path + " 已建立")
file_set()

##統計計算(mean+2std)
def statistics(a,row):
    if row['SR6'] > row['mean'] + a*row['std']:
        return 1
    else:
        return 0

## 讀取閃電資料
month_path = data_top_path + "/研究所/閃電資料/依測站分類/"+str(dis)+"km/"+year+"/"+month+"/**.csv"
result  =glob.glob(month_path)

for station_path in result:
    # print(station_path)
# station_path = "C:/Users/steve/python_data/研究所/閃電資料/依測站分類/36km/2021/06/88S950.csv"
    station_name = station_path[55:61]
    print(station_name)

    data = pd.read_csv(station_path)
    # print(data['data time'])

    data['data time'] = pd.to_datetime(data['data time']).dt.floor('min')
    data['if_lj_time'] = data['data time'] + pd.Timedelta(minutes=10)
    # print(data)


    ##計算某個SR裡的數值
    def count_funtion(SR_time_late,row):
        start_time = row['data time'] + pd.Timedelta(minutes=int(SR_time_late)-1)
        end_time = start_time + pd.Timedelta(minutes=5)

        return ((data['data time'] >= start_time) & (data['data time'] < end_time)).sum()

    #建立SR1~6
    for SR in tqdm(range(1,7),desc='建立SR1~6'):
        data['SR' + str(SR)] = data.apply(lambda row: count_funtion(SR, row), axis=1)

    #刪除SR1 ～SR5 任意比 = 0的資料
    # print(data[(data[['SR1', 'SR2', 'SR3', 'SR4', 'SR5']] == 0).any(axis=1)])
    # print(data)
    data = data[(data[['SR1', 'SR2', 'SR3', 'SR4', 'SR5']] != 0).all(axis=1)]
    #計算mean and std
    data['mean'] = data[['SR1', 'SR2', 'SR3', 'SR4', 'SR5']].mean(axis=1)
    data['std'] = data[['SR1', 'SR2', 'SR3', 'SR4', 'SR5']].std(ddof=0,axis=1)
    # print(data)


    data['lighting_jump_or_not'] = data.apply(lambda row: statistics(alpha, row), axis=1)
    # print(data[data['if_lj_time']=='2021-06-01 12:26:00'])
    # print(data[data['lighting_jump_or_not'] == 1])

    ##挑選存檔部分(if_lj_time)

    data_to_save = {
        'LJ_time' : data['if_lj_time'][data['lighting_jump_or_not'] == 1]
    }
    pd.DataFrame(data_to_save).to_csv(data_top_path + "/研究所/閃電資料/lighting_jump/半徑"+ str(dis) + 'km/' + year + '/'+ month + '/' + station_name + '.csv',index=False)

end_time = T.time()
# 計算執行時間
elapsed_time = end_time - start_time

# 將執行時間轉換為小時、分鐘和秒
hours, rem = divmod(elapsed_time, 3600)
minutes, seconds = divmod(rem, 60)

# 打印執行時間
print('程式執行了{}小時{}分{}秒'.format(int(hours), int(minutes), int(seconds)))