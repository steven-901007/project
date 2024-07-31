import sys
import os

import re
import math
import glob
from tqdm import tqdm
import time
import pandas as pd
from geopy.distance import geodesic

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../import_use')))

from import_use import importset


year = '2021' #年分
month = '06' #月份
data_top_path = "C:/Users/steve/python_data"
dis = 36
max_lon = 122.1
min_lon = 120
max_lat = 25.5
min_lat = 21.5
  

def rain_station_location_data(path):
    data_path = path
    lon_data_list = []  # 經度
    lat_data_list = []  # 緯度
    name_data_list = []  #測站名稱
    real_name_data_list = [] #測站實際名稱

    line = 0
    with open(data_path, 'r') as files:
        for file in files:
            if line >=3:
                data = re.split(re.compile(r'\s+|\n|\*'),file.strip())
                # print(data)
                if min_lon <float(data[4])< max_lon and min_lat <float(data[3])< max_lat:
                    lon_data_list.append(float(data[4]))
                    lat_data_list.append(float(data[3]))
                    name_data_list.append(data[0])
                    real_name_data_list.append(data[1])
            line +=1
        files.close()
    
    return lon_data_list, lat_data_list ,name_data_list ,real_name_data_list

importset.fileset(data_top_path+ "/研究所/雨量資料/"+year+"測站範圍內測站數/")
lon_data_list, lat_data_list ,station_name_data_list ,real_name_data_list = [],[],[],[]

##確認所有資料的測站都有被記錄
## 讀取每月資料
month_path = data_top_path+"/研究所/雨量資料/"+year+"_"+month+"/"+month
result  =glob.glob(month_path+"/*")
for day_path in tqdm(result,desc='資料處理中....'):
    # print(day_path)
    day = day_path[53:] #日期
    # print('日期:'+day)

    ## 讀取每日資料
    result  =glob.glob(day_path+'/*')
    for rain_data_path in result:
        # print(rain_data_path)
        lon_list, lat_list ,station_name_list,real_name_list = rain_station_location_data(rain_data_path)
        for i in range(len(station_name_list)):
            if station_name_list[i] == 'C1E890':##rawdata錯誤修改
                lon_list[i] = 120.6718
                lat_list[i] = 24.4652
            if station_name_data_list.count(station_name_list[i]) == 0:
                station_name_data_list.append(station_name_list[i])
                lon_data_list.append(lon_list[i])
                lat_data_list.append(lat_list[i])
                real_name_data_list.append(real_name_list[i])


data = {
    'station name':station_name_data_list,
    'lon':lon_data_list,
    'lat':lat_data_list
}

# for station_name_nb in range(len(station_name_list)):
station_name_nb = 0
station_name = station_name_list[station_name_nb]
real_name = real_name_data_list[station_name_nb]
station_lon = lon_data_list[station_name_nb]
station_lat = lat_data_list[station_name_nb]
station_lat_lon = (station_lat,station_lon)
data['distance_km'] = data.apply(lambda row: geodesic((row['緯度'], row['經度']), station_lat_lon).km, axis=1)
print(data['distance_km'])
