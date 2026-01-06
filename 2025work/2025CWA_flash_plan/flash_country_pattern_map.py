# -*- coding: utf-8 -*-
"""
各縣市閃電比例 Choropleth（單一來源 + 單一年份；不呼叫 flash_reader / 不畫散點）
- 從原始檔讀入指定來源 + 年度的閃電點
- 只保留位於指定經緯度框內的點；以此為母體計算各縣市比例
- 以色塊呈現比例，使用 msjh.ttc 中文字型
"""

import os, glob
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.patheffects as path_effects
from matplotlib.colors import Normalize
from matplotlib.ticker import PercentFormatter
import sys


## ============================== 參數區 ============================== ##
data_top_path = r"/home/steven/python_data/2025CWA_flash_plan"
county_shp_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

# 單一年份 + 單一來源（必選其一）
year_int = sys.argv[1] if len(sys.argv) > 1 else 2023
source_str = sys.argv[2] if len(sys.argv) > 2 else "TLDS"  # {"TLDS","EN","CWA"}

# 原始資料路徑
paths_dict = {
    "TLDS": f"{data_top_path}/raw_data/flash/TLDS",  # yyyy/yyyymm.txt
    "EN":   f"{data_top_path}/raw_data/flash/EN",    # lighting_yyyy.txt
    "CWA":  f"{data_top_path}/raw_data/flash/CWA",   # Lyyyy.csv
}

# 中文字型（微軟正黑）
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=12)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=18)

# 地圖與計算的經緯度限制（所有計算只採用此框內之閃電點）
lon_min, lon_max = 119.0, 122.5
lat_min, lat_max = 21.5, 25.5

# 輸出圖
result_fig_path = f"{data_top_path}/result/flash_pattern_draw/{year_int}_{source_str}.png"
## =================================================================== ##


## ============================== 讀縣市邊界 ============================== ##
county_gdf = gpd.read_file(county_shp_path)
if county_gdf.crs is None:
    raise ValueError("縣市圖層沒有 CRS，請確認 shapefile 投影資訊")
if str(county_gdf.crs).upper() not in ("EPSG:4326", "WGS84"):
    county_gdf = county_gdf.to_crs(epsg=4326)

county_name_col = "COUNTYNAME" if "COUNTYNAME" in county_gdf.columns else county_gdf.columns[0]
## =================================================================== ##


## ============================== 來源讀檔：只取 lon/lat ============================== ##
def _read_cwa_one_year_lonlat(year_int, cwa_root_path_str):
    fp = os.path.join(cwa_root_path_str, f"L{year_int}.csv")
    if not os.path.exists(fp):
        return pd.DataFrame(columns=["lon","lat"])
    # 優先只讀需要欄位，若欄位缺失則退回全讀
    try:
        df = pd.read_csv(fp, encoding="utf-8", usecols=["Longitude", "Latitude"])
        lon_col, lat_col = "Longitude", "Latitude"
    except Exception:
        df = pd.read_csv(fp, encoding="utf-8")
        df.columns = df.columns.astype(str).str.strip()
        cols_lower = {c.lower(): c for c in df.columns}
        lon_col = cols_lower.get("longitude")
        lat_col = cols_lower.get("latitude")
        if lon_col is None or lat_col is None:
            return pd.DataFrame(columns=["lon","lat"])

    out = pd.DataFrame({
        "lon": pd.to_numeric(df[lon_col], errors="coerce"),
        "lat": pd.to_numeric(df[lat_col],  errors="coerce")
    }).dropna(subset=["lon","lat"])
    return out

