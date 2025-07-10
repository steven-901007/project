from openpyxl import load_workbook
import glob
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib as mpl
import os

data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
data_source = 'EN'#flash_data來源


datas_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump/前估後符/EN_20210"

total_data = pd.DataFrame()

for month in range(4, 10):
    data_path = f"{datas_path}{month}/前估.csv"
    data = pd.read_csv(data_path)

    ## 只抓需要的欄位
    need_data = data[['station name', 'lon', 'lat', 'hit', 'total']]

    ## ✅ 檢查是否有缺經緯度
    missing_location = need_data[need_data['lon'].isna() | need_data['lat'].isna()]
    if not missing_location.empty:
        print(f"⚠️ 第 {month} 月有缺經緯度的測站：")
        print(missing_location[['station name']].drop_duplicates())

    ## 先對每月的測站資料做 groupby，但保留第一個 lon 和 lat
    month_sum_data = need_data.groupby('station name', as_index=False).agg({
        'lon': 'first',  # 經緯度不加總，取第一筆
        'lat': 'first',
        'hit': 'sum',
        'total': 'sum'
    })

    ## 累加 total_data
    if total_data.empty:
        total_data = month_sum_data
    else:
        ## 合併之前先分離經緯度，之後再補上（避免錯誤加總）
        total_data = pd.concat([total_data, month_sum_data])
        total_data = total_data.groupby('station name', as_index=False).agg({
            'lon': 'first',
            'lat': 'first',
            'hit': 'sum',
            'total': 'sum'
        })

## 加入命中率百分比
total_data['hit percent'] = total_data['hit'] / total_data['total'] * 100

## 顯示結果
print(total_data)

tg = 'hit percent'

prefigurance_hit_persent_list = total_data[tg].tolist()
prefigurance_lon_data_list = total_data['lon'].tolist()
prefigurance_lat_data_list = total_data['lat'].tolist()


# 設定經緯度範圍
lon_min, lon_max = 120, 122.1
lat_min, lat_max = 21.5, 25.5

##前估命中率繪圖
plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)

plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號

# 加載台灣的行政邊界
taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"  # 你需要提供台灣邊界的shapefile文件
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='white')
ax.add_feature(shape_feature)


# 加入經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

## 計算某個地方達到10mm/10min的次數 + colorbar
color_list = []

level = [0,3,10,17,24,52,66,80,87]
color_box = ['silver','purple','darkviolet','blue','g','y','orange','r']

for nb in prefigurance_hit_persent_list:
    more_then_maxma_or_not = 0
    for j in range(len(level)-1):
        if level[j]<nb<=level[j+1]:
            color_list.append(color_box[j])
            more_then_maxma_or_not = 1
            break
    if more_then_maxma_or_not == 0:
        color_list.append('lime')
        # print(nb)
# print(len(color_list))


# 標記經緯度點
ax.scatter(prefigurance_lon_data_list, prefigurance_lat_data_list, color=color_list, s=3, zorder=5)

# colorbar setting

nlevel = len(level)
cmap1 = mpl.colors.ListedColormap(color_box, N=nlevel)
cmap1.set_over('fuchsia')
cmap1.set_under('black')
norm1 = mcolors.Normalize(vmin=min(level), vmax=max(level))
norm1 = mcolors.BoundaryNorm(level, nlevel, extend='max')
im = cm.ScalarMappable(norm=norm1, cmap=cmap1)
cbar1 = plt.colorbar(im,ax=ax, extend='neither', ticks=level)


# 加入標籤
plt.xlabel('Longitude')
plt.ylabel('Latitude')

ax.set_title(tg)
# pic_save_path = f"{data_top_path}/前估後符/{data_source}_{year}{month}/前估命中率(%).png"
# plt.savefig(pic_save_path, bbox_inches='tight', dpi=300)

## 這是用來確認colorbar的配置
fig,ax1 = plt.subplots()
X = [i for i in range(len(prefigurance_hit_persent_list))]
Y = sorted(prefigurance_hit_persent_list)
ax1.plot(X,Y,color =  'black',marker = "*",linestyle = '--') #折線圖
ax1.set_title('這是用來確認colorbar的配置')


# 顯示地圖
plt.show()
from datetime import datetime
now_time = datetime.now()
formatted_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
# print(f"{formatted_time} 完成 Time：{year}{month}、dis：{dis}、source：{data_source}")