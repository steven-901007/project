import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from matplotlib.colors import ListedColormap, BoundaryNorm
import os

# ==== 基本設定 ====

data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = 2019
# flash_type = 'CG'  # 可選 'IC', 'CG', 'all'
# flash_type = 'IC'

lon_lat_gap = 0.01
lon_min, lon_max = 120.0, 122.03
lat_min, lat_max = 21.88, 25.32
flash_type_code = {
    'IC': 'Cloud',
    'CG': 'Ground'
}


# 輸出圖檔存放位置
save_path = "G:/我的雲端硬碟/工作/2025cook/工作進度_閃電/CWA"
os.makedirs(save_path, exist_ok=True)

# ====== 逐年、逐類型繪圖 ======

for year in range(2018, 2025):
    print(f"處理 {year} 年資料...")
    for flash_type in ['IC','CG']:
    # ====== 讀取資料 ======
        file_path = f"{data_top_path}/flash_data/raw_data/CWA/L{year}.csv"
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)

        for flash_type in ['IC','CG']:
            print(f"繪製 {flash_type} 閃電分布圖...")

            # ====== 資料篩選 ======
            df_type = df[df['Cloud or Ground'] == flash_type_code[flash_type]]

            # 濾除經緯度範圍外
            df_type = df_type[
                (df_type['Longitude'] >= lon_min) & (df_type['Longitude'] <= lon_max) &
                (df_type['Latitude'] >= lat_min) & (df_type['Latitude'] <= lat_max)
            ]

            if df_type.empty:
                print(f"⚠️ {year} 年 {flash_type} 無資料，跳過")
                continue

            # ====== 計算格子 ======
            lon_bins = np.arange(lon_min, lon_max + lon_lat_gap, lon_lat_gap)
            lat_bins = np.arange(lat_min, lat_max + lon_lat_gap, lon_lat_gap)

            H, xedges, yedges = np.histogram2d(
                df_type['Longitude'], df_type['Latitude'],
                bins=[lon_bins, lat_bins]
            )

            # ====== 顏色設定 ======
            colors = ["white", "plum", "slateblue", "blue", "green", "yellow", "orange", "red"]
            cmap = ListedColormap(colors)
            bounds = [0, 20, 50, 100, 200, 400, 500, 600, 700]
            norm = BoundaryNorm(bounds, cmap.N)

            # ====== 開始畫圖 ======
            fig = plt.figure(figsize=(10, 10))
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.set_xlim(lon_min, lon_max)
            ax.set_ylim(lat_min, lat_max)

            plt.rcParams['font.sans-serif'] = [u'MingLiu']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 加上台灣縣市邊界
            taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
            shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                                        ccrs.PlateCarree(), edgecolor='black', facecolor='none')
            ax.add_feature(shape_feature)

            # 加上格線
            gridlines = ax.gridlines(draw_labels=True, linestyle='--')
            gridlines.top_labels = False
            gridlines.right_labels = False

            # 閃電熱圖
            mesh = ax.pcolormesh(xedges, yedges, H.T, cmap=cmap, norm=norm, shading="auto", transform=ccrs.PlateCarree())

            # 顏色條
            cbar = plt.colorbar(mesh, ax=ax, orientation="vertical", shrink=0.7, pad=0.05)
            cbar.set_ticks(bounds)
            cbar.set_ticklabels(list(map(str, bounds)))

            # 標題與軸標籤
            plt.xlabel("Longitude", fontsize=12)
            plt.ylabel("Latitude", fontsize=12)
            ax.set_title(f"{year} CWA {flash_type} 閃電分佈", fontsize=14)

            # 儲存
            plt.tight_layout()
            plt.savefig(f"{save_path}/{year}_CWA_{flash_type}_map.png", dpi=300)
            plt.close()

