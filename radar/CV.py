import pyart
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader


# ==== 基本設定 ====
data_top_path = "C:/Users/steve/python_data/radar"
year = '2021'
month = '06'
day = '12'
hh = '20'
mm = '19'
ss = '00'

draw_line_or_not = 'yes' #yes or no
# 設定兩條射線角度（單位：度，0 度為正北，順時針）
beam_angle_1 = 180  # 第一條射線角度
beam_angle_2 = 290  # 第二條射線角度

shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

draw_shape = 'circle'
# draw_shape = 'square'

## ==== 讀取雷達資料 ====
data_path = f"{data_top_path}/{year}{month}{day}_u.RCWF/{year}{month}{day}{hh}{mm}{ss}.VOL"
radar = pyart.io.read_nexrad_archive(data_path)

## ==== 時間字串轉換 ====
time = data_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

## ==== Gridding：做 Composite Reflectivity ====
grid = pyart.map.grid_from_radars(
    radar,
    grid_shape=(1, 500, 500),
    grid_limits=((1000, 1000), (-150000.0, 150000.0), (-150000.0, 150000.0)),
    fields=['reflectivity']
)

## ==== 中文字型 ====
plt.rcParams['font.sans-serif'] = ['MingLiu']  # '細明體'
plt.rcParams['axes.unicode_minus'] = False

## ==== 畫圖 ====
fig = plt.figure(figsize=(10, 8))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())


# from matplotlib.colors import BoundaryNorm
# from matplotlib.colorbar import ColorbarBase

# levels = [-20, 0, 10, 20, 30, 40, 50, 60]  # 自訂 dBZ 等級
# cmap = plt.get_cmap('turbo')  # 或 'jet'、'viridis'、'NWSRef' 也可
# norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
from matplotlib.colors import LinearSegmentedColormap
# 畫合成雷達回波
if draw_shape == 'circle':
    display = pyart.graph.RadarMapDisplay(radar)
    display.plot_ppi_map(

        'reflectivity',

        sweep=0,
        vmin=0,
        vmax=65,
        cmap='NWSRef',
        # cmap='RefDiff',
        ax=ax,
        colorbar_label='合成雷達回波 (dBZ)',
        title=f"合成雷達回波圖（CV）\n觀測時間：{time_dt}",
        embellish=False,
        add_grid_lines=False,
        # add_colorbar = False,
     
    )


elif draw_shape == 'square':
    display = pyart.graph.GridMapDisplay(grid)
    display.plot_grid(
        'reflectivity',
        level=0,
        vmin=0,
        vmax=65,
        cmap='NWSRef',
        ax=ax,
        colorbar_label='合成雷達回波 (dBZ)',
        title=f"合成雷達回波圖（maximum value at each layer）\n觀測時間：{time_dt}",
        embellish=False,
        add_grid_lines=False
    )


cbar = ax.collections[0].colorbar  # 取得 colorbar
cbar.set_ticks(np.arange(0, 70, 5))  # 每 5 dBZ 一格

# 加上台灣邊界 shapefile
ax.add_geometries(
    Reader(shapefile_path).geometries(),
    crs=ccrs.PlateCarree(),
    facecolor='none',
    edgecolor='green',
    linewidth=1,
)

# ==== 畫雷達中心可控角度的射線 ====
if draw_line_or_not == 'yes':

    # 雷達位置（五分山）
    radar_lon = 121.792
    radar_lat = 25.067



    # 射線長度（單位：度，約 1 度 = 100 km，可自行調整）
    line_length = 1.0

    # 計算第一條射線終點座標
    import math
    end_lon_1 = radar_lon + line_length * math.sin(math.radians(beam_angle_1))
    end_lat_1 = radar_lat + line_length * math.cos(math.radians(beam_angle_1))

    # 計算第二條射線終點座標
    end_lon_2 = radar_lon + line_length * math.sin(math.radians(beam_angle_2))
    end_lat_2 = radar_lat + line_length * math.cos(math.radians(beam_angle_2))

    ax.plot([radar_lon, end_lon_1], [radar_lat, end_lat_1], color='black', linewidth=2, transform=ccrs.PlateCarree())
    ax.plot([radar_lon, end_lon_2], [radar_lat, end_lat_2], color='black', linewidth=2, transform=ccrs.PlateCarree())

# 地圖設定
ax.set_extent([119, 123.5, 21, 26.5])  # 台灣範圍
gl = ax.gridlines(draw_labels=True)
gl.right_labels = False

plt.tight_layout()
plt.show()