def _read_en_one_year_lonlat(year_int, en_root_path_str):
    fp = os.path.join(en_root_path_str, f"lightning_{year_int}.txt")
    if not os.path.exists(fp):
        return pd.DataFrame(columns=["lon","lat"])
    try:
        df = pd.read_csv(fp)
    except:
        df = pd.read_csv(fp, sep=r"[\s,]+", engine="python")

    # 允許 Lon/Lat 或 lon/lat
    if "lon" in df.columns and "lat" in df.columns:
        lon_col, lat_col = "lon", "lat"
    elif "Lon" in df.columns and "Lat" in df.columns:
        lon_col, lat_col = "Lon", "Lat"
    else:
        df.columns = df.columns.astype(str).str.strip()
        cols_lower = {c.lower(): c for c in df.columns}
        lon_col = cols_lower.get("lon")
        lat_col = cols_lower.get("lat")
        if lon_col is None or lat_col is None:
            return pd.DataFrame(columns=["lon","lat"])

    out = pd.DataFrame({
        "lon": pd.to_numeric(df[lon_col], errors="coerce"),
        "lat": pd.to_numeric(df[lat_col], errors="coerce")
    }).dropna(subset=["lon","lat"])
    return out


def _read_tlds_one_year_lonlat(year_int, tlds_root_path_str):
    """
    只讀取 TLDS 檔案中的經緯度欄位。
    規則（與 _read_tlds_one_year_df 一致）：
      - 年資料夾：<root>/<YYYY>/
      - 同時抓 .txt / .csv；檔名需以 YYYY 開頭
      - 編碼優先 UTF-8，失敗退 BIG5
    回傳欄位：["lon","lat"]
    """
    year_int = int(year_int)  # 型別保險
    year_folder_path_str = os.path.join(tlds_root_path_str, f"{year_int:04d}")
    if not os.path.isdir(year_folder_path_str):
        return pd.DataFrame(columns=["lon", "lat"])  # 年度資料夾不存在回空表

    ## 同時抓該年 .txt 與 .csv；要求檔名以 YYYY 開頭
    file_name_list = sorted([
        fn for fn in os.listdir(year_folder_path_str)
        if fn.startswith(f"{year_int:04d}") and (fn.endswith(".txt") or fn.endswith(".csv"))
    ])
    if not file_name_list:
        return pd.DataFrame(columns=["lon", "lat"])  # 沒檔案回空表

    dfs_list = []
    for file_name_str in file_name_list:
        file_path_str = os.path.join(year_folder_path_str, file_name_str)

        ## 先用 UTF-8，失敗才退 BIG5
        try:
            df = pd.read_csv(file_path_str, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path_str, encoding="big5")

        ## 欄名清理：移除 BOM 與首尾空白，避免 '﻿經度' / '﻿緯度' 類型問題
        df.columns = df.columns.astype(str).str.replace("\ufeff", "", regex=False).str.strip()

        ## 確保必要欄位存在（缺的補 NA；保守處理不同檔頭）
        for col in ["經度", "緯度"]:
            if col not in df.columns:
                df[col] = pd.NA

        ## 只取經緯度並轉為數值；經緯度缺失則丟掉
        tmp_df = pd.DataFrame({
            "lon": pd.to_numeric(df["經度"], errors="coerce"),
            "lat": pd.to_numeric(df["緯度"], errors="coerce")
        }).dropna(subset=["lon", "lat"])

        if not tmp_df.empty:
            dfs_list.append(tmp_df)

    if not dfs_list:
        return pd.DataFrame(columns=["lon", "lat"])
    return pd.concat(dfs_list, ignore_index=True)


def _get_points_lonlat_df(source_str, year_int, paths_dict):
    if source_str == "CWA":
        return _read_cwa_one_year_lonlat(year_int, paths_dict["CWA"])
    elif source_str == "EN":
        return _read_en_one_year_lonlat(year_int, paths_dict["EN"])
    elif source_str == "TLDS":
        return _read_tlds_one_year_lonlat(year_int, paths_dict["TLDS"])
    else:
        raise ValueError("source_str 必須是 {'TLDS','EN','CWA'}")
## =================================================================== ##


## ============================== 讀點、經緯度篩選、轉 GDF ============================== ##
pts_df = _get_points_lonlat_df(source_str, year_int, paths_dict)

# 只保留在指定經緯度框內的點
in_bbox_mask = (
    (pts_df["lon"] >= lon_min) & (pts_df["lon"] <= lon_max) &
    (pts_df["lat"] >= lat_min) & (pts_df["lat"] <= lat_max)
)
pts_df = pts_df.loc[in_bbox_mask].copy()

