import matplotlib.pyplot as plt
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import pandas as pd
from cartopy import geodesic
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib as mpl

from glob import glob
import pandas as pd

data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = '2021' #年分
month = '06' #月份
day = '29'
time_start = 5
time_end = 8
dis = 36
alpha = 2 #統計檢定
flash_source = 'EN' # EN or TLDS
station_name = '01P190'






time_start_datatime = pd.to_datetime(f"{year}{month}{day} {time_start}:00:00")
time_end_datatime = pd.to_datetime(f"{year}{month}{day} {time_end}:00:00")
# print(time_start_datatime,time_end_datatime)
##flash_data

lon_list = []
lat_list = []

flash_paths = f"{data_top_path}/flash_data/{flash_source}/sort_by_time/{year}/{month}/**.csv"
result = glob(flash_paths)
for flash_path in result:
    data_time_str = flash_path.split('/')[-1].split('\\')[-1].split('.')[0]
    data_time = pd.to_datetime(data_time_str)
    if time_start_datatime<=data_time<=time_end_datatime:
        
        flash_data = pd.read_csv(flash_path)
        if flash_data.empty != True:
            # print(data_time_str)
            # print(flash_data['lon'].tolist())
            lon_list = lon_list + flash_data['lon'].tolist()
            lat_list = lat_list + flash_data['lat'].tolist()
    elif data_time> time_end_datatime:
        break



# print(len(lon_list),len(lat_list))






##底圖(地圖+半徑+測站)

position_path = f"{data_top_path}/雨量資料/測站資料/{year}_{month}.csv"
position_datas = pd.read_csv(position_path)

point_lon = position_datas[position_datas['station name'] == station_name]['lon'].iloc[0]
point_lat = position_datas[position_datas['station name'] == station_name]['lat'].iloc[0]
point_real_name = position_datas[position_datas['station name'] == station_name]['station real name'].iloc[0]

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
taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"  # 你需要提供台灣邊界的shapefile文件
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                            ccrs.PlateCarree(), edgecolor='black', facecolor='white')
ax.add_feature(shape_feature)


# 加入經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False


ax.scatter(point_lon,point_lat,color = 'r', s=15, zorder=5,label = f"{station_name}")#main stataion
ax.scatter(lon_list,lat_list,color = 'green', s=1, zorder=5,marker='.',label = "flash location")
g = geodesic.Geodesic()
circle = g.circle(lon=point_lon, lat=point_lat, radius=dis*1000)  # radius in meters
ax.plot(circle[:, 0], circle[:, 1], color='blue', transform=ccrs.PlateCarree(),label = f"半徑 = {dis}")
plt.legend()

plt.title(f"Flash Pattern(source：{flash_source}) \n {year}/{month}/{day} {time_start}:00~{time_end}:00 \n {point_real_name}({station_name})")

# 顯示地圖

plt.show()

