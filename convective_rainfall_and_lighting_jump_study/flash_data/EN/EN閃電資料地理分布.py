import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from matplotlib.colors import ListedColormap, BoundaryNorm

data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = 2021
lon_lat_gap = 0.02 #繪製經緯度切割邊長

lon_min, lon_max = 120.0, 122.03
lat_min, lat_max = 21.88, 25.32

EN_flash_datas = pd.read_csv(f"{data_top_path}/閃電資料/raw_data/EN/{year}_EN/{year}_EN.txt")
# print(EN_flash_datas)


main_island_lon_lat_range = (lon_min < EN_flash_datas['lon']) & (EN_flash_datas['lon'] < lon_max) & (lat_min < EN_flash_datas['lat']) & (EN_flash_datas['lat'] < lat_max)
flash_datas_main_island = EN_flash_datas[main_island_lon_lat_range]

# print(flash_datas_main_island)

plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號



# 設定網格範圍與間距
lon_min, lon_max = 120.0, 122.03
lat_min, lat_max= 21.88, 25.32



lon_bins = np.arange(lon_min, lon_max + lon_lat_gap, lon_lat_gap)
lat_bins = np.arange(lat_min, lat_max + lon_lat_gap, lon_lat_gap)

# 計算每個網格的閃電數量
H, xedges, yedges = np.histogram2d(flash_datas_main_island["lon"], flash_datas_main_island["lat"], bins=[lon_bins, lat_bins])

# **自定義顏色**
colors = ["white","c", "blue","green","yellow", "orange", "red"]  # 顏色順序
cmap = ListedColormap(colors)

# **設定數據分級**
# bounds = []
# for i in range(7): #變動colorbar
#     bounds.append(round(np.max(H)*i/60)*10)
# print(bounds) 

bounds = [0, 110, 230, 340, 460, 570, 680] #固定colorbar

norm = BoundaryNorm(bounds, cmap.N)

# 設定圖表
fig = plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)

# 加載台灣的行政邊界
taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"  # 修改為你的台灣邊界資料
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='none')
ax.add_feature(shape_feature)


# 加入經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False
 
# 繪製閃電熱圖 (使用自定義顏色)
mesh = ax.pcolormesh(xedges, yedges, H.T, cmap=cmap, norm=norm, shading="auto", transform=ccrs.PlateCarree())

# 加入顏色條
cbar = plt.colorbar(mesh, ax=ax, orientation="vertical", shrink=0.7, pad=0.05)
cbar.set_ticks(bounds)
cbar.set_ticklabels([f"{bounds[0]}", f"{bounds[1]}", f"{bounds[2]}",f"{bounds[3]}" ,f"{bounds[4]}",f"{bounds[5]}", f"{int(np.max(H))}"])




# 加入標籤
plt.xlabel("Longitude", fontsize=12)
plt.ylabel("Latitude", fontsize=12)
ax.set_title(f"{year} 閃電分佈以{lon_lat_gap}度分隔\nsoruce = EN raw data(.txt)", fontsize=14)

# 顯示地圖
plt.show()


