import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature

# 讀取經緯度資料
data_path = "C:/Users/steve/python_data/研究所/雨量資料/rain_gauge_lat_lon.txt"
lon_data_list = []  # 經度
lat_data_list = []  # 緯度

with open(data_path, encoding='utf-8', errors='replace') as file:
    lines = file.readlines()  # 讀取所有行
    for line in lines:
        data = line.strip().split()
        lon_data_list.append(float(data[1]))
        lat_data_list.append(float(data[2]))

# 繪圖
plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())

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
ax.set_title('全台雨量站座標')

# 顯示地圖
plt.show()
