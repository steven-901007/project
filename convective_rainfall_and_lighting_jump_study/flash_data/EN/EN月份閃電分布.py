import matplotlib.pyplot as plt
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import pandas as pd
from cartopy import geodesic
from glob import glob
import os
from tqdm import tqdm


year = '2021'     # 年分
month = '09'
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"


##建立資料夾
def file_set(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print(file_path + " 已建立")
file_set(f"{data_top_path}/閃電資料/EN/月份閃電分布")

data_path = f"{data_top_path}/閃電資料/raw_data/EN/{year}_EN/{year}{month}.csv"
datas = pd.read_csv(data_path)
data_lon = datas['lon']
data_lat = datas['lat']
# print(datas)


# 設定字體和地圖範圍
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

lon_min, lon_max = 120, 122.1
lat_min, lat_max = 21.5, 25.5

# 加載台灣的行政邊界
taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='white')

plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)

# 添加地圖邊界和格線
ax.add_feature(shape_feature)
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

# 繪製主要測站和範圍內測站
ax.scatter(data_lon, data_lat, color='g', s=0.01, zorder=5)



ax.set_title(f"{year}/{month} 閃電分布\n falsh data source：EN")

# 儲存圖片
pic_save_path = f"{data_top_path}/閃電資料/EN/月份閃電分布/{year}{month}"
plt.savefig(pic_save_path, bbox_inches='tight', dpi=300)
plt.close()
# plt.show()
print(f"Time：{year}{month}")