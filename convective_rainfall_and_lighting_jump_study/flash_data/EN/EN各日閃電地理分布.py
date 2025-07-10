import matplotlib.pyplot as plt
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import pandas as pd
import numpy as np
import os
from matplotlib.colors import ListedColormap, BoundaryNorm
import sys

# ==== 參數設定 ====

year =  sys.argv[1] if len(sys.argv) > 1 else "2018" 
lon_lat_gap = 0.02  # 經緯度切割間距

import platform
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"



# ==== 畫圖範圍 ====
lon_min, lon_max = 120.0, 122.1
lat_min, lat_max = 21.5, 25.5

# ==== 色階設定 ====
colors = ["white","black" ,"c", "blue", "green", "yellow", "orange", "red"]
cmap = ListedColormap(colors)
bounds = [0,1,5,10,20,30,60,100]
norm = BoundaryNorm(bounds, cmap.N)

# ==== 建立儲存資料夾 ====
save_folder = f"{data_top_path}/flash_data/EN/day_map/{year}"
os.makedirs(save_folder, exist_ok=True)
print(save_folder + " 已建立")

# ==== 讀取資料 ====
data_path = f"{data_top_path}/flash_data/raw_data/EN/lightning_{year}.txt"
datas = pd.read_csv(data_path)

# ==== 確認時間格式 ====

datas['time'] = pd.to_datetime(datas['Time'],errors='coerce')

# ==== 建立每日清單 ====
datas['date'] = datas['time'].dt.date
unique_dates = datas['date'].unique()
print(f"共找到 {len(unique_dates)} 天的資料")

# ==== 逐日畫圖 ====
for date in unique_dates:
    daily_data = datas[datas['date'] == date]
    data_lon = daily_data['lon']
    data_lat = daily_data['lat']

    ## 計算格網資料
    lon_bins = np.arange(lon_min, lon_max + lon_lat_gap, lon_lat_gap)
    lat_bins = np.arange(lat_min, lat_max + lon_lat_gap, lon_lat_gap)
    H, xedges, yedges = np.histogram2d(data_lon, data_lat, bins=[lon_bins, lat_bins])

    ## 畫圖
    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)

    ## 加入台灣邊界
    taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
    shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                                   ccrs.PlateCarree(), edgecolor='black', facecolor='none')
    ax.add_feature(shape_feature)

    ## 經緯度格線
    gridlines = ax.gridlines(draw_labels=True, linestyle='--')
    gridlines.top_labels = False
    gridlines.right_labels = False

    ## 閃電熱圖
    mesh = ax.pcolormesh(xedges, yedges, H.T, cmap=cmap, norm=norm, shading="auto", transform=ccrs.PlateCarree())

    ## colorbar
    cbar = plt.colorbar(mesh, ax=ax, orientation="vertical", shrink=0.7, pad=0.05)
    cbar.set_ticks(bounds)
    cbar.set_ticklabels([str(b) for b in bounds])
    cbar.set_label("flash count")

    ## 標題與儲存
    date_str = date.strftime("%Y%m%d")
    ax.set_title(f"{date}", fontsize=14)
    # ax.set_title(f"{date} 閃電分佈以{lon_lat_gap}度分隔\nsource = EN raw data (.txt)", fontsize=14)
    pic_save_path = f"{save_folder}/{date_str}_gap={lon_lat_gap}.png"
    plt.savefig(pic_save_path, bbox_inches='tight', dpi=300)
    plt.close()

    print(f"{date_str} 圖片已儲存")

print("全部繪圖完成")
