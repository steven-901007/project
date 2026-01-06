## 讀 CSV，網格化取每格 ZHH "最大值" (Composite Reflectivity)
import os, glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from cartopy.io.shapereader import Reader
import cartopy.crs as ccrs
from matplotlib.font_manager import FontProperties
from matplotlib.colors import ListedColormap
from tqdm import tqdm
## ============================== 參數設定 ============================== ##
data_top_path = "/home/steven/python_data/NTU_radar"
day = '20210530'
time = '040410'
csv_folder_path = f"{data_top_path}/need_data/{day}"
target_col = 'Zhh'

# 顯示範圍
lon_min, lon_max = 121.0, 122.0
lat_min, lat_max = 24.50, 25.50
# grid_res_deg = 0.005  # 建議：稍微放寬一點點 (約500m) 填補空隙，或者維持 0.001 看細節

save_path = f"{data_top_path}/CV"
os.makedirs(save_path, exist_ok=True)
save_png_path = f"{save_path}/{day}_{time}_{target_col}.png"

myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)




# 台灣地圖 Shapefile 路徑
TW_map_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

## ============================== 讀檔與整併 ============================== ##
csv_file_list = sorted(glob.glob(os.path.join(csv_folder_path, f"{day}_{time}_*.csv")))

if not csv_file_list:
    raise FileNotFoundError(f"資料夾沒有 CSV：{csv_folder_path}")

print(f"找到 {len(csv_file_list)} 個檔案，開始讀取...")

all_data_df = pd.DataFrame()


for fp in tqdm(csv_file_list):
    try:
        one_df = pd.read_csv(fp)
        one_df = one_df[['lon', 'lat', 'hight',target_col]].copy()
        all_data_df = pd.concat([all_data_df, one_df], ignore_index=True)
    except Exception as e:
        print(f"⚠️ 讀檔失敗略過：{fp} -> {e}")
        continue
    # print(len(all_data_df))

    # print(len(one_df))
    # print(len(all_data_df))
    # print('------------------------')
    # t.sleep(1)
print(f"資料合併完成！共 {len(all_data_df)} 筆數據。")
print(all_data_df.head())
print(f'max{target_col}:',all_data_df[target_col].max(),f'min{target_col}:',all_data_df[target_col].min())

# 
# 經緯度範圍篩選
mask_geo = (
    (all_data_df["lon"] >= lon_min) & (all_data_df["lon"] <= lon_max) &
    (all_data_df["lat"] >= lat_min) & (all_data_df["lat"] <= lat_max) &
    (all_data_df["hight"] >= 0)  # 高度大於等於 0 米
)
all_data_df = all_data_df.loc[mask_geo].copy()

if target_col == 'Zhh':
    all_data_df = all_data_df.loc[all_data_df['Zhh'] >= 0].copy()
    print(f'max{target_col}:',all_data_df[target_col].max(),f'min{target_col}:',all_data_df[target_col].min())

print(f"資料經緯度篩選完成！共 {len(all_data_df)} 筆數據。")
# print(all_data_df.head())
print(f"maxhight:",all_data_df['hight'].max(),f"minhight:",all_data_df['hight'].min())
print(all_data_df[all_data_df[target_col]>70])
# ========== 繪圖 ========== ##
fig = plt.figure(figsize=(10, 8))
ax = plt.axes(projection=ccrs.PlateCarree())

# 1. 使用 layer_df (篩選過高度的資料)
sc = plt.scatter(
    all_data_df["lon"].values,
    all_data_df["lat"].values,
    c=all_data_df[target_col].values,
    cmap='jet', 
    vmin=0,
    vmax=75,
    s=0.5,           # 點的大小稍微大一點點可能比較清楚，看解析度
    alpha=1.0      # 不透明
)

# 台灣地圖 Shapefile 路徑
TW_map_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
# 2. 加入台灣地圖
ax.add_geometries(Reader(TW_map_path).geometries(), crs=ccrs.PlateCarree(),
                facecolor='none', edgecolor='black', linewidth=1.5, alpha=0.7)

# 3. 設定範圍與標籤
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# 4. 設定正確的標題 (顯示時間與高度)


# 5. 加入 Colorbar
cbar = plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
# cbar.set_label(target_col)
# 設定標題與軸
ax.set_title(f"最強{target_col}\n{day} {time}", fontproperties=title_font)


# 儲存
plt.savefig(save_png_path, dpi=300, bbox_inches="tight") # 解析度提高到300以看清數字
print(f"✅ 完成！最大回波數值圖已儲存至： {save_png_path}")
# plt.show()
plt.close(fig)
