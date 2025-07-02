import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from matplotlib.colors import ListedColormap, BoundaryNorm

# ====== 基本設定 ======
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = 2021
flash_type = 'CG'  # 可選 'IC', 'CG', 'all'
flash_type = 'IC'
lon_lat_gap = 0.01

lon_min, lon_max = 120.0, 122.03
lat_min, lat_max = 21.88, 25.32

for year in range(2018,2025):
    print(year)
    for flash_type in ['IC',"CG"]:
        print(flash_type)



        # ====== 載入資料並篩選範圍 ======
        EN_flash_datas = pd.read_csv(f"{data_top_path}/flash_data/raw_data/EN/lightning_{year}.txt")

        main_island_lon_lat_range = (
            (lon_min < EN_flash_datas['lon']) & (EN_flash_datas['lon'] < lon_max) &
            (lat_min < EN_flash_datas['lat']) & (EN_flash_datas['lat'] < lat_max)
        )
        flash_datas_main_island = EN_flash_datas[main_island_lon_lat_range]

        # ====== 根據類別篩選 IC / CG / all ======
        if flash_type in ['IC', 'CG']:
            flash_datas_main_island = flash_datas_main_island[flash_datas_main_island['lightning_type'] == flash_type]
        elif flash_type == 'all':
            pass  # 不做篩選
        else:
            raise ValueError("flash_type 必須是 'IC', 'CG' 或 'all'")

        # ====== 字型設定 ======
        plt.rcParams['font.sans-serif'] = [u'MingLiu']
        plt.rcParams['axes.unicode_minus'] = False

        # ====== 計算格子 ======
        lon_bins = np.arange(lon_min, lon_max + lon_lat_gap, lon_lat_gap)
        lat_bins = np.arange(lat_min, lat_max + lon_lat_gap, lon_lat_gap)


        H, xedges, yedges = np.histogram2d(
            flash_datas_main_island["lon"], flash_datas_main_island["lat"],
            bins=[lon_bins, lat_bins]
        )

        # ====== 顏色與 colorbar 設定 ======
        colors = ["white", "plum", "slateblue", "blue", "green", "yellow", "orange", "red"]
        cmap = ListedColormap(colors)
        bounds = [0, 20, 50, 100, 200, 400, 500, 600, 700]
        norm = BoundaryNorm(bounds, cmap.N)

        # ====== 畫圖開始 ======
        fig = plt.figure(figsize=(10, 10))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.set_xlim(lon_min, lon_max)
        ax.set_ylim(lat_min, lat_max)

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
        if flash_type == 'all':
            flash_type = 'IC+CG'
        ax.set_title(f"{year} EN {flash_type} 閃電分佈", fontsize=14)

        print(f"{year} EN {flash_type} 閃電分佈以 {lon_lat_gap} 度分隔")
        # plt.show()
        plt.savefig(f"G:/我的雲端硬碟/工作/2025cook/工作進度_閃電/EN/{year}_{flash_type}_map.png", dpi=300)