import glob
import re
import math

year = '2021' #年分
month = '06' #月份

rain_data_path = "C:/Users/steve/python_data/研究所/雨量資料/2021_06/06/20210629/202106290930.QPESUMS_GAUGE.10M.mdf"
hour = rain_data_path[64:66]
minute  =rain_data_path[66:68]
# print(minute)


## 每日資料處理
data_hour_lat_list = [] 
data_hour_lon_list = []
data_hour_rain_list = [] #降雨量
location_of_rain_more_then_10 = []
line = 0
with open(rain_data_path, 'r') as files:
    for file in files:
        elements = re.split(re.compile(r'\s+|\n|\*'),file.strip())
        # print(elements)
        # print(len(elements))
        if line >= 3 :
            data_hour_lat_list.append(elements[3])
            data_hour_lon_list.append(elements[4])
            rain_data = float(elements[7]) #MIN_10
            if rain_data >= 0:
                data_hour_rain_list.append(rain_data)

                if rain_data >=10:
                    location = elements[0]
                    
                    print(elements[0]+'  '+str(rain_data))
            else:
                data_hour_rain_list.append(0)
        line += 1
