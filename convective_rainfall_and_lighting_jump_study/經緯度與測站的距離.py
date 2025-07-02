import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

# ==== 參數設定 ====
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
target_lon = 121.77   # 你的經度
target_lat = 25.07    # 你的緯度
station_file = rf"{data_top_path}\雨量資料\測站資料\2021_06.csv"
nearest_count = 20   # 要找幾個最近的測站
taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

# ==== 讀取測站資料 ====
station_df = pd.read_csv(station_file)

# ==== 計算距離 ====
distances = []
for _, row in station_df.iterrows():
    station_coord = (row['lat'], row['lon'])
    target_coord = (target_lat, target_lon)
    distance_km = geodesic(station_coord, target_coord).kilometers
    distances.append(distance_km)

station_df['distance_km'] = distances

# ==== 找最近的 N 個測站 ====
nearest_df = station_df.sort_values('distance_km').head(nearest_count).reset_index(drop=True)

# ==== 顯示結果 ====
print("最近的測站：")
print(nearest_df[['station name', 'station real name', 'lon', 'lat', 'distance_km']])

## ==== 中文字型 ====
plt.rcParams['font.sans-serif'] = ['MingLiu']  # '細明體'
plt.rcParams['axes.unicode_minus'] = False

# ==== 畫地圖 ====
plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
# 加載台灣行政邊界
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='None')
ax.add_feature(shape_feature)

# 加入經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

# 畫所有測站
ax.scatter(station_df['lon'], station_df['lat'], c='gray', label='所有測站',s = 2, alpha=0.5, transform=ccrs.PlateCarree())

# 畫最近測站
ax.scatter(nearest_df['lon'], nearest_df['lat'], c='blue',s = 2, label='最近測站', transform=ccrs.PlateCarree())

# 畫目標座標
ax.scatter(target_lon, target_lat, c='red', marker='x', s=100, label='指定座標', transform=ccrs.PlateCarree())

# 標記最近測站名稱
for _, row in nearest_df.iterrows():
    ax.text(row['lon'], row['lat'], row['station real name'], fontsize=8, transform=ccrs.PlateCarree())



plt.title('最近測站位置圖')
plt.legend()
plt.show()
