import pyart
import matplotlib.pyplot as plt
from datetime import datetime
import cartopy.crs as crs

data_top_path = "C:/Users/steve/python_data/radar"
year = '2024'
month = '05'
day = '23'

## 讀入雷達檔案
data_path = f"{data_top_path}/{year}{month}{day}_u.RCWF/{year}{month}{day}000200.VOL"
radar = pyart.io.read_nexrad_archive(data_path)

time = data_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

#取屬性latitude
lat_atri = radar.latitude
lat = lat_atri["data"]

plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號

fig = plt.figure(figsize=(16, 8))
display = pyart.graph.RadarMapDisplay(radar) #畫雷達圖用的物件

## ==== 第一張圖：風速 ====
ax = plt.subplot(121, projection=crs.PlateCarree())
display.plot_ppi_map('velocity',
                     sweep=1,
                     ax=ax,
                     projection=crs.PlateCarree(),
                     colorbar_label='逕向風速 ($V_{r}$) \n (m/s)',
                     title='',
                     vmin=-30,
                     vmax=30,
                     shapefile=f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp",
                     shapefile_kwargs={"facecolor": 'none', 'edgecolor': 'green'},
                     embellish=False,
                     cmap='RdBu_r')
ax.set_extent([119, 123.5, 21, 26.5])
gl = ax.gridlines(draw_labels=True)
gl.right_labels = False

sweep = 0

## ==== 第二張圖：反射率 + 高度等高線 ====
ax = plt.subplot(122, projection=crs.PlateCarree())
display.plot_ppi_map('reflectivity',
                     sweep=sweep,
                     ax=ax,
                     colorbar_label='雷達迴波 ($Z_{e}$) \n (dBZ)',
                     title='',
                     vmin=-20,
                     vmax=60,
                     shapefile=f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp",
                     shapefile_kwargs={"facecolor": 'none', 'edgecolor': 'green'},
                     embellish=False)

# ==== 加入等高線 ====
x, y, z = radar.get_gate_x_y_z(sweep=sweep)  # 單位：公尺
z_km = z / 1000.0  # 換成 km

# 換算成實際經緯度（近似，僅用 radar 中心偏移）
x_lon = x / 100000.0 + radar.longitude['data'][0]
y_lat = y / 100000.0 + radar.latitude['data'][0]

contour = ax.contour(x_lon, y_lat, z_km,
                     levels=[1, 2, 3, 4, 5],  # 可以自行調整要標示的高度層
                     colors='black', linewidths=1)
ax.clabel(contour, fmt='%1.0f km', fontsize=10)

ax.set_extent([119, 123.5, 21, 26.5])
gl = ax.gridlines(draw_labels=True)
gl.right_labels = False

print("所有掃描層仰角（degrees）：", radar.fixed_angle['data'])

plt.suptitle(f"雷達觀測時間：{time_dt}", fontsize=18)
plt.show()
