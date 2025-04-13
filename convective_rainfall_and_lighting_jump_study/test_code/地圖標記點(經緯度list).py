import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
from cartopy import geodesic



## 無縣市邊界

data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
dis = 36

# 設定標記點的經緯度
station_lon = 120.46

station_lat = 22.98

# print(len(point_lon),len(point_lat))
## 繪圖
data = pd.read_csv(f"{data_top_path}/閃電資料/EN/依時間分類/2021/06/202106010854.csv")

point_lon = data['lon']
point_lat = data['lat']









# 設定經緯度範圍
lon_min, lon_max = 120.0, 122.03
lat_min, lat_max = 21.88, 25.32

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

ax.scatter(point_lon,point_lat,color = 'r', s=3, zorder=5)

g = geodesic.Geodesic()
circle = g.circle(lon=station_lon, lat=station_lat, radius=dis*1000)  # radius in meters
ax.plot(circle[:, 0], circle[:, 1], color='blue', transform=ccrs.PlateCarree(),label = f"半徑 = {dis}")

# 加入標籤
plt.xlabel('Longitude')
plt.ylabel('Latitude')

ax.set_title('全台雨量站座標')

# 顯示地圖
plt.show()