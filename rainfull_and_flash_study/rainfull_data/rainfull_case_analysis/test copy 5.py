import pandas as pd
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Circle

# 設定年分和月份
year = '2021'
month = '06'

# 設定資料路徑
data_top_path = "C:/Users/steve/python_data"
dis = 36

# 設定目標測站編號
station = '466920'

selected_time = '010830'  # 假設這個時間點存在於資料中

# 讀取測站資料
tg_station_data_path = f"{data_top_path}/研究所/雨量資料/{year}測站資料.csv"
tg_station_datas = pd.read_csv(tg_station_data_path)

# 獲取目標測站的實際名稱、經度和緯度
tg_station_real_name = tg_station_datas[tg_station_datas['station name'] == station]['station real name'].iloc[0]
tg_station_lon = tg_station_datas[tg_station_datas['station name'] == station]['lon'].iloc[0]
tg_station_lat = tg_station_datas[tg_station_datas['station name'] == station]['lat'].iloc[0]
tg_station_lat_lon = (tg_station_lat, tg_station_lon)

# 讀取雨量資料
data_path = f"{data_top_path}/研究所/雨量資料/{str(dis)}km個案分析/{month}/{station}/{station}_rain_data.xlsx"
datas = pd.read_excel(data_path)

# 取得測站的經緯度資料
lats = datas['station lat']
lons = datas['station lon']
rain_values = datas[selected_time].fillna(0)  # 將NaN值替換為0

# 設定更多顏色對應的級別和顏色
levels = [0, 0.5, 1, 2, 5, 7, 10, 15, 20]
colors = ['#4a90e2', '#357ABD', '#2B5A8A', '#1F3A61', '#16254D', '#10337D', '#ff6347', '#e74c3c', 'r']  # 使用深蓝色
cmap = mcolors.ListedColormap(colors)
norm = mcolors.BoundaryNorm(levels, ncolors=cmap.N, clip=True)

# 創建繪圖對象
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
ax.set_extent([119.5, 122.5, 21.5, 25.5], crs=ccrs.PlateCarree())
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.add_feature(cfeature.LAKES, edgecolor='black')
ax.add_feature(cfeature.RIVERS)
ax.gridlines(draw_labels=True)

# 畫等雨量圖
sc = ax.scatter(lons, lats, c=rain_values, cmap=cmap, norm=norm, s=10, edgecolor='none')
plt.colorbar(sc, ax=ax, orientation='vertical', label='Rainfall (mm)')

# # 繪製以 tg_station_lat_lon 為中心的圓
# circle_2_5 = plt.Circle(tg_station_lat_lon, 2.5/111, color='blue', fill=False, transform=ccrs.PlateCarree(), linewidth=2, zorder=10)
# circle_36 = plt.Circle(tg_station_lat_lon, 36/111, color='red', fill=False, transform=ccrs.PlateCarree(), linewidth=2, zorder=10)

# ax.add_patch(circle_2_5)
# ax.add_patch(circle_36)

# 設定圖例
# ax.legend([circle_2_5, circle_36], ['2.5 km Radius', '36 km Radius'], loc='upper right')

# 設定標題
plt.title(f'Rainfall Distribution at {selected_time} UTC')

# 顯示圖表
plt.show()