# 轉成 GeoDataFrame
if pts_df.empty:
    pts_gdf = gpd.GeoDataFrame(columns=["lon","lat","geometry"], crs="EPSG:4326")
else:
    pts_gdf = gpd.GeoDataFrame(
        pts_df,
        geometry=gpd.points_from_xy(pts_df["lon"], pts_df["lat"]),
        crs="EPSG:4326"
    )
## =================================================================== ##


## ============================== 各縣市計數（只針對框內點）與比例 ============================== ##
if pts_gdf.empty:
    # 沒有點，全部 0
    county_with_num_gdf = county_gdf[[county_name_col, "geometry"]].copy()
    county_with_num_gdf[source_str] = 0
    county_with_num_gdf["ratio"] = 0.0
    total_count = 0
else:
    # 空間連接：點 -> 縣市
    joined = gpd.sjoin(
        pts_gdf, county_gdf[[county_name_col, "geometry"]],
        how="inner", predicate="within"
    )
    grp = joined.groupby(county_name_col).size().reset_index(name=source_str)
    county_with_num_gdf = county_gdf.merge(grp, on=county_name_col, how="left").fillna({source_str: 0})
    total_count = float(county_with_num_gdf[source_str].sum())
    county_with_num_gdf["ratio"] = 0.0 if total_count <= 0 else county_with_num_gdf[source_str] / total_count
## =================================================================== ##


## ============================== 代表點與繪圖 ============================== ##
county_with_num_gdf["rep_point_geom"] = county_with_num_gdf.representative_point()
county_with_num_gdf["rep_lon"] = county_with_num_gdf["rep_point_geom"].x
county_with_num_gdf["rep_lat"] = county_with_num_gdf["rep_point_geom"].y

fig, ax = plt.subplots(figsize=(8, 10))

# Choropleth：固定比例範圍 0~20%
cmap = plt.get_cmap("Blues")
vmin, vmax = 0.0, 0.20  # 0% ~ 20%
norm = Normalize(vmin=vmin, vmax=vmax, clip=True)

# 超過上限的比例統一設為上限顏色
county_with_num_gdf["ratio_clipped"] = county_with_num_gdf["ratio"].clip(upper=vmax)

county_with_num_gdf.plot(
    ax=ax,
    column="ratio_clipped",
    cmap=cmap,
    linewidth=0.4,
    edgecolor="black",
)

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm._A = []

### 修改區開始 ###
# 改成一般數值格式（0.00 ~ 0.20）
cbar = plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
cbar.set_label("閃電比例[%]", fontproperties=myfont)

# 設定顯示刻度與格式（可選）
cbar.ax.yaxis.set_major_formatter(plt.FormatStrFormatter("%.2f"))  # 兩位小數
### 修改區結束 ###

for tick in cbar.ax.get_yticklabels():
    tick.set_fontproperties(myfont)


# 視窗與標題
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)

for _, row in county_with_num_gdf.iterrows():
    if not (lon_min <= row["rep_lon"] <= lon_max and lat_min <= row["rep_lat"] <= lat_max):
        continue
    ratio = float(row["ratio"]) if pd.notna(row["ratio"]) else 0.0
    if ratio < 0.001:
        continue
    txt = f"{ratio*100:.1f}"
    t = ax.text(row["rep_lon"], row["rep_lat"], txt,
                ha="center", va="center", fontsize=10, fontproperties=myfont,
                clip_on=True)
    t.set_path_effects([path_effects.withStroke(linewidth=1.5, foreground="white")])

ax.set_aspect("equal")

total_in_wan = round(total_count / 10000, 1)
title_str = f"{year_int} {source_str} 各縣市閃電比例 [%]（全台總閃電量 = {total_in_wan:g} 萬）"
ax.set_title(title_str, fontproperties=title_font)

plt.tight_layout()
os.makedirs(os.path.dirname(result_fig_path), exist_ok=True)
plt.savefig(result_fig_path, dpi=300, bbox_inches="tight")
print(f"地圖輸出： {result_fig_path}")
plt.show()
plt.close()
