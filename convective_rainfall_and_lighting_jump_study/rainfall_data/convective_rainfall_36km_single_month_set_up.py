from openpyxl import load_workbook
from glob import glob
import re
import pandas as pd
import os
from tqdm import tqdm
import importset


year = '2021' #年分
month = '07' #月份
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
dis = 36

station_data_name,station_real_data_name,lon_data,lat_data = importset.rain_station_location_data_to_list(data_top_path,year,month)

file_path = f"{data_top_path}/雨量資料/對流性降雨{dis}km/{year}/{month}"
importset.fileset(file_path)



# #儲存list
rain_data_36km_station_list_list = [[] for i in range(len(station_data_name))] ##二階list
# print(rain_data_36km_sta_list_list)

rain_data_paths = f"{data_top_path}/雨量資料/降雨data/{year}/{month}/**.csv"
result = glob(rain_data_paths)
for rain_data_path in tqdm(result,desc='資料讀取中'):
# rain_data_path = result[0]
    time = rain_data_path.split('\\')[-1].split('.')[0]
    # print(time)
    rain_datas = pd.read_csv(rain_data_path, dtype=str)
    # print(rain_datas)
    for index, row in rain_datas.iterrows():
        rain_data_rainfall = float(row['rain data'])
        if rain_data_rainfall >= 10:
            rain_data_station_name = row['station name']
            # print(row['station name'])
            rain_data_station_path=  f"{data_top_path}/雨量資料/測站範圍內測站數/{year}_{month}/{rain_data_station_name}.csv"
            rain_data_stations = pd.read_csv(rain_data_station_path)
            # print(rain_data_stations)
            for rain_data in rain_data_stations['station name']:
                # print(rain_data)
                if rain_data_36km_station_list_list[station_data_name.index(rain_data)].count(time) == 0:
                    rain_data_36km_station_list_list[station_data_name.index(rain_data)].append(time)





##資料建立
for station in tqdm(range(len(rain_data_36km_station_list_list)),desc='資料建立'):
    if rain_data_36km_station_list_list[station] != []:
        save_data = {
            'time data':rain_data_36km_station_list_list[station]
        }
        save_data['time data'] = pd.to_datetime(save_data['time data']).strftime('%Y/%m/%d %H:%M')

        save_path = f"{data_top_path}/雨量資料/對流性降雨{dis}km/{year}/{month}/{station_data_name[station]}.csv"
        pd.DataFrame(save_data, dtype=str).to_csv(save_path,index=False)