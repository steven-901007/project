import pyart
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta  
import os
from glob import glob
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy import geodesic
from matplotlib.font_manager import FontProperties
import platform
import sys
import pandas as pd
# 引入顏色控制模組
from matplotlib.colors import ListedColormap, BoundaryNorm 


## ==== 時間設定 ==== ##
year = sys.argv[1] if len(sys.argv) > 1 else '2024'
month = sys.argv[2] if len(sys.argv) > 2 else '06'
day = sys.argv[3] if len(sys.argv) > 3 else '02'
station = sys.argv[4] if len(sys.argv) > 4 else 'RCCG'
draw_one_or_all = sys.argv[5] if len(sys.argv) > 5 else'one'  # 'one' or 'all'
hh = '08'
mm = '00'
ss = '00'

if station == 'RCWF':

    lon_min, lon_max = 120.5, 123
    lat_min, lat_max = 24.5, 26   
elif station == 'RCCG':
    lon_min, lon_max = 115, 125
    lat_min, lat_max = 18, 28
# elif station == 'RCCG':
#     lon_min, lon_max = 117, 123
#     lat_min, lat_max = 21, 26
## ==== 路徑設定 ==== ##
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/radar"
    flash_data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/radar"
    flash_data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"

##測站名
if station == 'RCWF':
    station_realname = '五分山'
elif station == 'RCCG':
    station_realname = '七股'
elif station == 'RCKT':
    station_realname = '墾丁'
elif station == 'RCHL':
    station_realname = '花蓮'

shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
save_dir = f"{data_top_path}/CV/{year}{month}{day}_{station}"
os.makedirs(save_dir, exist_ok=True)

## ============================== 手動定義 CWA (中央氣象署) Colormap ============================== ##
def get_cwa_ref_cmap():
    """
    手動建立台灣中央氣象署 (CWA/CWB) 風格的雷達回波色階
    """
    # 定義色階
    cwa_colors = [
        '#00FFFF', # 00-05 dBZ (Cyan)
        '#0090FF', # 05-10 dBZ (Sky Blue)
        '#0000FF', # 10-15 dBZ (Blue)
        '#00FF00', # 15-20 dBZ (Lime)
        '#00C800', # 20-25 dBZ (Green)
        '#009000', # 25-30 dBZ (Dark Green)
        '#FFFF00', # 30-35 dBZ (Yellow)
        '#FFD200', # 35-40 dBZ (Orange-Yellow)
        '#FF9000', # 40-45 dBZ (Orange)
        '#FF0000', # 45-50 dBZ (Red)
        '#C80000', # 50-55 dBZ (Dark Red)
        '#900000', # 55-60 dBZ (Maroon)
        '#FF00FF', # 60-65 dBZ (Magenta)
        '#900090'  # 65+   dBZ (Purple)
    ]
    
    # 定義每個顏色對應的數值範圍
    levels = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
    
    # 建立 Colormap
    cmap = ListedColormap(cwa_colors)
    cmap.set_under('none')     # 低於 0 透明
    cmap.set_over('#900090')   # 高於 70 紫色
    
    # 建立 BoundaryNorm (關鍵！讓顏色變成色塊)
    norm = BoundaryNorm(levels, ncolors=len(cwa_colors), clip=False)
    
    return cmap, norm, levels


from matplotlib.font_manager import FontProperties
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
plt.rcParams['axes.unicode_minus'] = False

## ==== 找出要處理的 VOL 檔案清單 ==== ##
if draw_one_or_all == 'one':
    vol_file = f"{data_top_path}/data/{year}{month}{day}_u.{station}/{year}{month}{day}{hh}{mm}{ss}.VOL"
    vol_files = [vol_file]
else:
    vol_folder = f"{data_top_path}/data/{year}{month}{day}_u.{station}"
    vol_files = sorted(glob(f"{vol_folder}/*.VOL"))

# 取得 CWA 樣式設定
cwa_cmap, cwa_norm, cwa_levels = get_cwa_ref_cmap()

