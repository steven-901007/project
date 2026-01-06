import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# # 1. 讀取 CSV (請確認你的欄位名稱是 lon 和 lat)
# df = pd.read_csv("/home/steven/python_data/NTU_radar/need_data/20210530/20210530_040410_000.csv")

# # 2. 設定畫布與地圖投影
# plt.figure(figsize=(8, 8))
# ax = plt.axes(projection=ccrs.PlateCarree())

# # 3. 設定台灣範圍與畫海岸線
# ax.set_extent([119, 123, 21, 26])  # 經度 119-123, 緯度 21-26
# ax.coastlines(resolution='10m')    # 畫出高解析度海岸線

# # 4. 畫點 (x=經度, y=緯度)
# ax.scatter(df['lon'], df['lat'], color='red', s=1, transform=ccrs.PlateCarree())
# print(len(df['lon']))
# plt.title("Taiwan Map Plot")
# plt.savefig("/home/steven/python_data/NTU_radar/CV/text.png")import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import glob  # 1. 新增這個套件，用來搜尋檔案

# 定義檔案路徑模式
file_pattern = "/home/steven/python_data/NTU_radar/need_data/20210530/20210530_040410_*.csv"

# 2. 抓取所有符合的檔案路徑
all_files = glob.glob(file_pattern)

# 3. 讀取所有檔案並合併成一個 DataFrame
# 這裡使用列表生成式一次讀取，再用 concat 接起來
df_list = [pd.read_csv(filename) for filename in all_files]
df = pd.concat(df_list, ignore_index=True)

print(f"已讀取 {len(all_files)} 個檔案，總共有 {len(df)} 筆資料")

# 4. 設定畫布與地圖投影 (以下維持原樣)
plt.figure(figsize=(8, 8))
ax = plt.axes(projection=ccrs.PlateCarree())

# 設定台灣範圍與畫海岸線
ax.set_extent([119, 123, 21, 26])
ax.coastlines(resolution='10m')

# 5. 畫點
ax.scatter(df['lon'], df['lat'], color='red', s=1, transform=ccrs.PlateCarree())

plt.title("Taiwan Map Plot (Merged Data)")
plt.savefig("/home/steven/python_data/NTU_radar/CV/text.png")