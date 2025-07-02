import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from datetime import datetime


year = '2021' #年分
month = '09' #月份
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
dis = 36 #半徑
title_name_time = 'Time'
data_time_zone = 'LCT' #LCT or UTC


# 建立資料夾
def file_set(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print(file_path + " 已建立")

file_set(f"{data_top_path}/flash_data/EN/sort_by_time/EN_{year}{month}_{dis}km")

# Haversine公式，用於計算兩點之間的球面距離（經緯度）
def haversine(lon1, lat1, lon2, lat2):
    # 將度轉換為弧度
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # Haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    # 地球半徑（公里）
    r = 6371
    return c * r

# 讀取flash_data並轉換日期時間格式
flash_rawdata_df = pd.read_csv(f"{data_top_path}/flash_data/raw_data/EN/{year}_EN/{year}{month}.csv")
flash_datas_df = flash_rawdata_df[[title_name_time, 'lon', 'lat']].copy()

flash_datas_df[title_name_time] = pd.to_datetime(flash_datas_df[title_name_time]).dt.floor('min')

# 讀取測站資料
station_datas_path = f"{data_top_path}/雨量資料/測站資料/{year}_{month}.csv"
station_datas = pd.read_csv(station_datas_path)

# 遍歷測站，計算距離並保存結果
for index, row in tqdm(station_datas.iterrows()):

    station_name = row['station name']
    station_lon = row['lon']
    station_lat = row['lat']

    # 計算每個閃電點與測站的距離
    flash_datas_df['distance'] = haversine(flash_datas_df['lon'], flash_datas_df['lat'], station_lon, station_lat)

    # 過濾掉距離超過36公里的flash_data
    need_flash_datas_df = flash_datas_df[flash_datas_df['distance'] <= dis]

    # 計算每分鐘內的閃電次數
    need_inf_flash_data_df = need_flash_datas_df.groupby(title_name_time).size().reset_index(name='flash_count')
    need_inf_flash_data_df.columns = ['data time','flash_count']

    if data_time_zone == 'UTC':
        need_inf_flash_data_df['data time'] = need_inf_flash_data_df['data time'] + pd.Timedelta(hours=8) #UTC ==> LCT

    save_path = f"{data_top_path}/flash_data/EN/sort_by_time/EN_{year}{month}_{dis}km/{station_name}.csv"
    need_inf_flash_data_df.to_csv(save_path,index=False)  


now_time = datetime.now()
formatted_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
print(f"{formatted_time} 完成 Time：{year}/{month}、dis：{dis} ,time zone = {data_time_zone}")