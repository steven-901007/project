import glob
import re
import math
import time
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib as mpl


year = '2021' #年分
month = '06' #月份
day = '29'  #日期

##讀取每日資料

data_name_of_station_list = [] 
data_lon_list = []
data_lat_list = []
data_rain_list = [] #降雨量

day_path = "C:/Users/steve/python_data/研究所/雨量資料/"+year+"_"+month+"/"+month+"/"+year+month+day
result  =glob.glob(day_path+'/*')
for rain_data_path in result:
    # print(rain_data_path)

    hour = rain_data_path[64:66]
    minute  =rain_data_path[66:68]
    print(hour+":"+minute)


    ## 每日資料處理 rain data >10mm (10min)
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
                        # data_name_of_station_list.append(station_name)
                        data_lon_list.append(float(elements[4]))
                        data_lat_list.append(float(elements[3]))
            line += 1

# print(data_lon_list,data_lat_list)


## 繪圖

# 設定經緯度範圍
lon_min, lon_max = 120, 122.1
lat_min, lat_max = 21.5, 25.5

plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)

plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號

# 加載台灣的行政邊界
taiwan_shapefile = "C:/Users/steve/python_data/研究所/Taiwan_map_data/COUNTY_MOI_1090820.shp"  # 你需要提供台灣邊界的shapefile文件
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='lightgray')
ax.add_feature(shape_feature)


# 加入經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

## 計算某個地方達到10mm/10min的次數 + colorbar
color_list = []
level = [0,1,2,3,4,5,6]
color_box = ['none','r','orange','y','g','b','purple']

for i in range(len(data_lon_list)):
    lon_lat_count = min([data_lon_list.count(data_lon_list[i]),data_lat_list.count(data_lat_list[i])])#避免某個地方的經度or緯度一樣(but 經度and緯度不一樣)
    # print(lon_lat_count)
    for j in range(len(level)-1):
        if level[j]<lon_lat_count<=level[j+1]:
            color_list.append(color_box[j+1])
            # print(color_box[j+1])
            break

print(color_list)


# 標記經緯度點
ax.scatter(data_lon_list, data_lat_list, color=color_list, s=3, zorder=5)

# colorbar setting

nlevel = len(level) + 1  # 因為BoundaryNorm需要邊界數比顏色數多1
cmap1 = mcolors.ListedColormap(color_box)
norm1 = mcolors.BoundaryNorm(boundaries=[0.5, 1.5, 2.5, 3.5], ncolors=nlevel)# 設定 BoundaryNorm，這會將每個等級對應到顏色
im = cm.ScalarMappable(norm=norm1, cmap=cmap1)# 創建一個ScalarMappable用於colorbar
im.set_array([])  # 這一步是必需的，否則會出現錯誤
# 繪製colorbar
cbar1 = plt.colorbar(im, extend='neither', ticks=[1, 2, 3], shrink=0.6, aspect=30) #colorbar(shrink = colorbar長度,aspect = colorbar寬度)
cbar1.ax.set_yticklabels(['1', '2', '3'])  # 設置colorbar上的標籤


# 加入標籤
plt.xlabel('Longitude')
plt.ylabel('Latitude')

ax.set_title('全台雨量站座標')

# 顯示地圖
plt.show()

