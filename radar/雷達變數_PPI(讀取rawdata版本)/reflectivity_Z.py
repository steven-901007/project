import pyart
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime


## === 路徑與時間設定 ===
data_top_path = "C:/Users/steve/python_data/radar"
year = '2021'
month = '11'
day = '26'
hh = '07'
mm = '36'
ss = '00'

file_path = f"{data_top_path}/{year}{month}{day}_u.RCWF/{year}{month}{day}{hh}{mm}{ss}.VOL"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"  # 縣市邊界
plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號


time = file_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

## === 讀取雷達資料 ===
radar = pyart.io.read(file_path)
sweep_num = 4  # 你想畫第幾圈仰角

## === 畫圖 ===
display = pyart.graph.RadarMapDisplay(radar)
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

display.plot_ppi_map('reflectivity',
                     sweep=sweep_num,
                     ax=ax,
                     colorbar_label='雷達迴波 ($Z_{e}$) \n (dBZ)',
                     title=f'reflectivity\n{time_dt}',
                     vmin=0,
                     vmax=70,
                     shapefile=shapefile_path,
                     shapefile_kwargs={"facecolor": 'none', 'edgecolor': 'green'},
                     embellish=False)

# x, y, z = radar.get_gate_x_y_z(sweep=sweep_num)  # 單位：公尺
# z_km = z / 1000.0  # 換成 km

# # 換算成實際經緯度（近似，僅用 radar 中心偏移）
# x_lon = x / 100000.0 + radar.longitude['data'][0]
# y_lat = y / 100000.0 + radar.latitude['data'][0]

# contour = ax.contour(x_lon, y_lat, z_km,
#                      levels=[1, 2, 3, 4, 5],  # 可以自行調整要標示的高度層
#                      colors='black', linewidths=1)
# ax.clabel(contour, fmt='%1.0f km', fontsize=10)

ax.set_extent([119, 123.5, 21, 26.5])  # 台灣地區範圍
gl = ax.gridlines(draw_labels=True)
gl.right_labels = False
plt.show()
