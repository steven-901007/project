import glob
import re
import math

year = '2021' #年分
month = '06' #月份

## 讀取雨量站經緯度資料
def rain_station_location_data():
    data_path = "C:/Users/steve/python_data/研究所/雨量資料/2021_06/06/20210601/202106010000.QPESUMS_GAUGE.10M.mdf"
    lon_data_list = []  # 經度
    lat_data_list = []  # 緯度
    name_data_list = []  #測站名稱

    line = 0
    with open(data_path, 'r') as files:
        for file in files:
            if line >=3:
                data = re.split(re.compile(r'\s+|\n|\*'),file.strip())
                # print(data)
                if 120 <float(data[4])< 122.1 and 21.5 <float(data[3])< 25.5:
                    lon_data_list.append(float(data[4]))
                    lat_data_list.append(float(data[3]))
                    name_data_list.append(data[0])
            line +=1

    return lon_data_list, lat_data_list ,name_data_list

lon_data_list, lat_data_list ,name_data_list = rain_station_location_data()



rain_data_path = "C:/Users/steve/python_data/研究所/雨量資料/2021_06/06/20210629/202106290930.QPESUMS_GAUGE.10M.mdf"
hour = rain_data_path[64:66]
minute  =rain_data_path[66:68]
# print(minute)


## 每日資料處理 rain data >10mm (10min)
data_name_of_station_list = [] 
data_rain_list = [] #降雨量

line = 0
with open(rain_data_path, 'r') as files:
    for file in files:
        elements = re.split(re.compile(r'\s+|\n|\*'),file.strip())
        # print(elements)
        # print(len(elements))
        if line >= 3 :
            station_name = elements[0]
            rain_data_of_10min = float(elements[7]) #MIN_10
            if rain_data_of_10min >= 0: #排除無資料(data = -998.00)
                rain_data_of_3_hour = float(elements[8]) #HOUR_3
                rain_data_of_6_hour = float(elements[9]) #HOUR_6
                rain_data_of_12_hour = float(elements[10]) #HOUR_12
                rain_data_of_24_hour = float(elements[11]) #HOUR_24
                if 10<=rain_data_of_10min <= rain_data_of_3_hour <= rain_data_of_12_hour <= rain_data_of_24_hour: #QC
                    data_rain_list.append(rain_data_of_10min)
                    data_name_of_station_list.append(station_name)
        line += 1

print(data_rain_list,data_name_of_station_list)

