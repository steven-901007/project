import os, glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from cartopy.io.shapereader import Reader
import cartopy.crs as ccrs
from matplotlib.font_manager import FontProperties
import matplotlib.cm as matplotlib_cm
# 引入 BoundaryNorm 用來製作分層色階
from matplotlib.colors import ListedColormap, BoundaryNorm 
import time as t
from tqdm import tqdm
import datetime
from datetime import timedelta


## ============================== 參數設定 ============================== ##
data_top_path = "/home/steven/python_data/NTU_radar"
day = '20210530'  
time = '041004'   
csv_folder_path = f"{data_top_path}/need_data/{day}"

target_col = 'Zhh'# 'Zhh' 或 'Zdr' 或 'rho'
lon_min, lon_max = 121.0, 121.5  
lat_min, lat_max = 25, 25.50    

myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
TW_map_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

## ============================== 手動定義 CWA (中央氣象署) Colormap ============================== ##
def get_cwa_ref_cmap(target_col):
    if target_col == 'Zhh':
        """
        手動建立台灣中央氣象署 (CWA/CWB) 風格的雷達回波色階
        """
        # 定義色階 (這是根據你提供的圖檔與氣象署慣用色票整理的)
        cwa_colors = [
            '#00FFFF', # 00-05 dBZ (Cyan / 淺藍)
            '#0090FF', # 05-10 dBZ (Sky Blue / 天藍)
            '#0000FF', # 10-15 dBZ (Blue / 藍)
            '#00FF00', # 15-20 dBZ (Lime / 螢光綠)
            '#00C800', # 20-25 dBZ (Green / 綠)
            '#009000', # 25-30 dBZ (Dark Green / 深綠)
            '#FFFF00', # 30-35 dBZ (Yellow / 黃)
            '#FFD200', # 35-40 dBZ (Orange-Yellow / 橙黃)
            '#FF9000', # 40-45 dBZ (Orange / 橘)
            '#FF0000', # 45-50 dBZ (Red / 紅)
            '#C80000', # 50-55 dBZ (Dark Red / 深紅)
            '#900000', # 55-60 dBZ (Maroon / 褐紅) - 註: 有些版本這裡會轉紫，視具體年份而定，此處依圖示調整
            '#FF00FF', # 60-65 dBZ (Magenta / 洋紅)
            '#900090'  # 65+   dBZ (Purple / 紫)
        ]
        
        # 定義每個顏色對應的數值範圍 (0 到 70，每 5 一格)
        levels = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]

    elif target_col == 'Zdr':
        """
        手動建立 CWA 雙偏振差異色階
        """
        cwa_colors = [
            '#0000FF',
            '#0090FF',
            '#00FFFF',
            '#00FF00', 
            '#FF0000', 
            '#FFA500', 
            '#FFFF00', 
            '#800080'  
        ]
        
        levels = [-3, -1, 0, 1, 2, 2.5, 5, 7.5, 10]
    elif target_col == 'rho':
        """
        手動建立 CWA 相關係數色階
        """
        cwa_colors = [
            '#FF0000', # 0.0 - 0.5 (Red / 紅)
            '#FFA500', # 0.5 - 0.7 (Orange / 橘)
            '#FFFF00', # 0.7 - 0.85 (Yellow / 黃)
            '#00FF00', # 0.85 - 0.95 (Green / 綠)
            '#0000FF'  # 0.95 - 1.0 (Blue / 藍)
        ]
        
        levels = [0.0, 0.25, 0.5, 0.75, 0.95, 1.0]
        
     # 建立 Colormap
    cmap = ListedColormap(cwa_colors)

    cmap.set_under('gray')
    cmap.set_over('gray')         

    norm = BoundaryNorm(levels, ncolors=len(cwa_colors), clip=False)
    
    return cmap, norm, levels

## ============================== 讀檔與整併 ============================== ##
csv_file_list = sorted(glob.glob(os.path.join(csv_folder_path, f"{day}_{time}_*.csv")))

if not csv_file_list:
    raise FileNotFoundError(f"資料夾沒有 CSV：{csv_folder_path}")