for vol_file in vol_files:
    try:
        radar = pyart.io.read_nexrad_archive(vol_file)
        time_str = os.path.basename(vol_file).split('.')[0]
        time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")  # 這裡保持 datetime 格式
        time_str = (time_dt + timedelta(hours=8)).strftime("%Y%m%d%H%M")  # 轉 LCT 並轉成字串

        ## ==== 製作 Grid 資料 ==== ##
        # grid = pyart.map.grid_from_radars(
        #     radar,
        #     grid_shape=(31, 241, 241),
        #     grid_limits=((0, 15000), (-150000, 150000), (-150000, 150000)),
        #     fields=['reflectivity'],
        #     weighting_function='Nearest',
        # )
        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(31, 801, 801),
            grid_limits=((0, 15000), (-500000, 500000), (-500000, 500000)),
            fields=['reflectivity'],
            weighting_function='Nearest',
        )
        ## ==== 計算 beam height 遮罩 ==== ##
        x = grid.x['data'] / 1000  # km
        y = grid.y['data'] / 1000
        z = grid.z['data']  # m

        radar_lon = radar.longitude['data'][0]
        radar_lat = radar.latitude['data'][0]

        # 計算距離
        x2d, y2d = np.meshgrid(x * 1000, y * 1000)  # m
        r = np.sqrt(x2d**2 + y2d**2)  # m

        sweep_elevs = radar.fixed_angle['data']
        beam_heights = []
        for elev in sweep_elevs:
            h_beam = np.sqrt(r**2 + 8500000**2 + 2 * r * 8500000 * np.sin(np.radians(elev))) - 8500000
            beam_heights.append(h_beam)
        min_beam_height = np.min(np.array(beam_heights), axis=0)  # shape: (ny, nx)

        ## ==== 取得最大 reflectivity（Composite Reflectivity）==== ##
        reflectivity_data = grid.fields['reflectivity']['data']  # shape: (nz, ny, nx)

        # 建立遮罩：如果該層高度小於 beam height → 遮蔽
        for i in range(reflectivity_data.shape[0]):
            height = z[i]
            reflectivity_data[i][height < min_beam_height] = np.nan

        # Composite
        comp_reflect = np.nanmax(reflectivity_data, axis=0)

        # # 計算網格點到雷達中心的距離 (km)
        # dist_grid = np.sqrt(x2d**2 + y2d**2) / 1000 
        # # 將超過 250km 的資料遮蔽
        # comp_reflect[dist_grid > 250] = np.nan

        # 經緯度轉換
        lon_grid = radar_lon + (x / 111) / np.cos(np.radians(radar_lat))
        lat_grid = radar_lat + (y / 111)


        ## ==== 畫圖 ==== ##
        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())

        # 修改：加入 cmap 與 norm
        mesh = ax.pcolormesh(
            lon_grid,
            lat_grid,
            comp_reflect,
            cmap=cwa_cmap,   # 改用 CWA 顏色
            norm=cwa_norm,   # 改用 CWA 分層
            transform=ccrs.PlateCarree()
        )
        print('資料處理完成')
        
        ax.scatter(radar_lon, radar_lat, marker='x', color='red', s=30, zorder = 3,label='雷達位置', transform=ccrs.PlateCarree())
        ax.scatter(radar_lon, radar_lat, marker='X', color='w', s=100, zorder = 2, transform=ccrs.PlateCarree())
        # === 修改處：繪製雷達最大觀測範圍圓 ===

        gd = geodesic.Geodesic()
        for max_range_km in [230,460]:
            # 計算圓圈座標點
            circle_pts = gd.circle(lon=radar_lon, lat=radar_lat, radius=max_range_km * 1000)
            if max_range_km == 230:
                label_text = f'都卜勒掃描範圍 ({max_range_km}km)'
                c = 'gray'
            else:
                label_text = f'非都卜勒長距離掃描範圍 ({max_range_km}km)'
                c = 'black'
            # 繪製圓圈線條
            ax.plot(circle_pts[:, 0], circle_pts[:, 1], color=c, linestyle='--', 
                    linewidth=1.5, transform=ccrs.PlateCarree(), label=label_text)



        # 標題與 colorbar
        time_str_title = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S") 
        # ax.set_title(f"CV 測站:{station_realname}\n{time_str_title} LCT", fontproperties=title_font)
        ax.set_title(f"氣象局CWA 七股雷達站 雷達掃描範圍", fontproperties=title_font) ##for work
        # 修改：Colorbar 設定
        cbar = plt.colorbar(mesh, ax=ax, shrink=0.8, 
                            ticks=cwa_levels, spacing='uniform')
        cbar.set_label("dBZ", fontproperties=myfont)
        
        # 台灣邊界
        ax.add_geometries(
            Reader(shapefile_path).geometries(),
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor='black',
            linewidth=2,
        )
        print('繪圖完成')
        
        gl = ax.gridlines(draw_labels=True)
        gl.right_labels = False

        # 設定範圍
        ax.set_xlim(lon_min, lon_max)
        ax.set_ylim(lat_min, lat_max)
        

        plt.legend(loc='upper right', fontsize=12, prop=myfont)
        plt.tight_layout()
        output_path = f"{save_dir}/{time_str}00_CV.png"
        plt.savefig(output_path, dpi=150)

        if draw_one_or_all == 'one':
            plt.show()
        plt.close()
        print(f"✅ 儲存圖檔： {output_path}")
    except Exception as e:
        print(f"❌ 讀取錯誤：{vol_file}\n原因：{e}")