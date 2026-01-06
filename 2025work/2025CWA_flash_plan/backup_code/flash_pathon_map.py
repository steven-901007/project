# -*- coding: utf-8 -*-
"""
繪圖主程式（單一來源 + 單一年份；不呼叫 flash_reader）
- 從 flash_data/{year}_{source}.csv 讀入各縣市閃電數（此檔由 flash_reader 產生）
- 可選：是否呼叫 flash_points 來畫該來源的散點
- 使用指定字型 msjh.ttc 顯示中文（避免 Glyph missing）

#### 之後若需要可以改成繪製閃電(經過0.01經緯度加總的繪圖)熱點圖
"""

import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.patheffects as path_effects

# 若要畫散點需有 flash_points 模組
from flash_points import get_lightning_points

## ============================== 參數區 ============================== ##
data_top_path = r"/home/steven/python_data/2025CWA_flash_plan"
county_shp_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

paths_dict = {
    "TLDS": f"{data_top_path}/raw_data/flash/TLDS",
    "EN":   f"{data_top_path}/raw_data/flash/EN",
    "CWA":  f"{data_top_path}/raw_data/flash/CWA",
}

year_int = 2018
source_str = "CWA"             # {"TLDS","EN","CWA"}
use_flash_points_bool = False   # 是否畫散點

# 中文字型設定（msjh.ttc）
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=12)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=18)

# 地圖範圍
lon_min, lon_max = 119.0, 122.5
lat_min, lat_max = 21.5, 25.5

# 輸入 / 輸出
flash_counts_csv_path = f"{data_top_path}/result/flash_pattern_draw/flash_data/{year_int}_{source_str}.csv"
result_fig_path = f"{data_top_path}/result/flash_pattern_draw/county_map_counts_{year_int}_{source_str}.png"
## =================================================================== ##


## ============================== 讀縣市邊界 ============================== ##
county_gdf = gpd.read_file(county_shp_path)
if county_gdf.crs is None:
    raise ValueError("縣市圖層沒有 CRS，請確認 shapefile 投影資訊")
if str(county_gdf.crs).upper() not in ("EPSG:4326", "WGS84"):
    county_gdf = county_gdf.to_crs(epsg=4326)
county_name_col = "COUNTYNAME" if "COUNTYNAME" in county_gdf.columns else county_gdf.columns[0]
## =================================================================== ##


## ============================== 讀入縣市統計 ============================== ##
if not os.path.exists(flash_counts_csv_path):
    raise FileNotFoundError(f"找不到 {flash_counts_csv_path}，請先用 flash_reader 產出。")

counts_df = pd.read_csv(flash_counts_csv_path)
if county_name_col not in counts_df.columns or source_str not in counts_df.columns:
    raise ValueError(f"統計檔缺少必要欄位：{county_name_col}, {source_str}")

county_with_num_gdf = county_gdf.merge(
    counts_df[[county_name_col, source_str]],
    on=county_name_col, how="left"
).fillna({source_str: 0})
## =================================================================== ##


## ============================== 取得散點 ============================== ##
lon_lat_points_list = [[], []]
if use_flash_points_bool:
    lon_lat_points_list = get_lightning_points(
        data_source=source_str,
        years_list=[year_int],
        paths_dict=paths_dict
    )
## =================================================================== ##


## ============================== 代表點與繪圖 ============================== ##
county_with_num_gdf["rep_point_geom"] = county_with_num_gdf.representative_point()
county_with_num_gdf["rep_lon"] = county_with_num_gdf["rep_point_geom"].x
county_with_num_gdf["rep_lat"] = county_with_num_gdf["rep_point_geom"].y

fig, ax = plt.subplots(figsize=(8, 10))
county_gdf.plot(ax=ax, facecolor="none", edgecolor="black", linewidth=0.8)

if use_flash_points_bool and len(lon_lat_points_list[0]) > 0:
    ax.scatter(lon_lat_points_list[0], lon_lat_points_list[1], s=0.05, alpha=1, label=f"{source_str} 閃電點")

# 標註縣市閃電數字（白邊防重疊）
for _, row in county_with_num_gdf.iterrows():
    txt = f"{int(row[source_str])}" if pd.notna(row[source_str]) else "0"
    t = ax.text(row["rep_lon"], row["rep_lat"], txt,
                ha="center", va="center", fontsize=8, fontproperties=myfont)
    t.set_path_effects([path_effects.withStroke(linewidth=1.5, foreground="white")])

ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)
ax.set_aspect("equal")

# 中文標題
title_str = f"{year_int} {source_str}資料各縣市閃電數"
ax.set_title(title_str, fontproperties=title_font)

if use_flash_points_bool and len(lon_lat_points_list[0]) > 0:
    ax.legend(loc="lower left", prop=myfont)

plt.tight_layout()
os.makedirs(os.path.dirname(result_fig_path), exist_ok=True)
plt.savefig(result_fig_path, dpi=300, bbox_inches="tight")
print(f"地圖輸出： {result_fig_path}")
plt.show()
