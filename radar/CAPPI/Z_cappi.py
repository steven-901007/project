import pyart
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os
from glob import glob
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy import geodesic
from matplotlib.font_manager import FontProperties
import platform
import sys

## ==== 時間設定 ==== ##
year = sys.argv[1] if len(sys.argv) > 1 else '2021'
month = sys.argv[2] if len(sys.argv) > 2 else '05'
day = sys.argv[3] if len(sys.argv) > 3 else '30'
hh = '00'
mm = '04'
ss = '00'

draw_one_or_all = 'one'  # 只處理一筆

## ==== 路徑設定 ==== ##
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/radar"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/radar"

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

## ==== 主程式 ==== ##
for vol_file in vol_files:
    try:
        radar = pyart.io.read_nexrad_archive(vol_file)
        time_str = os.path.basename(vol_file).split('.')[0]
        time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")
        print(radar)
    #     # 製作 grid
    #     grid = pyart.map.grid_from_radars(
    #         radar,
    #         grid_shape=(31, 241, 241),  # 垂直 0~15km，共 31 層
    #         grid_limits=((0, 15000), (-150000, 150000), (-150000, 150000)),
    #         fields=['reflectivity'],
    #         gridding_algo='map_to_grid',
    #         weighting_function='Cressman',
    #         min_radius=500.0,  # 不插值太遠
    #     )

    #     heights = grid.z['data']  # 每層高度 (m)
    #     x = grid.x['data'] / 1000  # km
    #     y = grid.y['data'] / 1000
    #     radar_lon = radar.longitude['data'][0]
    #     radar_lat = radar.latitude['data'][0]

    #     # 經緯度轉換
    #     lon_grid = radar_lon + (x / 111) / np.cos(np.radians(radar_lat))
    #     lat_grid = radar_lat + (y / 111)

    #     # 每層畫一張圖
    #     for i, height in enumerate(heights):
    #         reflectivity_layer = grid.fields['reflectivity']['data'][i, :, :]

    #         fig = plt.figure(figsize=(10, 8))
    #         ax = plt.axes(projection=ccrs.PlateCarree())

    #         mesh = ax.pcolormesh(
    #             lon_grid,
    #             lat_grid,
    #             reflectivity_layer,
    #             cmap='NWSRef',
    #             vmin=0,
    #             vmax=65,
    #             transform=ccrs.PlateCarree()
    #         )

    #         ax.set_title(
    #             f"RCWF（五分山）雷達反射率\n高度層：{int(height)} m\n觀測時間：{time_dt}",
    #             fontproperties=title_font
    #         )
    #         cbar = plt.colorbar(mesh, ax=ax, shrink=0.8)
    #         cbar.set_label("反射率 (dBZ)", fontproperties=myfont)
    #         cbar.set_ticks(np.arange(0, 70, 5))

    #         # 台灣邊界
    #         ax.add_geometries(
    #             Reader(shapefile_path).geometries(),
    #             crs=ccrs.PlateCarree(),
    #             facecolor='none',
    #             edgecolor='green',
    #             linewidth=1,
    #         )

    #         # 雷達紅點 + 黑色 36km 圓
    #         ax.plot(radar_lon, radar_lat, 'ro', transform=ccrs.PlateCarree())
    #         circle = geodesic.Geodesic().circle(lon=radar_lon, lat=radar_lat, radius=36000, n_samples=360)
    #         circle_lons, circle_lats = zip(*circle)
    #         ax.plot(circle_lons, circle_lats, color='black', linewidth=2, linestyle='-', transform=ccrs.PlateCarree())

    #         ax.set_extent([119, 123.5, 21, 26.5])
    #         gl = ax.gridlines(draw_labels=True)
    #         gl.right_labels = False

    #         plt.tight_layout()
    #         output_path = f"{save_dir}/{time_str}_CV_z{int(height)}m.png"
    #         plt.savefig(output_path, dpi=150)
    #         print(f"✅ 儲存圖檔：{output_path}")
    #         plt.close()

    except Exception as e:
        print(f"❌ 讀取錯誤：{vol_file}\n原因：{e}")
