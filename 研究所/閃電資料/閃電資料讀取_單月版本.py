import re
import os
import glob
import pandas as pd

year = '2021'
month = '01'  

flash_time_list = []
flash_lon_list = []
flash_lat_list = []
flash_ic_or_cg = []


data_path = 'C:/Users/steve/python_data/研究所/閃電資料/'+year+'/'+year+month+'.txt'
# result  =glob.glob(path)
# for data_path in result:
#     # f = os.path.basename(f) #單純輸出檔案名稱
#     print(data_path)

delimiter_pattern = re.compile(r',|\n') #當資料分隔符號有"空行"or"空白"or"*"等多個符號時使用
try:
    with open(data_path, 'r',encoding='utf-8') as file:
        for line in file:
            # 使用正則表達式來分割每一行
            elements = re.split(delimiter_pattern, line.strip())
            # print(elements) #以列表顯示
            flash_time_list.append(elements[0])
            flash_lon_list.append(elements[2])
            flash_lat_list.append(elements[3])
            flash_ic_or_cg.append(elements[5])
except:
    with open(data_path, 'r') as file:
        for line in file:
            # 使用正則表達式來分割每一行
            elements = re.split(delimiter_pattern, line.strip())
            # print(elements) #以列表顯示
            flash_time_list.append(elements[0])
            flash_lon_list.append(elements[2])
            flash_lat_list.append(elements[3])
            flash_ic_or_cg.append(elements[5])

flash_time_list.pop(0)
flash_lon_list.pop(0)
flash_lat_list.pop(0)
flash_ic_or_cg.pop(0)
print(flash_lon_list,flash_lat_list)


