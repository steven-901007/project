import matplotlib.pyplot as plt
import matplotlib.image as mpimg





# 設定標記點的經緯度
point_lon = [122.5704,119]
point_lat = [23.7466,22]

# 設定經緯度範圍
lon_min, lon_max = 118, 123
lat_min, lat_max = 21, 26

# 讀取背景圖片
background_image_path = "C:/Users/steve/GitHub/project/研究所/台灣地圖背景.png"  # 替換為你的圖片路徑
background_image = mpimg.imread(background_image_path)

# 繪製空白的經緯度框架
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Coordinate Point with Background Image')

# 顯示背景圖片
ax.imshow(background_image, extent=[lon_min, lon_max, lat_min, lat_max], aspect='auto')

# 標記經緯度點
ax.scatter(point_lon, point_lat, color='red', s=100)  # s 參數控制點的大小


# 顯示地圖
plt.grid(True)
plt.show()
