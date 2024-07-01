import os
import re
import calendar
import csv
from tqdm import tqdm
from openpyxl import load_workbook
import math


year = '2021' #年分
month = '06' #月份
data_top_path = "C:/Users/steve/python_data"
dis = 36


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




## 讀取閃電資料
need_t_list = []
t_list = []
simple_t_list = []
raw_data_lon_list = []
raw_data_lat_list = []
data_path = data_top_path+'/研究所/閃電資料/raw_data/'+year+'/'+year+month+'.txt'
delimiter_pattern = re.compile(r',|\n') #當資料分隔符號有"空行"or"空白"or"*"等多個符號時使用
try:
    with open(data_path, 'r',encoding='utf-8') as file:
        next(file)

        for line in file:
            # 使用正則表達式來分割每一行
            elements = re.split(delimiter_pattern, line.strip())
            # print(elements) #以列表顯示
            t = elements[0]
            need_t = t[:len(t)-3]
            simple_t = t[0:4] + t[5:7] + t[8:10] + t[11:13] + t[14:16]  #yyyymmddHHMM
            raw_data_lon = round(float(elements[2]),3)
            raw_data_lat = round(float(elements[3]),3)
            need_t_list.append(need_t)
            simple_t_list.append(simple_t)
            # t_list.append(t)
            raw_data_lon_list.append(raw_data_lon)
            raw_data_lat_list.append(raw_data_lat)
except:
    with open(data_path, 'r') as file:
        next(file)

        for line in file:
            # 使用正則表達式來分割每一行
            elements = re.split(delimiter_pattern, line.strip())
            # print(elements) #以列表顯示
            t = elements[0]
            need_t = t[:len(t)-3]
            simple_t = t[0:4] + t[5:7] + t[8:10] + t[11:13] + t[14:16]  #yyyymmddHHMM
            raw_data_lon = round(float(elements[2]),3)
            raw_data_lat = round(float(elements[3]),3)
            need_t_list.append(need_t)
            simple_t_list.append(simple_t)
            # t_list.append(t)
            raw_data_lon_list.append(raw_data_lon)
            raw_data_lat_list.append(raw_data_lat)

file.close()

# print(simple_t_list)


def fileset(path):    #建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 
    
fileset(data_top_path + "/研究所/閃電資料/依測站分類/"+str(dis)+'km/'+year+ '/' + month)


for station_nb in tqdm(range(len(name_data_list)),desc='寫入資料'):
    data = [['yyyymmddHHMM']]
    csv_file_path = data_top_path + "/研究所/閃電資料/依測站分類/"+str(dis)+'km/'+year+ '/' + month + '/' + year+month+'_'+str(dis)+'km_'+name_data_list[station_nb] + '.csv'
    station_lon = lon_data_list[station_nb]
    station_lat = lat_data_list[station_nb]

    for data_nb in range(len(simple_t_list)):
        data_lon = raw_data_lon_list[data_nb]
        data_lat = raw_data_lat_list[data_nb]
        data_time = simple_t_list[data_nb]

        if haversine(station_lat,station_lon,data_lat,data_lon) < dis:
            data.append([data_time])

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    file.close()