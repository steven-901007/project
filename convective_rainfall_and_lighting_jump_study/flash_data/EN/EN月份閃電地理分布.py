import matplotlib.pyplot as plt
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import pandas as pd
import numpy as np
import os

# 參數設定
year = '2021'
month = '05'
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
lon_lat_gap = 0.02 # 經緯度切割間距

# 建立儲存圖片資料夾
def file_set(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print(file_path + " 已建立")
file_set(f"{data_top_path}/閃電資料/EN/月份閃電地理分布/{year}_{month}")

# 讀取資料
data_path = f"{data_top_path}/閃電資料/raw_data/EN/{year}_EN/{year}{month}.csv"
datas = pd.read_csv(data_path)
data_lon = datas['lon']
data_lat = datas['lat']

# 設定畫圖範圍
lon_min, lon_max = 120.0, 122.1
lat_min, lat_max = 21.5, 25.5

# 計算格網資料
lon_bins = np.arange(lon_min, lon_max + lon_lat_gap, lon_lat_gap)
lat_bins = np.arange(lat_min, lat_max + lon_lat_gap, lon_lat_gap)
H, xedges, yedges = np.histogram2d(data_lon, data_lat, bins=[lon_bins, lat_bins])

# 顏色與分級設定
from matplotlib.colors import ListedColormap, BoundaryNorm
colors = ["white", "c", "blue", "green", "yellow", "orange", "red"]
cmap = ListedColormap(colors)
bounds = [0, 30, 60, 90, 120, 150, 180]
norm = BoundaryNorm(bounds, cmap.N)

# 畫圖
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False
fig = plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)

# 加入台灣邊界
taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='none')
ax.add_feature(shape_feature)

# 經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

# 閃電熱圖
mesh = ax.pcolormesh(xedges, yedges, H.T, cmap=cmap, norm=norm, shading="auto", transform=ccrs.PlateCarree())

# colorbar
cbar = plt.colorbar(mesh, ax=ax, orientation="vertical", shrink=0.7, pad=0.05)
cbar.set_ticks(bounds)
cbar.set_ticklabels([str(b) for b in bounds])
cbar.set_label("閃電次數")

# 標題與儲存
ax.set_title(f"{year}/{month} 閃電分佈以{lon_lat_gap}度分隔\nsoruce = EN raw data(.txt)", fontsize=14)
pic_save_path = f"{data_top_path}/閃電資料/EN/月份閃電地理分布/{year}_{month}/{year}{month}_gap={lon_lat_gap}.png"
plt.savefig(pic_save_path, bbox_inches='tight', dpi=300)
plt.close()
# plt.show()
print(f"Time：{year}{month}")