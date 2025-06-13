import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
import cartopy.feature as cfeature
import pyart

# ==== 中文設定 ====
plt.rcParams['font.sans-serif'] = ['MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# ==== 資料與雷達設定 ====
file_path = "C:/Users/steve/python_data/radar/PID/20240523000200.nc"
shapefile_path = "C:/Users/steve/python_data/radar/Taiwan_map_data/COUNTY_MOI_1090820.shp"
radar = pyart.io.read(file_path)

# ==== 雷達位置 ====
radar_lat = radar.latitude['data'][0]
radar_lon = radar.longitude['data'][0]

# ==== 剖面線方向設定（例如雷達往左上）====
length_deg = 1.2  # 經緯度方向延伸長度（越大線越長）

# 例如畫一條左上 → 右下的線（逆對角線）
lat0 = radar_lat + length_deg
lon0 = radar_lon - length_deg
lat1 = radar_lat - length_deg
lon1 = radar_lon + length_deg
print(lat0,lat1,lon0,lon1)
# ==== 畫地圖 ====
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.set_extent([119, 123.5, 21, 26.5])

# ==== 台灣邊界 ====
shape_feature = cfeature.ShapelyFeature(
    Reader(shapefile_path).geometries(),
    ccrs.PlateCarree(),
    edgecolor='r',
    facecolor='none'
)
ax.add_feature(shape_feature, linewidth=1)

# ==== 畫雷達位置點 ====
ax.plot(radar_lon, radar_lat, 'bo', markersize=8, label='Radar')

# ==== 畫剖面線（任意方向）====
ax.plot([lon0, lon1], [lat0, lat1], 'k--', linewidth=2, label='Cross-section Line')

# ==== 加格線與圖例 ====
gl = ax.gridlines(draw_labels=True)
gl.right_labels = False
ax.legend(loc='upper left')

# ==== 標題與顯示 ====
ax.set_title("垂直剖面位置示意圖（任意方向）")
plt.tight_layout()
plt.show()
