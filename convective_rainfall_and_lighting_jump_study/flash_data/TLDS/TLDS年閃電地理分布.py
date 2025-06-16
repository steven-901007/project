from tqdm import tqdm
import pandas as pd
import os
from glob import glob
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from matplotlib.colors import ListedColormap, BoundaryNorm

# ==== 基本設定 ====
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = 2024
flash_type = 'CG'  # 可選 'IC', 'CG', 'all'
flash_type = 'IC'
# ==== 讀取 TLDS 資料 ====
data_folder = f"{data_top_path}/閃電資料/raw_data/TLDS/{year}/"
file_paths = sorted(glob(os.path.join(data_folder, f"{year}*")))
all_data = []

for file_path in tqdm(file_paths, desc="讀取TLDS資料"):
    try:
        data = pd.read_csv(file_path, encoding='utf-8')
    except:
        data = pd.read_csv(file_path, encoding='big5')

    data['日期時間'] = pd.to_datetime(data['日期時間'], errors='coerce')
    data = data.dropna(subset=['日期時間'])
    data["hour"] = data["日期時間"].dt.hour
    data["month"] = data["日期時間"].dt.month
    all_data.append(data)

lightning_data_df = pd.concat(all_data, ignore_index=True)

# ==== 類型過濾 ====
if year in [2023 , 2024]:
    if flash_type == 'IC':
        df_plot = lightning_data_df[lightning_data_df['類型'] == 'IC']
    elif flash_type == 'CG':
        df_plot = lightning_data_df[lightning_data_df['類型'] == 'CG']
    elif flash_type == 'all':
        df_plot = lightning_data_df[lightning_data_df['類型'].isin(['IC', 'CG'])]
    else:
        raise ValueError("flash_type 必須是 'IC', 'CG', 或 'all'")
else:
    if flash_type == 'IC':
        df_plot = lightning_data_df[lightning_data_df['雷擊型態'] == 'IC']
    elif flash_type == 'CG':
        df_plot = lightning_data_df[lightning_data_df['雷擊型態'] == 'CG']
    elif flash_type == 'all':
        df_plot = lightning_data_df[lightning_data_df['雷擊型態'].isin(['IC', 'CG'])]
    else:
        raise ValueError("flash_type 必須是 'IC', 'CG', 或 'all'")

# ==== 繪製 heatmap (month-hour) ====
def plot_heatmap(data, title, ax):
    full_index = pd.MultiIndex.from_product([range(1, 13), range(0, 24)], names=['month', 'hour'])
    count_table = data.groupby(['month', 'hour']).size().reindex(full_index, fill_value=0).unstack()
    sns.heatmap(
        count_table, ax=ax, cmap='YlOrRd',
        linewidths=0.5, annot=False,
        xticklabels=True, yticklabels=True
    )
    ax.set_title(f"{year} TLDS {title} Lightning Count", fontsize=14)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Month")
    ax.invert_yaxis()

fig, ax = plt.subplots(figsize=(9, 6))
plot_heatmap(df_plot, flash_type, ax)
plt.tight_layout()
plt.savefig(f"G:/我的雲端硬碟/工作/2025cook/工作進度_閃電/TLDS/{year}_{flash_type}_hour_and_month.png", dpi=300)

# ==== 繪製空間分布圖（地圖） ====
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# 地圖範圍與解析度設定
lon_min, lon_max = 120.0, 122.03
lat_min, lat_max = 21.88, 25.32
lon_lat_gap = 0.01

# 過濾台灣本島資料
main_island_range = (
    (df_plot['經度'] > lon_min) & (df_plot['經度'] < lon_max) &
    (df_plot['緯度'] > lat_min) & (df_plot['緯度'] < lat_max)
)
df_main_island = df_plot[main_island_range]

# 建立格網
lon_bins = np.arange(lon_min, lon_max + lon_lat_gap, lon_lat_gap)
lat_bins = np.arange(lat_min, lat_max + lon_lat_gap, lon_lat_gap)

H, xedges, yedges = np.histogram2d(
    df_main_island['經度'], df_main_island['緯度'],
    bins=[lon_bins, lat_bins]
)

# 色階設定
colors = ["white", "plum", "slateblue", "blue", "green", "yellow", "orange", "red"]
cmap = ListedColormap(colors)
bounds = [0, 20, 50, 100, 200, 400, 500, 600, 700]
norm = BoundaryNorm(bounds, cmap.N)

# 畫圖
fig = plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)

# 加上台灣 shapefile 邊界
taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='none')
ax.add_feature(shape_feature)

# 加上格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

# 閃電分布熱圖
mesh = ax.pcolormesh(xedges, yedges, H.T, cmap=cmap, norm=norm, shading="auto", transform=ccrs.PlateCarree())

# 顏色條
cbar = plt.colorbar(mesh, ax=ax, orientation="vertical", shrink=0.7, pad=0.05)
cbar.set_ticks(bounds)
cbar.set_ticklabels(list(map(str, bounds)))

# 標題與標籤
plt.xlabel("Longitude", fontsize=12)
plt.ylabel("Latitude", fontsize=12)
flash_label = flash_type if flash_type != 'all' else 'IC+CG'
ax.set_title(f"{year} TLDS {flash_label} 閃電分佈", fontsize=14)

# 存圖
plt.savefig(f"G:/我的雲端硬碟/工作/2025cook/工作進度_閃電/TLDS/{year}_{flash_label}_map.png", dpi=300)
print(f"已完成 {year} TLDS {flash_label}：月時圖 + 空間分布圖")
