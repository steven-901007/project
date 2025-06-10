import pyart
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

data_top_path = "C:/Users/steve/python_data/radar"
year = '2024'
month = '05'
day = '23'


## 讀入雷達檔案
data_path = f"{data_top_path}/{year}{month}{day}_u.RCWF/{year}{month}{day}000200.VOL"
radar = pyart.io.read_nexrad_archive(data_path)

time = data_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")
# print(time_dt)

# print(radar.info())

#取屬性latitude
lat_atri = radar.latitude
# print(lat_atri)

import cartopy.crs as crs


#根據鍵值取數值
lat = lat_atri["data"]



plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號

fig = plt.figure(figsize=(16,8))
display = pyart.graph.RadarMapDisplay(radar) #先開一個要畫雷達地圖的物件
ax = plt.subplot(121,
                 projection=crs.PlateCarree())



display.plot_ppi_map('velocity',
                     sweep=1,
                     ax=ax,
                     projection=crs.PlateCarree(),
                     colorbar_label='逕向風速 ($V_{r}$) \n (m/s)',
                     title='',
                     vmin=-30,
                     vmax=30,
                     shapefile=f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp",
                     shapefile_kwargs={"facecolor":'none','edgecolor':'green'},
                     embellish=False, #取消內建的海岸線shapefile
                     cmap='RdBu_r')
ax.set_extent([119, 123.5, 21, 26.5])
gl=ax.gridlines(draw_labels=True)
gl.right_labels = False

ax = plt.subplot(122,
                 projection=crs.PlateCarree())
display.plot_ppi_map('reflectivity',
                     sweep=0,
                     ax=ax,
                     colorbar_label='雷達迴波 ($Z_{e}$) \n (dBZ)',
                     title='',
                     vmin=-20,
                     vmax=60,
                     shapefile=f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp",
                     shapefile_kwargs={"facecolor":'none','edgecolor':'green'},
                     embellish=False)

print("所有掃描層仰角（degrees）：", radar.fixed_angle['data'])

ax.set_extent([119, 123.5, 21, 26.5])
gl=ax.gridlines(draw_labels=True)
gl.right_labels = False
plt.suptitle(f"雷達觀測時間：{time_dt}", fontsize=18)
plt.show()
