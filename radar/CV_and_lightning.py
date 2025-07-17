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

## ==== 時間設定 ==== ##
year = sys.argv[1] if len(sys.argv) > 1 else '2021'
month = sys.argv[2] if len(sys.argv) > 2 else '05'
day = sys.argv[3] if len(sys.argv) > 3 else '30'
hh = '04'
mm = '01'
ss = '00'

draw_one_or_all = 'one'

## ==== 路徑設定 ==== ##
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/radar"
    flash_data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/radar"
    flash_data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"

shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
save_dir = f"{data_top_path}/CV/{year}{month}{day}"
os.makedirs(save_dir, exist_ok=True)

myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
plt.rcParams['axes.unicode_minus'] = False

## ==== 找出要處理的 VOL 檔案清單 ==== ##
if draw_one_or_all == 'one':
    vol_file = f"{data_top_path}/data/{year}{month}{day}_u.RCWF/{year}{month}{day}{hh}{mm}{ss}.VOL"
    vol_files = [vol_file]
else:
    vol_folder = f"{data_top_path}/data/{year}{month}{day}_u.RCWF"
    vol_files = sorted(glob(f"{vol_folder}/*.VOL"))

for vol_file in vol_files:
    try:
        radar = pyart.io.read_nexrad_archive(vol_file)
        time_str = os.path.basename(vol_file).split('.')[0]
        time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")  # 這裡保持 datetime 格式
        time_str = (time_dt + timedelta(hours=8)).strftime("%Y%m%d%H%M")  # 轉 LCT 並轉成字串


        ## ==== 製作 Grid 資料 ==== ##
        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(31, 241, 241),
            grid_limits=((0, 15000), (-150000, 150000), (-150000, 150000)),
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

        # 經緯度轉換
        lon_grid = radar_lon + (x / 111) / np.cos(np.radians(radar_lat))
        lat_grid = radar_lat + (y / 111)

        ## ==== 加入閃電資料（EN，每分鐘一檔）==== ##
        flash_path = f"{flash_data_top_path}/flash_data/EN/sort_by_time/{year}/{month}/{time_str}.csv"
        # print(flash_path)
        flash_data_now = None
        if os.path.exists(flash_path):
            try:
                flash_data_now = pd.read_csv(flash_path)  # 該分鐘 EN 閃電資料（LCT）
            except Exception as e:
                print(f"⚠️ 讀取閃電檔案失敗：{flash_path}\n原因：{e}")

        ## ==== 畫圖 ==== ##
        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())

        mesh = ax.pcolormesh(
            lon_grid,
            lat_grid,
            comp_reflect,
            cmap='NWSRef',
            vmin=0,
            vmax=65,
            transform=ccrs.PlateCarree()
        )

        # 畫出閃電點（如果有的話）
        if flash_data_now is not None and not flash_data_now.empty:
            ax.scatter(
                flash_data_now['lon'], flash_data_now['lat'],
                s=10, c='black', label='閃電', transform=ccrs.PlateCarree(), zorder=5
            )
            ax.legend(loc='upper right', fontsize=12, prop=myfont)

        # 標題與 colorbar
        time_str_title = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S") 
        ax.set_title(f"CV 測站:RCWF(五分山)\n觀測時間:{time_str_title}", fontproperties=title_font)
        cbar = plt.colorbar(mesh, ax=ax, shrink=0.8)
        cbar.set_label("反射率 (dBZ)", fontproperties=myfont)
        cbar.set_ticks(np.arange(0, 70, 5))

        



        # 台灣邊界
        ax.add_geometries(
            Reader(shapefile_path).geometries(),
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor='green',
            linewidth=1,
        )

        # 雷達中心與 36km 圓
        ax.plot(radar_lon, radar_lat, 'ro', transform=ccrs.PlateCarree())
        circle = geodesic.Geodesic().circle(lon=radar_lon, lat=radar_lat, radius=36000, n_samples=360)
        circle_lons, circle_lats = zip(*circle)
        ax.plot(circle_lons, circle_lats, color='black', linewidth=2, linestyle='-', transform=ccrs.PlateCarree())
        lon_min = np.min(lon_grid)
        lon_max = np.max(lon_grid)
        lat_min = np.min(lat_grid)
        lat_max = np.max(lat_grid)
        margin_lon = (lon_max - lon_min) * 0.02
        margin_lat = (lat_max - lat_min) * 0.02
        ax.set_extent([lon_min - margin_lon, lon_max + margin_lon,
                    lat_min - margin_lat, lat_max + margin_lat])
        gl = ax.gridlines(draw_labels=True)
        gl.right_labels = False



        plt.tight_layout()
        output_path = f"{save_dir}/{time_str}00_CV.png"
        plt.savefig(output_path, dpi=150)
        if draw_one_or_all == 'one':
            plt.show()
        plt.close()
        print(f"✅ 儲存圖檔：{output_path}")
    except Exception as e:
        print(f"❌ 讀取錯誤：{vol_file}\n原因：{e}")
