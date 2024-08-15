import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from openpyxl import load_workbook

## 設定區
station = []
year = '2021' #年分
month = '06' #月份
# data_top_path = "C:/Users/steve/python_data"
data_top_path = "C:/Users/steven.LAPTOP-8A1BDJC6/OneDrive/桌面"
station_lat_max ,station_lat_min = 25.2 , 24.9
station_lon_max ,station_lon_min = 121.6, 121.5




def rain_station_location_data_to_list(data_top_path,year):## 讀取雨量站經緯度資料
    import pandas as pd
    data_path = data_top_path + "/研究所/雨量資料/"+ year + "測站資料.csv"
    data = pd.read_csv(data_path)
    station_data_name = data['station name'].to_list()
    station_real_data_name = data['station real name'].to_list()
    lon_data = data['lon'].to_list()
    lat_data = data['lat'].to_list()
    # print(data)
    return station_data_name,station_real_data_name,lon_data,lat_data
station_data_name_lsit,station_real_data_name_list,lon_data_list,lat_data_list = rain_station_location_data_to_list(data_top_path,year)

for station_nb in range(len(station_data_name_lsit)):
    if station_lat_max >= lat_data_list[station_nb] > station_lat_min and station_lon_max >= lon_data_list[station_nb] > station_lon_min:
        station.append(station_data_name_lsit[station_nb])

point_lon = []
point_lat = []

for s in station:
    point_lon.append(lon_data_list[station_data_name_lsit.index(s)])
    point_lat.append(lat_data_list[station_data_name_lsit.index(s)])

print(station)

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
taiwan_shapefile = data_top_path+"/研究所/Taiwan_map_data/COUNTY_MOI_1090820.shp"  # 你需要提供台灣邊界的shapefile文件
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='white')
ax.add_feature(shape_feature)


# 加入經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

ax.scatter(point_lon,point_lat,color = 'r', s=3, zorder=5)
# 加入標籤
plt.xlabel('Longitude')
plt.ylabel('Latitude')

ax.set_title('全台雨量站座標')

# 顯示地圖
plt.show()