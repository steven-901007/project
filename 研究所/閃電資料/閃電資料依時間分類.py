import os
import re
import calendar
import csv
from tqdm import tqdm
year = '2021' #年分
month = '06' #月份
data_top_path = "C:/Users/steve/python_data"



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


fileset(data_top_path + "/研究所/閃電資料/依時間分類/"+year+ '/' + month)

last_day = calendar.monthrange(int(year),int(month))[1]
# print(last_day)

for dd in tqdm(range(1,last_day+1),desc = '寫入資料'):
    dd = str(dd).zfill(2)

    for HH in range(24):
        HH = str(HH).zfill(2)

        for MM in range(60):
            MM = str(MM).zfill(2)
            day = year+month+dd+HH+MM

            csv_file_path = data_top_path + "/研究所/閃電資料/依時間分類/"+year+ '/' + month + '/' + day + '.csv'

            data = []

            if simple_t_list.count(day) != 0:
                data.append(['lon','lat'])
                
            for data_nb in range(simple_t_list.count(day)):
                data.append([raw_data_lon_list[data_nb],raw_data_lat_list[data_nb]])

            with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(data)
            file.close()