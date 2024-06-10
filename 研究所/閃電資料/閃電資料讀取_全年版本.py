import re
import os
import glob



time_list = []
lon_time_list = []
lat_time_list = []
ic_or_cg = []


path = 'C:/Users/steve/python_data/研究所/閃電資料/2021/*'
result  =glob.glob(path)
for data_path in result:
    # f = os.path.basename(f) #單純輸出檔案名稱
    print(data_path)

    delimiter_pattern = re.compile(r',|\n') #當資料分隔符號有"空行"or"空白"or"*"等多個符號時使用
try:
    with open(data_path, 'r',encoding='utf-8') as file:
        for line in file:
            # 使用正則表達式來分割每一行
            elements = re.split(delimiter_pattern, line.strip())
            # print(elements) #以列表顯示
            time_list.append(elements[0])
            lon_time_list.append(elements[2])
            lat_time_list.append(elements[3])
            ic_or_cg.append(elements[5])
except:
    with open(data_path, 'r') as file:
        for line in file:
            # 使用正則表達式來分割每一行
            elements = re.split(delimiter_pattern, line.strip())
            # print(elements) #以列表顯示
            time_list.append(elements[0])
            lon_time_list.append(elements[2])
            lat_time_list.append(elements[3])
            ic_or_cg.append(elements[5])

print(time_list)