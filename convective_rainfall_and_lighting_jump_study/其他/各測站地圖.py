import matplotlib.pyplot as plt
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import pandas as pd
from cartopy import geodesic
from glob import glob
import os
from tqdm import tqdm

year = '2021'  # 年分
month = '06'  # 月份
dis = 36
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"

def fileset(path):    # 建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立")

fileset(f"{data_top_path}/各測站地圖/{year}{month}")

# 讀取一次靜態資料
position_path = f"{data_top_path}/rain_data/測站資料/{year}_{month}.csv"
station_inf_datas = pd.read_csv(position_path)

# 設定字體和地圖範圍
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

lon_min, lon_max = 120, 122.1
lat_min, lat_max = 21.5, 25.5

# 加載台灣的行政邊界
taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='white')

# 處理所有測站檔案
result = glob(f"{data_top_path}/rain_data/測站範圍內測站數/{year}_{month}/**.csv")

for station_path in tqdm(result, desc='地圖繪製中...'):
    station_name = os.path.basename(station_path.split('.')[0])
    range_stations = pd.read_csv(station_path)
    merge_range_stations = pd.merge(range_stations['station name'],
                                    station_inf_datas[['station name', 'lon', 'lat']],
                                    on='station name', how='inner')

    mean_station_real_name = station_inf_datas[station_inf_datas['station name'] == station_name]['station real name'].iloc[0]
    point_lon = station_inf_datas[station_inf_datas['station name'] == station_name]['lon'].iloc[0]
    point_lat = station_inf_datas[station_inf_datas['station name'] == station_name]['lat'].iloc[0]

    plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)

    # 添加地圖邊界和格線
    ax.add_feature(shape_feature)
    gridlines = ax.gridlines(draw_labels=True, linestyle='--')
    gridlines.top_labels = False
    gridlines.right_labels = False

    # 繪製主要測站和範圍內測站
    ax.scatter(point_lon, point_lat, color='r', s=15, zorder=5)
    ax.scatter(merge_range_stations['lon'], merge_range_stations['lat'], color='g', s=5, zorder=4)

    # 繪製測站範圍圓形
    g = geodesic.Geodesic()
    circle = g.circle(lon=point_lon, lat=point_lat, radius=dis*1000)
    ax.plot(circle[:, 0], circle[:, 1], color='blue', transform=ccrs.PlateCarree())

    ax.set_title(f"{mean_station_real_name} ({point_lon},{point_lat})\ndis = {dis}km")

    # 儲存圖片
    pic_save_path = f"{data_top_path}/各測站地圖/{year}{month}/{station_name}_{mean_station_real_name}"
    plt.savefig(pic_save_path, bbox_inches='tight', dpi=300)
    plt.close()

    # 清除變數
    del point_lat, point_lon, merge_range_stations, mean_station_real_name

print(f"Time：{year}{month}、dis：{dis}")