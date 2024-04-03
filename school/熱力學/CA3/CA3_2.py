import netCDF4 as nc
import glob
import re
from openpyxl import Workbook
import numpy as np
import os
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
# map file
def locate(list,number):
    return np.abs(list-number).argmin()

def map(path,latitude,longitude):

    map_file_path =path
    map = nc.Dataset(map_file_path)
    # print(map)



    # map data
    lat = map.variables["lat"][:]
    lon = map.variables["lon"][:]

    # 指定經緯度的值
    latitude = latitude
    longitude = longitude

    # 找到最接近指定經緯度值的索引
    y = locate(lat, latitude)  # south_north
    x = locate(lon, longitude)  # west_east
    # print(lat[y],lon[x])
    # print(lat)
    return x , y

map_file_path = "C:/Users/steve/python_data/thermodynamics/TOPO.nc"
x,y = map(map_file_path,24.56457,120.82458)    #苗栗座標
# print(x,y)    


#pressure
def pressure(path):
    pressure_file_path = path

    delimiter_pattern = re.compile(r'\s+|\n|\   ')
    pressure_data = []
    with open(pressure_file_path, 'r') as file:
        for line in file:
            data = re.split(delimiter_pattern, line.strip())
            # print(data) #以列表顯示
            try:
                pressure_data.append(round(float(data[1])/100,3))
            except:pass
    # pressure_data.remove(pressure_data[0])
    # print(len(pressure_data))
    # print(pressure_data)    #從第一層到第70層
    return pressure_data
P_list = pressure("C:/Users/steve/python_data/thermodynamics/pressure.txt")  #[pa]
# print(P_list)    


#density
def ro(path):
    ro_file_path = path
    delimiter_pattern = re.compile(r'\s+|\n|\   ')
    ro_data = []
    with open(ro_file_path, 'r') as file:
        for line in file:
            data = re.split(delimiter_pattern, line.strip())
            # print(data) #以列表顯示
            try:
                ro_data.append(data[1])
            except:pass
    ro_data.remove(ro_data[0])
    # print(len(ro_data))
    # print(ro_data)    #從第一層到第70層
    return ro_data
ro_list = ro("C:/Users/steve/python_data/thermodynamics/density.txt")  #[pa]
# print(ro_list)    
   

#Rv
Rv = 287


#g
g = 9.8



thermodynamics_folder = "C:/Users/steve/python_data/thermodynamics/Thermodynamic/"
thermodynamics_file_path = thermodynamics_folder+'tpe20110802cln.L.Thermodynamic-000084.nc'
thrermodynamics_data = nc.Dataset(thermodynamics_file_path)



#Tv
specific_humidity = thrermodynamics_data.variables["qv"][0]
hight = thrermodynamics_data.variables["zc"]
Tv_list = []
hight_list = []
# print(len(specific_humidity))
# print(len(P_list))


# data set + 將無效資料去除 qv = 0
for i in range(len(specific_humidity)):
    qv = specific_humidity[i][y][x]
    Tv = round(float(P_list[i])/(float(ro_list[i])*Rv),5)
    if qv != 0:
        Tv_list.append(Tv)
        hight_list.append(int(hight[i]))
    else:
        P_list[i] = -999
# print(Tv_list)
# print(len(Tv_list))
# print(hight_list)
# print(P_list)


while P_list.count(-999) != 0:
    P_list.remove(-999)
    # Sd_list.remove(-999)
    # hight_list.remove(-999)
    # Temperature_list.remove(-999)
# print(P_list)
    

#detail P count by Tv and hight
detail_P_list = [P_list[0]*100]
for i in range(len(P_list)-1):
    # print(i)
    delta_Z = float(hight_list[i+1])-float(hight_list[i])
    # print(delta_Z)
    delta_P = -delta_Z*float(ro_list[i])*g
    P = round(delta_P + detail_P_list[i],3)
    detail_P_list.append(round(P,3))
    print(delta_P/delta_Z/delta_Z)
    
    # print(Tv)
for i in range(len(detail_P_list)):
    detail_P_list[i] = round(float(detail_P_list[i])/100,2)
# print(detail_P_list)
# print(len(detail_P_list))
# print(ro_list)
# print(P_list[0])

for i in range(len(hight_list)):
    hight_list[i] = hight_list[i]/1000


#再次去除無效資料 p<0
for i in range(len(detail_P_list)):
    if detail_P_list[i]<0:
        detail_P_list[i] = -999
        hight_list[i] = -999

while detail_P_list.count(-999) != 0:
    detail_P_list.remove(-999)
    hight_list.remove(-999)


plt.rcParams['font.sans-serif'] = [u'MingLiu'] #細明體
plt.rcParams['axes.unicode_minus'] = False 
fig = plt.figure()
ax = fig.add_subplot()

ax.plot(detail_P_list,hight_list,color ='black',lw = 1)


#average data and draw
color_bar = ['b','g','y','pink','orange']
data_set_list = [3,5,7,10,70]
# color_bar = ['b']
# data_set_list = [3]
for set in range(len(data_set_list)):
    # print(set)
    set_size = data_set_list[set]
    new_detail_P_list = []

    for data in range(0,len(detail_P_list),set_size):
        sum_number = 0
        count = 0
        for size in range(data,data+set_size):
            # print(size)
            try:
                sum_number += detail_P_list[size]
                count += 1
            except:
                pass
        # print(data)
        # plt.axhline(hight_list[data],c = "r" , ls = "--" , lw = 0.3) #水平輔助線
        # print(count)
        # print(sum_number)
        average_number =round(sum_number/count,3)
        # print(average_number)
        for i in range(data,data+count):
            new_detail_P_list.append(average_number)
    # print(new_detail_P_list)
    # print(len(new_detail_P_list))
    ax.plot(new_detail_P_list,hight_list,color =color_bar[set],lw = 1,label = 'average for every '+str(set_size)+' data')
        



hight_tick_set_list = [hight_list[0]]
for i in range(0,round(max(hight_list))-round(min(hight_list))+1,2):
    hight_tick_set_list.append(i+1)
hight_tick_set_list.remove(max(hight_tick_set_list))
hight_tick_set_list.append(max(hight_list))

ax.set_ylim(hight_list[0])
ax.set_xlim(detail_P_list[len(detail_P_list)-1])
ax.set_yticks(hight_tick_set_list)
plt.ylabel('Height[km]',fontsize = 20)
plt.xlabel('pressure [hpa]',fontsize = 20)
plt.legend()
plt.title('2011/08/02 14:00\n地點:苗栗站\n (120.82458 E,24.56457 N)')
plt.show()