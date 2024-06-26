import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import cartopy.feature as cfeature

## 無縣市邊界

data_top_path = "C:/Users/steve/python_data"

# 設定標記點的經緯度
point_lon = [119.86,120.04,119.89,120.04,119.90,119.89,119.88,119.83,119.82,119.88,119.99,119.92]
point_lat = [26.47,
26.43,
26.44,
26.10,
26.31,
26.32,
26.22,
26.35,
26.35,
26.33,
26.31,
26.43]
print(len(point_lon),len(point_lat))
## 繪圖












# 設定經緯度範圍
lon_min, lon_max = 119, 122.1
lat_min, lat_max = 21.5, 27.5

plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)

plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號

# 加載台灣的行政邊界
taiwan_shapefile = data_top_path+"/研究所/Taiwan_map_data/COUNTY_MOI_1090820.shp"  # 你需要提供台灣邊界的shapefile文件
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='white')
ax.add_feature(shape_feature)


# 加入經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

ax.scatter(point_lon,point_lat,color = 'r', s=3, zorder=5)
# 加入標籤
plt.xlabel('Longitude')
plt.ylabel('Latitude')

ax.set_title('全台雨量站座標')

# 顯示地圖
plt.show()