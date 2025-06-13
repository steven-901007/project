import pyart
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
import cartopy.feature as cfeature





def cross_section_map(data_top_path,year,month,day,hh,mm,ss,lon0,lon1,lat0,lat1):
    # ==== 中文字型設定 ====
    plt.rcParams['font.sans-serif'] = ['MingLiu']  # '細明體'
    plt.rcParams['axes.unicode_minus'] = False

    shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
    data_path = f"{data_top_path}/{year}{month}{day}_u.RCWF/{year}{month}{day}{hh}{mm}{ss}.VOL"

    # ==== 讀取雷達資料 ====
    radar = pyart.io.read_nexrad_archive(data_path)
    time = data_path.split('/')[-1].split('.')[0]
    time_dt = datetime.strptime(time, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")



    # ==== 雷達位置 ====
    radar_lat = radar.latitude['data'][0]
    radar_lon = radar.longitude['data'][0]

    # ==== 畫圖開始 ====
    fig = plt.figure(figsize=(10, 8))
    ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # ==== 畫 CV 圖（雷達站單層）====
    display = pyart.graph.RadarMapDisplay(radar)
    display.plot_ppi_map(
        'reflectivity',
        sweep=0,
        vmin=0,
        vmax=65,
        cmap='NWSRef',
        ax=ax,
        colorbar_label='合成雷達回波 (dBZ)',
        title=f"cross section\n觀測時間：{time_dt}",
        embellish=False,
        add_grid_lines=False,
        zorder = 2,
    )

    # ==== Colorbar 每 5 dBZ ====
    cbar = ax.collections[0].colorbar
    cbar.set_ticks(np.arange(0, 70, 5))

    # ==== 加上台灣邊界 ====
    shape_feature = cfeature.ShapelyFeature(
        Reader(shapefile_path).geometries(),
        ccrs.PlateCarree(),
        edgecolor='green',
        facecolor='none',
        zorder = 3,
    )
    ax.add_feature(shape_feature, linewidth=1)

    # ==== 畫雷達位置點 + 剖面線 ====
    ax.plot(radar_lon, radar_lat, 'bo',color = 'black' ,zorder = 4,markersize=5, label='Radar')
    ax.plot([lon0, lon1], [lat0, lat1], '-',color = 'black',zorder = 4, linewidth=3, label='剖面線')

    # ==== 加格線與圖例 ====
    ax.set_extent([119, 123.5, 21, 26.5])  # 台灣範圍
    gl = ax.gridlines(draw_labels=True)
    gl.right_labels = False
    ax.legend(loc='lower left')

    plt.tight_layout()
    plt.show()


cross_section_map(# ==== 基本設定 ====
data_top_path = "C:/Users/steve/python_data/radar",
year = '2024',
month = '05',
day = '23',
hh = '00',
mm = '02',
ss = '00',
lon0 = 122.0,
lon1 = 120.8,
lat0 = 26.3,
lat1 = 25.3)