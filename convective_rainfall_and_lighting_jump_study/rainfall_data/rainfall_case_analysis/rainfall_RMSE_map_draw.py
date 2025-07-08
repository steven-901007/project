import glob
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib as mpl
from tqdm import tqdm
import pandas as pd
import numpy as np
from cartopy import geodesic


year = '2021' #年分
month = '07' #月份
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"



station_data_path = f"{data_top_path}/rain_data/測站資料/{year}_{month}.csv"
station_data = pd.read_csv(station_data_path)
# print(station_data)

RMSE_lon_list = []
RMSE_lat_list = []
RMSE_lsit = []
##降雨資料讀取

RMSE_data_path = f"{data_top_path}/rain_data/cwa小時雨量測試/RMSE.csv"
RMSE_datas = pd.read_csv(RMSE_data_path)
# print(RMSE_datas)

merged_data = pd.merge(RMSE_datas, station_data[['station name', 'lon', 'lat']], on='station name', how='left')
print(merged_data)

level = [0,2,3,5,10,20,30,40]
color_box = ['silver','orange','y','g','blue','darkviolet','r']
conditions = [
    (merged_data['RMSE'] >= level[0]) & (merged_data['RMSE'] < level[1]),
    (merged_data['RMSE'] >= level[1]) & (merged_data['RMSE'] < level[2]),
    (merged_data['RMSE'] >= level[2]) & (merged_data['RMSE'] < level[3]),
    (merged_data['RMSE'] >= level[3]) & (merged_data['RMSE'] < level[4]),
    (merged_data['RMSE'] >= level[4]) & (merged_data['RMSE'] < level[5]),
    (merged_data['RMSE'] >= level[5]) & (merged_data['RMSE'] < level[6]),
    (merged_data['RMSE'] >= level[6]) & (merged_data['RMSE'] < level[7]),
]
# level = [0,1,3,5,10]
# color_box = ['silver','b','g','orange']
# conditions = [
#     (merged_data['RMSE'] >= level[0]) & (merged_data['RMSE'] < level[1]),
#     (merged_data['RMSE'] >= level[1]) & (merged_data['RMSE'] < level[2]),
#     (merged_data['RMSE'] >= level[2]) & (merged_data['RMSE'] < level[3]),
#     (merged_data['RMSE'] >= level[3]) & (merged_data['RMSE'] < level[4]),
# ]
# 對應的顏色

# 使用 np.select 根據條件設置顏色
merged_data['color'] = np.select(conditions, color_box)


## 繪圖

# 設定經緯度範圍
lon_min, lon_max = 120, 122.1
lat_min, lat_max = 21.5, 25.5

plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)

plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號

# 加載台灣的行政邊界
taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp" # 你需要提供台灣邊界的shapefile文件
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                            ccrs.PlateCarree(), edgecolor='black', facecolor='white')
ax.add_feature(shape_feature)


# 加入經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

ax.scatter(merged_data['lon'],merged_data['lat'],color = merged_data['color'],s=5,zorder=4,label = 'around stataion location') #周圍dis內的測站
g = geodesic.Geodesic()


# colorbar setting

nlevel = len(level)
cmap1 = mpl.colors.ListedColormap(color_box, N=nlevel)
cmap1.set_over('fuchsia')
cmap1.set_under('black')
norm1 = mcolors.Normalize(vmin=min(level), vmax=max(level))
norm1 = mcolors.BoundaryNorm(level, nlevel, extend='max')
im = cm.ScalarMappable(norm=norm1, cmap=cmap1)
cbar1 = plt.colorbar(im,ax=ax, extend='neither', ticks=level, aspect=30, shrink=0.5)
cbar1.set_label('RMSE', rotation=270, labelpad=20)
# 加入標籤
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title(f"RMSE[mm]\n{year}/{month}\nmax = {merged_data['RMSE'].max()},min = {merged_data['RMSE'].min()}")
# print(merged_data['RMSE'].max(),merged_data['RMSE'].min())

plt.show()