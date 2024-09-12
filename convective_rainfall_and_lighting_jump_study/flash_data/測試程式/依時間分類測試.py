import os
import calendar
from tqdm import tqdm
from openpyxl import load_workbook
import math
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
from glob import glob

year = '2021' #年分
month = '06' #月份
data_top_path = "C:/Users/steve/python_data"
dis = 36
time = '051950'
# station_name = 'C0G880'



## 讀取雨量站經緯度資料
def rain_station_location_data():
    import pandas as pd
    data_path = f"{data_top_path}/研究所/雨量資料/{year}測站資料.csv"
    data = pd.read_csv(data_path)
    station_data_name = data['station name'].to_list()
    station_real_data_name = data['station real name'].to_list()
    lon_data = data['lon'].to_list()
    lat_data = data['lat'].to_list()
    # print(data)
    return station_data_name,station_real_data_name,lon_data,lat_data
station_data_name,station_real_data_name,lon_data,lat_data = rain_station_location_data()

def flash_color_set(x):
    if -5<x<=0:
        return 'r'
    elif -10<x<=-5:
        return 'y'
    elif -30<x<=-10:
        return 'g'
    elif -60<x<=-30:
        return 'blue'

reference_time = pd.to_datetime(f'{year}-{month}-{time[:2]} {time[2:4]}:{time[4:]}:00')
flash_data_lon_lat_color_list = [[],[],[]] 
## 讀取閃電資料
flash_data_paths = f"{data_top_path}/研究所/閃電資料/依時間分類/{year}/{month}/**.csv"
result = glob(flash_data_paths)
for flash_data_path in result:
    # print(flash_data_path)
    flash_data_time = pd.to_datetime(flash_data_path.split('\\')[-1].split('/')[-1].split('.')[0])
    
    # print(flash_data_time)
    time_diff = flash_data_time - reference_time
    if pd.Timedelta(minutes=-60) < time_diff <= pd.Timedelta(minutes=0):
        flash_data = pd.read_csv(flash_data_path)
        # print(flash_data)
        flash_data_lon_lat_color_list[0].append(flash_data['lon'].iloc[-1])
        flash_data_lon_lat_color_list[1].append(flash_data['lat'].iloc[-1])
    if pd.Timedelta(minutes=-5) < time_diff <= pd.Timedelta(minutes=0):
        flash_data_lon_lat_color_list[2].append('r')
    elif pd.Timedelta(minutes=-10) < time_diff <= pd.Timedelta(minutes=-5):
        flash_data_lon_lat_color_list[2].append('y')
    elif pd.Timedelta(minutes=-30) < time_diff <= pd.Timedelta(minutes=-10):
        flash_data_lon_lat_color_list[2].append('g')
    elif pd.Timedelta(minutes=-60) < time_diff <= pd.Timedelta(minutes=-30):
        flash_data_lon_lat_color_list[2].append('b')
# print(flash_data_lon_lat_color_list)

        



##繪圖
lon_min, lon_max = 119.9, 122.1
lat_min, lat_max = 21.5, 25.5

plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)

plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號

# 加載台灣的行政邊界
taiwan_shapefile = data_top_path+"/研究所/Taiwan_map_data/COUNTY_MOI_1090820.shp"  # 你需要提供台灣邊界的shapefile文件
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='white')
ax.add_feature(shape_feature)


# 加入經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

# ax.scatter(flash_rawdata['經度'],flash_rawdata['緯度'],color = 'g', s=3, zorder=5)
ax.scatter(flash_data_lon_lat_color_list[0],flash_data_lon_lat_color_list[1],color = flash_data_lon_lat_color_list[2],s = 6,zorder = 7)
# 加入標籤
plt.xlabel('Longitude')
plt.ylabel('Latitude')

ax.set_title(f'{year}-{month}-{time[:2]} {time[2:4]}:{time[4:]}')

# 顯示地圖
plt.show()
