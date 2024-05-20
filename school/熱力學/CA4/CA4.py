import netCDF4 as nc
import glob
import re
from openpyxl import load_workbook
import numpy as np
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
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
# x,y = map(map_file_path,24.56457,120.82458)    #苗栗座標
x,y = map(map_file_path,23.96,120.30586)    #座標
# print(x,y)


#pressure file
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
P = pressure("C:/Users/steve/python_data/thermodynamics/pressure.txt")  #[pa]
# print(P[2])


# wth(surface flux of potential temperature)
pt_list = []
# wth_folder = "C:/Users/steve/python_data/thermodynamics/Surface/"
# result  =glob.glob(wth_folder+'**')
# for wth_file_path in result:
#     print(wth_file_path)
file_path = "C:/Users/steve/python_data/thermodynamics/Thermodynamic/tpe20110802cln.L.Thermodynamic-000000.nc"
thrermodynamics_data = nc.Dataset(file_path)
# print(thrermodynamics_data)
potential_temps = thrermodynamics_data.variables["th"][0]
for i in range(len(potential_temps)):
    pt = potential_temps[i][y][x]
    pt_list.append(pt)
# print(pt_list)

add_wth_list = [0]
for i in range(len(pt_list)):
    add_wth_list.append(add_wth_list[i]+pt_list[i])

add_wth_list.remove(add_wth_list[0])
print(add_wth_list)


# hight [m]
hight_list = []
hight = thrermodynamics_data.variables["zc"]
for i in range(len(hight)):
    # print(hight[i])
    hight_list.append(int(hight[i]))
# print(hight_list)




#繪圖
plt.rcParams['font.sans-serif'] = [u'MingLiu'] #細明體
plt.rcParams['axes.unicode_minus'] = False 
fig = plt.figure()
a1 = fig.add_subplot()
a1.plot(hight_list,add_wth_list,color =  'r',linestyle = '-',label ='sensible heat flux')
# a1.set_xticks(time_count,time_tick,fontsize = 15,rotation = 60)
a1.set_xlabel(r'$\theta$',fontsize = 20)
a1.set_ylabel('hight',fontsize = 20)
# plt.legend(fontsize = 15)
# plt.yticks(fontsize = 20)
a1.set_ylim(0)
plt.title('tpe20110802cln surver(140.112.66.200)\ntime :000000\n苗栗站(24.56457N,120.82458E)',fontsize = 20)
plt.show()