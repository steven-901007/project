import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import re

## 讀取雨量站經緯度資料
def rain_station_location_data():
    data_path = "C:/Users/steve/python_data/研究所/雨量資料/2021_06/06/20210601/202106010000.QPESUMS_GAUGE.10M.mdf"
    lon_data_list = []  # 經度
    lat_data_list = []  # 緯度
    count_for_station_number = 0 #雨量站數量
    tatal_count_for_station_number = 0 #實際雨量站數量(包含不列入研究考量)之雨量站

    line = 0
    with open(data_path, 'r') as files:
        for file in files:
            if line >=3:
                data = re.split(re.compile(r'\s+|\n|\*'),file.strip())
                print(data)
                if 120 <float(data[4])< 122.1 and 21.5 <float(data[3])< 25.5:
                    lon_data_list.append(float(data[4]))
                    lat_data_list.append(float(data[3]))
                    count_for_station_number += 1
                tatal_count_for_station_number += 1 
            line +=1
    print(tatal_count_for_station_number)
    return lon_data_list, lat_data_list ,count_for_station_number ,tatal_count_for_station_number

lon_data_list, lat_data_list ,count_for_station_number ,tatal_count_for_station_number = rain_station_location_data()

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
taiwan_shapefile = "C:/Users/steve/python_data/研究所/Taiwan_map_data/COUNTY_MOI_1090820.shp"  # 你需要提供台灣邊界的shapefile文件
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='lightgray')
ax.add_feature(shape_feature)


# 加入經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

# 標記經緯度點
ax.scatter(lon_data_list, lat_data_list, color='red', s=3, zorder=5)

# 加入標籤
plt.xlabel('Longitude')
plt.ylabel('Latitude')
ax.set_title('全台雨量站座標\n雨量站數量：' + str(count_for_station_number))

# 顯示地圖
plt.show()
