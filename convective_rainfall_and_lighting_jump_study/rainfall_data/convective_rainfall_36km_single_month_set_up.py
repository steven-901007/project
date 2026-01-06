from openpyxl import load_workbook
from glob import glob
import re
import pandas as pd
import os
from tqdm import tqdm

import sys
##變數設定

month =  sys.argv[2] if len(sys.argv) > 1 else "11" 
year = sys.argv[1] if len(sys.argv) > 1 else '2024'
dis = 36

import platform
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"

def fileset(path):    #建立資料夾
    import os
    
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 



def rain_station_location_data_to_list(data_top_path,year,month):## 讀取雨量站經緯度資料
    import pandas as pd
    data_path = f"{data_top_path}/rain_data/station_data/{year}_{month}.csv"
    data = pd.read_csv(data_path)
    station_data_name = data['station name'].to_list()
    station_real_data_name = data['station real name'].to_list()
    lon_data = data['lon'].to_list()
    lat_data = data['lat'].to_list()
    # print(data)
    return station_data_name,station_real_data_name,lon_data,lat_data

station_data_name,station_real_data_name,lon_data,lat_data = rain_station_location_data_to_list(data_top_path,year,month)

file_path = f"{data_top_path}/rain_data/CR_{dis}km/{year}/{month}"
fileset(file_path)



# #儲存list
rain_data_36km_station_list_list = [[] for i in range(len(station_data_name))] ##二階list
# print(rain_data_36km_sta_list_list)

rain_data_paths = f"{data_top_path}/rain_data/rainfall_data/{year}/{month}/**.csv"
result = glob(rain_data_paths)
for rain_data_path in tqdm(result,desc='資料讀取中'):
# rain_data_path = result[0]
    time = os.path.basename(rain_data_path).split('.')[0]
    # print(time)
    rain_datas = pd.read_csv(rain_data_path, dtype=str)
    # print(rain_datas)
    for index, row in rain_datas.iterrows():
        rain_data_rainfall = float(row['rain data'])
        if rain_data_rainfall >= 10:
            rain_data_station_name = row['station name']
            # print(row['station name'])
            rain_data_station_path=  f"{data_top_path}/rain_data/station_count_in_range/{year}_{month}/{rain_data_station_name}.csv"
            rain_data_stations = pd.read_csv(rain_data_station_path)
            # print(rain_data_stations)
            for rain_data in rain_data_stations['station name']:
                # print(rain_data)
                if rain_data_36km_station_list_list[station_data_name.index(rain_data)].count(time) == 0:
                    rain_data_36km_station_list_list[station_data_name.index(rain_data)].append(time)





##資料建立
for station in tqdm(range(len(rain_data_36km_station_list_list)),desc='資料建立'):
    if rain_data_36km_station_list_list[station] != []:
        save_data = pd.DataFrame({
            'time data': rain_data_36km_station_list_list[station]
        })
        save_data['time data'] = pd.to_datetime(save_data['time data'], format='%Y%m%d%H%M', errors='coerce')
        save_data = save_data.dropna(subset=['time data'])
        save_data['time data'] = save_data['time data'].dt.strftime('%Y/%m/%d %H:%M')


        save_path = f"{data_top_path}/rain_data/CR_{dis}km/{year}/{month}/{station_data_name[station]}.csv"
        pd.DataFrame(save_data, dtype=str).to_csv(save_path,index=False)

from datetime import datetime
now_time = datetime.now()
formatted_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
print(f"{formatted_time} 完成 {year}/{month}")