output_dir = f"/home/steven/python_data/NTU_radar/CAPPI/{day}/{day}{time}/{target_col}"
os.makedirs(output_dir, exist_ok=True)

print(f"找到 {len(csv_file_list)} 個檔案，開始讀取...")

df_list = []
for fp in tqdm(csv_file_list):
    try:
        one_df = pd.read_csv(fp)
        one_df = one_df[['lon', 'lat', 'hight', target_col]]
        df_list.append(one_df)
    except Exception as e:
        print(f"⚠️ 讀檔失敗略過：{fp} -> {e}")
        print(one_df.columns)
        continue

if not df_list:
    raise ValueError("沒有成功讀取任何資料！")

all_data_df = pd.concat(df_list, ignore_index=True)
print(f"資料合併完成！共 {len(all_data_df)} 筆數據。")

## ============================== 資料篩選 ============================== ##
mask_geo = (
    (all_data_df["lon"] >= lon_min) & (all_data_df["lon"] <= lon_max) &
    (all_data_df["lat"] >= lat_min) & (all_data_df["lat"] <= lat_max) &
    (all_data_df["hight"] >= 0)
)
all_data_df = all_data_df.loc[mask_geo].copy()

# 這裡我們要保留 0 以上的資料，因為 CWA 色階是從 0 開始畫藍色的
# if target_col == 'Zhh':
#     all_data_df = all_data_df.loc[all_data_df['Zhh'] >= 0].copy()
    
print(f"篩選後數據量: {len(all_data_df)}")

## ============================== 迴圈繪圖 ============================== ##

# 【步驟 1】 取得 CWA 的 cmap 和 norm
cwa_cmap, cwa_norm, cwa_levels = get_cwa_ref_cmap(target_col)

for h_km in range(0, 11):
    center_h_m = h_km * 1000
    h_min_m = center_h_m - 500
    h_max_m = center_h_m + 500

    layer_df = all_data_df[
        (all_data_df["hight"] >= h_min_m) & 
        (all_data_df["hight"] < h_max_m)
    ].copy()

    if layer_df.empty:
        print(f"  ⚠️ {h_km}km 高度層無資料，跳過。")
        continue 
    
    print(f"處理高度 {h_km}km (資料數: {len(layer_df)})")

    # 排序
    layer_df.sort_values(by=target_col, ascending=True, inplace=True)

    # ========== 繪圖 ========== ##
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # 【步驟 2】 繪製 Scatter，加入 norm 參數
    sc = ax.scatter(
        layer_df["lon"].values,
        layer_df["lat"].values,
        c=layer_df[target_col].values,
        cmap=cwa_cmap,   # 使用 CWA 顏色
        norm=cwa_norm,   # 【關鍵】使用 CWA 的分層規則
        s=1.5,
        edgecolors='none',
        alpha=1.0,
        zorder=2
    )

    # 2. 加入台灣地圖
    ax.add_geometries(Reader(TW_map_path).geometries(), crs=ccrs.PlateCarree(),
                    facecolor='none', edgecolor='black', linewidth=1.5, alpha=0.7, zorder=5)

    # 3. 設定範圍
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)

    # 4. 標題與時間
    day_str = datetime.datetime.strptime(day, '%Y%m%d').strftime('%Y/%m/%d')
    time_str = (datetime.datetime.strptime(time, '%H%M%S') + timedelta(hours=8)).strftime('%H:%M:%S')
    ax.set_title(f"CAPPI {h_km}km ({target_col}) - {day_str} {time_str} LCT", fontproperties=title_font)

    # 5. Colorbar 設定 (要配合 levels)
    # spacing='uniform' 讓每個顏色格子在 colorbar 上等寬
    cbar = plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04, spacing='uniform', ticks=cwa_levels)


    gl = ax.gridlines(draw_labels=True)
    gl.right_labels = False    
    # 儲存
    output_path = f"{output_dir}/{day}_{time}_{h_km}km.png"
    plt.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)

print(f"✅ 所有圖檔處理完成！儲存於: {output_dir}")