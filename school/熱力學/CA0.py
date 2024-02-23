#資料路徑必須是英文 否則會無法讀取

import netCDF4 as nc

import numpy as np
import matplotlib.pyplot as plt
import datetime

# file path
map_file_path = "C:/Users/steve/python_data/thermodynamics/CA0/TOPO.nc"
data_file_path = 'C:/Users/steve/python_data/thermodynamics/CA0/tpe20110802cln.L.Thermodynamic-000048.nc'

# read file
map = nc.Dataset(map_file_path)
# print(map)
data = nc.Dataset(data_file_path)
print(data)

# nb = 0
# for i in data.variables.keys():
#     dt = data.variables[i][:]
#     print(str(nb)+','+i+str(dt.shape))  #資料名稱(一維資料筆數,二維資料筆數,三維資料筆數)
#     nb += 1

def locate(list,number):
    return np.abs(list-number).argmin()

# map data
lat = map.variables["lat"][:]
lon = map.variables["lon"][:]

# 指定經緯度的值
latitude = 23.487
longitude = 120.959

# 找到最接近指定經緯度值的索引
y = locate(lat, latitude)  # south_north
x = locate(lon, longitude)  # west_east
# print(lat[y],lon[x])
# print(lat)


#data data
tg_qv = []
tg_height = []


# begin_height = 0 #3858

xc = data.variables['xc'][:]
xy = data.variables['yc'][:]
qv = data.variables['qv'][0] #濕度
# print(th)
for i in range(len(qv)):
    q = qv[i][y][x]
    h = data.variables['zc'][i]
    if q != 0:
        tg_height.append(h/1000)
        tg_qv.append(q*1000)


# print(tg_height[45])



ax = plt.axes()
plt.rcParams['font.sans-serif'] = [u'MingLiu'] #細明體
plt.rcParams['axes.unicode_minus'] = False #設定中文

x = tg_qv
y = tg_height


ax.plot(x,y,color =  'black',linestyle = '-') 

ax.set_xlabel("比濕[g/kg]",fontsize = 20)
ax.set_ylabel("高度[km]",loc='center',fontsize = 20)

ax.set_ylim(tg_height[0]) #設定y軸的起始數字

ax.tick_params(axis='x', labelsize=12) #設定x座標字體大小
ax.tick_params(axis='y', labelsize=12) #設定y座標字體大小

plt.annotate(str(int(tg_height[0]*1000))+'m', xy=(tg_qv[0], tg_height[0]), xytext=(tg_qv[0]+0.5, tg_height[0]+2),
            arrowprops=dict(facecolor='black', shrink=0.05),fontsize = 15)

ax.set_title(data_file_path[46:83]+'\nYushan Weather Station (23.487N, 120.959E)',fontsize = 20)
plt.show()
plt.close()
