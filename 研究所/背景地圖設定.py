import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# 創建一個投影為 PlateCarree 的地圖
plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())

# 加載地形圖
ax.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
ax.add_feature(cfeature.COASTLINE)

# 設置地圖的範圍
ax.set_extent([118, 123, 21, 26])  # 台灣的大致範圍

# 加入經緯度格線
# ax.gridlines(draw_labels=True, linestyle='--')

# 加入標籤
plt.title('MAP')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# 顯示地圖
plt.show()
