# -*- coding: utf-8 -*-
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from matplotlib.font_manager import FontProperties
from matplotlib.colors import Normalize
import math 
import sys
# ==========================================
# 1. 設定與參數
# ==========================================
# 路徑設定
data_top_path = r"/home/steven/python_data/2025CWA_flash_plan"
county_shp_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

# 指定要分析的年份與來源
target_year = sys.argv[1] if len(sys.argv) > 1 else "2015"
target_source = sys.argv[2] if len(sys.argv) > 2 else "CWA"
ic_cg = sys.argv[3] if len(sys.argv) > 3 else'IC'
flash_data_path = f"{data_top_path}/city_counts/{target_year}_{target_source}.csv"

# 繪圖設定
save_path = f"{data_top_path}/result/flash_pattern_draw/count_area/{target_source}/{target_year}_{target_source}_{ic_cg}_Density.png"

from matplotlib.font_manager import FontProperties
# 字型設定
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=12)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=18)

# 地圖範圍 (WGS84 經緯度)
lon_min, lon_max = 119.0, 122.5
lat_min, lat_max = 21.5, 25.5

# ==========================================
# 2. 繪圖函式定義 (封裝)
# ==========================================
def draw_lightning_density_map(county_gdf, year,ic_or_cg, source, total_count, 
                               lon_min, lon_max, lat_min, lat_max, 
                               myfont, title_font, save_path):
    """
    繪製  閃電密度 Choropleth 地圖
    """
    fig, ax = plt.subplots(figsize=(8, 10))

    # --- 設定顏色映射 ---
    if ic_or_cg == 'IC':
        c = "Blues"
    elif ic_or_cg == 'CG':
        c = "Reds"
    cmap = plt.get_cmap(c) 
    vmin = 0.0
    real_max = county_gdf[f"{ic_or_cg}_density"].max()
    vmax = math.ceil(real_max / 5) * 5
    if vmax == 0: 
        vmax = 5
    norm = Normalize(vmin=vmin, vmax=vmax, clip=True)

    # --- 處理數據 (截斷超過上限的值以防顏色爆掉) ---
    # 注意：這裡複製一份以避免修改到原始資料
    plot_gdf = county_gdf.copy()
    plot_gdf["density_clipped"] = plot_gdf[f"{ic_or_cg}_density"].clip(upper=vmax)

    # --- 繪製主地圖 ---
    plot_gdf.plot(
        ax=ax,
        column="density_clipped", 
        cmap=cmap,
        norm=norm,
        linewidth=0.4,
        edgecolor="black",
    )

    # --- 設定 Colorbar ---
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    
    cbar = plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label(f"{ic_or_cg} 閃電密度 [筆/km²]", fontproperties=myfont)
    cbar.ax.yaxis.set_major_formatter(plt.FormatStrFormatter("%.1f")) 

    for tick in cbar.ax.get_yticklabels():
        tick.set_fontproperties(myfont)

    # --- 設定視窗範圍 ---
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    ax.set_aspect("equal")

    # --- 標註密度數值 ---
    # 計算代表點 (若無)
    if "rep_lon" not in plot_gdf.columns:
        plot_gdf["rep_point"] = plot_gdf.representative_point()
        plot_gdf["rep_lon"] = plot_gdf["rep_point"].x
        plot_gdf["rep_lat"] = plot_gdf["rep_point"].y

    for _, row in plot_gdf.iterrows():
        # 過濾範圍外
        if not (lon_min <= row["rep_lon"] <= lon_max and lat_min <= row["rep_lat"] <= lat_max):
            continue
        
        val = int(row[f"{ic_or_cg}"]) if pd.notna(row[f"{ic_or_cg}"]) else 0.0
        
            
        txt = f"{val}"
        t = ax.text(row["rep_lon"], row["rep_lat"], txt,
                    ha="center", va="center", fontsize=10, fontproperties=myfont,
                    clip_on=True, color='black')
        t.set_path_effects([path_effects.withStroke(linewidth=1.5, foreground="white")])

    # --- 標題與存檔 ---
    total_in_wan = round(total_count / 10000, 1)
    # 1. 根據密度欄位降序排序，取前 3 名
    target_col = f"{ic_or_cg}_density"
    top3_df = county_gdf.sort_values(target_col, ascending=False).head(3)
    
    # 2. 格式化文字 (例如: 花蓮縣=20.1、臺東縣=15.5...)
    # 使用 list comprehension 快速建立字串列表
    top3_list = [f"{row['COUNTYNAME']}" for _, row in top3_df.iterrows()]
    top3_text = "、".join(top3_list) # 用頓號連接

    # 3. 設定標題
    title_str = f"{year} {source} 各縣市 {ic_or_cg} 閃電密度\n（Top 3：{top3_text}）"
    ax.set_title(title_str, fontproperties=title_font)

    plt.tight_layout()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"地圖已儲存至： {save_path}")
    
    plt.show()
    plt.close()

# ==========================================
# 3. 主程式流程
# ==========================================

# (A) 讀取資料
print(f"正在讀取 CSV: {flash_data_path}")
flash_data = pd.read_csv(flash_data_path)

print(f"正在讀取地圖檔: {county_shp_path}")
gdf = gpd.read_file(county_shp_path)

# (B) 處理地圖與計算面積
# 1. 先轉為 TWD97 (EPSG:3826) 以計算準確面積 (單位: 平方公尺)
gdf_proj = gdf.to_crs(epsg=3826)
# 2. 計算面積並轉為平方公里
gdf_proj['area_km2'] = gdf_proj.area / 10**6
# 3. 將面積資訊映射回原始 WGS84 的 gdf (方便後續畫經緯度圖)
gdf['area_km2'] = gdf_proj['area_km2']

# (C) 合併資料 (Flash Data + Map Data)
# 保留必要的欄位進行合併
area_map = gdf[['COUNTYNAME', 'area_km2', 'geometry']]
merged_gdf = pd.merge(area_map, flash_data, on='COUNTYNAME', how='left')

# (D) 填補空值 (防止某些縣市沒閃電資料變成 NaN)
merged_gdf['IC'] = merged_gdf['IC'].fillna(0)
merged_gdf['CG'] = merged_gdf['CG'].fillna(0)

# (E) 計算密度 (核心邏輯)
# IC_density = IC數量 / 面積
merged_gdf['IC_density'] = merged_gdf['IC']  / merged_gdf['area_km2']
merged_gdf['CG_density'] = merged_gdf['CG']  / merged_gdf['area_km2']

# 簡單檢查
print("\n--- 密度計算結果 (前5筆) ---")
print(merged_gdf)

total_ic_count = merged_gdf['IC'].sum()

# (F) 執行繪圖
draw_lightning_density_map(
    county_gdf=merged_gdf, 
    year=target_year, 
    ic_or_cg = ic_cg,
    source=target_source, 
    total_count=total_ic_count,
    lon_min=lon_min, lon_max=lon_max, 
    lat_min=lat_min, lat_max=lat_max,
    myfont=myfont, title_font=title_font, 
    save_path=save_path
)