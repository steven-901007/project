##前估
import os
from openpyxl import load_workbook
import glob
import datetime
import pandas as pd
import re
import math
from tqdm import tqdm





def haversine(lat1, lon1, lat2, lon2): #經緯度距離
    # 地球的半徑（公里）
    R = 6371.0

    # 將經緯度從度轉換為弧度
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # 經緯度差
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine公式
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # 計算距離
    distance = R * c

    return distance

def fileset(path):    #建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 

def case_data_set(year,month,day,time_start,time_end,dis,station_name,data_top_path):

    #測站經緯度and36km的測站有哪些
    stations_name_for_36km_path = f"{data_top_path}/雨量資料/測站範圍內測站數/{year}_{month}/{station_name}.csv"
    stations_name_for_36km_pd = pd.read_csv(stations_name_for_36km_path)
    # print(stations_name_for_36km_pd)


    ## 建立資料夾
    case_root_path = f"{data_top_path}/個案分析/{station_name}_{dis}_{year}{month}{day}_{str(time_start).zfill(2)}00to{str(time_end).zfill(2)}00"
    fileset(case_root_path)

    # time_start = datetime.datetime(time_start,0)
    # time_end = datetime.datetime(time_end,0)
    #將時間的type改成時間型態
    time_start = datetime.datetime(int(year),int(month),int(day),time_start)
    time_end = datetime.datetime(int(year),int(month),int(day),time_end)
    # print(time_start,time_end)


    ##雨量raw data建立
    rain_paths = f"{data_top_path}/雨量資料/降雨data/{year}/{month}/**"
    rain_file_paths  =glob.glob(rain_paths)
    # print(rain_file_paths)
    rain_data_save_datas = pd.DataFrame()
    for rain_path in tqdm(rain_file_paths,desc='雨量raw data讀取'):
        time_str = rain_path.split('/')[-1].split('\\')[-1].split('.')[0]
        # print(time_str)
        file_time = datetime.datetime.strptime(time_str, '%Y%m%d%H%M')
        # print(file_time)
        if time_start <= file_time < time_end:
            # print(rain_path)
            rain_datas = pd.read_csv(rain_path)
            stations_name_for_36km_pd['station name'] = stations_name_for_36km_pd['station name'].astype(str)
            rain_datas['station name'] = rain_datas['station name'].astype(str)

            union_datas = pd.merge(stations_name_for_36km_pd,rain_datas, on='station name', how='inner')
            # print(stations_name_for_36km_pd)
            # print(rain_datas)
            # print(stations_name_for_36km_pd.info())
            # print(rain_datas.info())
            union_datas['data time'] = file_time
            union_datas = union_datas[['data time', 'station name', 'rain data']]
            # print(union_datas)
            # print(rain_datas)
            rain_data_save_datas = pd.concat([rain_data_save_datas, union_datas], axis=0, ignore_index=True)

    rain_data_save_path = case_root_path + '/rain_raw_data.csv'
    pd.DataFrame(rain_data_save_datas).to_csv(rain_data_save_path,index=False)
    print('雨量資料已建立')


    ##閃電資料建立(讀取依測站分類)
    flash_path = f"{data_top_path}/閃電資料/依測站分類/{year}_{month}_{dis}km/{station_name}.csv"
    flash_data = pd.read_csv(flash_path)
    flash_data['data time'] = pd.to_datetime(flash_data['data time'])
    # print(flash_data['data time'])
    save_data = flash_data[(flash_data['data time'] >= time_start) & 
                        (flash_data['data time'] < time_end)]
    # print(save_data)
    flash_data_save_path = case_root_path + '/flash_data.csv'
    save_data.to_csv(flash_data_save_path,index=False)
    print('閃電資料已建立')


# # # ## 變數設定
# data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
# year = '2021' #年分
# month = '06' #月份
# day = '04'
# time_start = 12
# time_end = 18
# dis = 36
# alpha = 2 #統計檢定
# # station_name = 'C0F9N0'
# # station_name = 'C0V800' #六龜
# station_name = '466920' #台北


# case_data_set(year,month,day,time_start,time_end,dis,station_name,data_top_path)
