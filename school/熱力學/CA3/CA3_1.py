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
                pressure_data.append(data[1])
            except:pass
    pressure_data.remove(pressure_data[0])
    # print(len(pressure_data))
    # print(pressure_data)    #從第一層到第70層
    return pressure_data
P_list = pressure("C:/Users/steve/python_data/thermodynamics/pressure.txt")  #[pa]
# print(P_list)    





thermodynamics_folder = "C:/Users/steve/python_data/thermodynamics/Thermodynamic/"
thermodynamics_file_path = thermodynamics_folder+'tpe20110802cln.L.Thermodynamic-000084.nc'
thrermodynamics_data = nc.Dataset(thermodynamics_file_path)
# print(thrermodynamics_data)
# print(thrermodynamics_data.variables["zc"][:])

# Cp
Cp = 1004


# g
g = 9.8


# hight [m]
hight_list = []
hight = thrermodynamics_data.variables["zc"]
for i in range(len(hight)):
    # print(hight[i])
    hight_list.append(int(hight[i]))
# print(hight_list)


#potential temperature & Sd/Cp
Potential_Temperature_list = []
Sd_list = [] # Sd/Cp
Temperature_list = []
potential_temps = thrermodynamics_data.variables["th"][0]
for i in range(len(potential_temps)):
    pt = potential_temps[i][y][x]
    T = round(pt*((float(P_list[i])/100000)**(0.286)),5)
    z = hight_list[i]
    Sd = round((Cp*T + g*z)/Cp,5)
    Sd_list.append(Sd)
    Potential_Temperature_list.append(pt)
    Temperature_list.append(T)
    # print(potential_temps[i][y][x])  #potential temp
# print(Potential_Temperature_list)
# print(len(Potential_Temperature_list))
# print(Sd_list)


#選取有效資料 + 高度單位轉換
specific_humidity = thrermodynamics_data.variables["qv"][0]
for i in range(len(specific_humidity)):
    qv = specific_humidity[i][y][x]
    if qv == 0:
        Potential_Temperature_list[i] = -999
        Sd_list[i] = -999
        hight_list[i] = -999
        Temperature_list[i] = -999
    else:
        hight_list[i] = hight_list[i]/1000
    # print(qv)
# print(Potential_Temperature_list)
# print(Sd_list)
        

#將無效資料去除
while Potential_Temperature_list.count(-999) != 0:
    Potential_Temperature_list.remove(-999)
    Sd_list.remove(-999)
    hight_list.remove(-999)
    Temperature_list.remove(-999)


#設定max data輔助線
Sd_support_line_list = []
pt_support_line_list = []
for i in range(len(Sd_list)):
    Sd_support_line_list.append(max(Sd_list))
    pt_support_line_list.append(max(Potential_Temperature_list))



#繪圖
plt.rcParams['font.sans-serif'] = [u'MingLiu'] #細明體
plt.rcParams['axes.unicode_minus'] = False 
fig = plt.figure()
ax = fig.add_subplot()

ax.plot(Sd_list,hight_list,color ='r',lw = 1,label = r'$S_{d}$' + '/' +r'$C_{p}$')
ax.plot(Potential_Temperature_list,hight_list,color ='g',lw = 1,label = 'Potential Temperature')
#max data 輔助線
ax.plot(Sd_support_line_list,hight_list,color ='r',lw = 0.5,linestyle = '--')
ax.plot(pt_support_line_list,hight_list,color ='g',lw = 0.5,linestyle = '--')

#max data 註解文字
ax.text(max(Sd_list),max(hight_list), round(max(Sd_list)),
         color = 'r',
         fontsize=10,
         horizontalalignment='center', 
         verticalalignment='bottom')
ax.text(max(Potential_Temperature_list),max(hight_list), round(max(Potential_Temperature_list)),
         color = 'g',
         fontsize=10,
         horizontalalignment='center', 
         verticalalignment='bottom') 

hight_tick_set_list = [hight_list[0]]
for i in range(0,round(max(hight_list))-round(min(hight_list))+1,2):
    hight_tick_set_list.append(i+1)
hight_tick_set_list.remove(max(hight_tick_set_list))
hight_tick_set_list.append(max(hight_list))

ax.set_ylim(hight_list[0])
ax.set_yticks(hight_tick_set_list)
plt.ylabel('Height[km]',fontsize = 20)
plt.xlabel('Temperature [k]',fontsize = 20)
plt.legend()
plt.title('2011/08/02 14:00\n地點:苗栗站\n (120.82458 E,24.56457 N)')
plt.show()