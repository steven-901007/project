from openpyxl import Workbook,load_workbook
import math
import re
from datetime import datetime, timedelta
import statistics
from tqdm import tqdm ##跑進度條的好玩東西
import pandas as pd
from geopy.distance import geodesic



year = '2021' #年分
month = '06' #月份
data_top_path = "C:/Users/steve/python_data"
alpha = 2 #統計檢定


## 讀取雨量站經緯度資料
def rain_station_location_data():
    data_path = data_top_path+"/研究所/雨量資料/"+year+"測站範圍內測站數.xlsx"
    lon_data_list = []  # 經度
    lat_data_list = []  # 緯度
    name_data_list = []  #測站名稱
    wb = load_workbook(data_path)
    ws = wb[month]
    for i in range(ws.max_column):
        lon_data_list.append(ws.cell(3,i+1).value)
        lat_data_list.append(ws.cell(2,i+1).value)
        name_data_list.append(ws.cell(1,i+1).value)
    wb.close()
    return lon_data_list, lat_data_list ,name_data_list
lon_data_list, lat_data_list ,name_data_list = rain_station_location_data()


## 兩經緯度距離
def haversine(lat1, lon1, lat2, lon2):
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


## 與測站距離<36 km的有那些
dis = 36


## 建立存檔位置
wb_lighting_jump = Workbook()
ws_lighting_jump = wb_lighting_jump.active
ws_lighting_jump.title = month


## 讀取閃電資料
flash_data_path = data_top_path+'/研究所/閃電資料/raw_data/'+year+'/'+year+month+'.txt'
flash_rawdata = pd.read_csv(flash_data_path,header = 0)
flash_rawdata['simple_time'] = flash_rawdata['日期時間'].str[:4] + flash_rawdata['日期時間'].str[5:7] + flash_rawdata['日期時間'].str[8:10] + flash_rawdata['日期時間'].str[11:13] + flash_rawdata['日期時間'].str[14:16]
# print(flash_rawdata['simple_time'],flash_rawdata['經度'],flash_rawdata['緯度'])


row = 1
# for station_name in name_data_list:
station_name = name_data_list[0]

ws_lighting_jump.cell(row,1).value = station_name
col = 2

station_lon = lon_data_list[name_data_list.index(station_name)]
station_lat = lat_data_list[name_data_list.index(station_name)]
station_lat_lon = (station_lat,station_lon)
# print(station_name,station_lon,station_lat)

flash_data_time_list = []

flash_rawdata['distance_km'] = flash_rawdata.apply(lambda row: geodesic((row['緯度'], row['經度']), station_lat_lon).km, axis=1)
# print(flash_rawdata)

target_data = flash_rawdata[flash_rawdata['distance_km'] < dis].reset_index(drop=True)# 篩選距離小於dis的數據並重置索引

# 計算simple_time的出現次數
simple_time_counts = target_data['simple_time'].value_counts().reset_index()
simple_time_counts.columns = ['simple_time', 'count']

target_data = target_data.merge(simple_time_counts, on='simple_time', how='left')# 將計算的次數合併回target_data

target_data_simple_time = target_data.drop_duplicates(subset=['simple_time'])# 移除simple_time重複的數據，保留首次出現的行

print(target_data_simple_time)



for time in tqdm(flash_data_time_unique_list):
    # print(time)
    SR_list = []
    time_dt = datetime.strptime(time, "%Y-%m-%d %H:%M")

    for start in range(6):
        start_time_dt = time_dt + timedelta(minutes=start)
        end_time_dt = start_time_dt + timedelta(minutes=5)
        # print(start_time_dt,end_time_dt)

        flash_sum_for_SR = 0
        for chack_time in range(len(flash_data_time_unique_list)):
            chack_time_dt = datetime.strptime(flash_data_time_unique_list[chack_time], "%Y-%m-%d %H:%M")

            if start_time_dt <= chack_time_dt < end_time_dt:
                flash_sum_for_SR += flash_data_time_count_list[chack_time]
        SR_list.append(flash_sum_for_SR)
    # print(SR_list)
    SR_1_5_list = SR_list[:5]
    SR_6 = SR_list[5]

    if SR_1_5_list.count(0) == 0:
        SR_1_5_mean = statistics.mean(SR_1_5_list)
        SR_1_5_std = statistics.pstdev(SR_1_5_list)

        if SR_6 > SR_1_5_mean + alpha*SR_1_5_std:
            # print(time)
            ws_lighting_jump.cell(row,col).value = time
            col += 1
row += 1





#     wb_lighting_jump.save(data_top_path+"/研究所/閃電資料/lighting_jump/"+year+'_'+month+'_lighting_jump.xlsx')    
# print('已建立' +data_top_path+"/研究所/閃電資料/lighting_jump/"+year+'_'+month+'_lighting_jump.xlsx')