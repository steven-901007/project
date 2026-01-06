# -*- coding: utf-8 -*-
"""
繪製2018-2025 7、8月嘉義、台南大雨閃電分布
區分IC/CG閃電，每年輸出一張（導入微軟正黑體）
不分小時都用同一種顏色
"""

import os
import pandas as pd
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from matplotlib.font_manager import FontProperties
from matplotlib import cm, colors
import geopandas as gpd


## ============================== 路徑設定 ============================== ##
data_top_path = "/home/steven/python_data/2025CWA_flash_plan"
flash_data_root = f"{data_top_path}/raw_data/flash/CWA/"
county_shp_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
result_folder_path = f"{data_top_path}/result/flash_pattern/2018_2025_78month_year_flash/"
os.makedirs(result_folder_path, exist_ok=True)


## ============================== 中文字型設定 ============================== ##
# 中文字型（微軟正黑）
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=12)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=12)

## ============================== 參數設定 ============================== ##
start_lct_dt = pd.Timestamp(2025, 7, 28, 0, 0, 0, tz='Asia/Taipei')
end_lct_dt   = pd.Timestamp(2025, 8, 4, 23, 59, 59, tz='Asia/Taipei')

lon_min_float, lon_max_float = 120.0, 121.0
lat_min_float, lat_max_float = 22.8, 23.66

# ================= 1. 準備地圖資料 =================
# 讀取縣市界線
county_gdf = gpd.read_file(county_shp_path)

# 確保座標系統 (WGS84)
if county_gdf.crs is None or str(county_gdf.crs).upper() not in ("EPSG:4326", "WGS84"):
    county_gdf = county_gdf.to_crs(epsg=4326)

# 鎖定嘉義台南
target_names = ['嘉義縣', '嘉義市', '臺南市']
county_col = "COUNTYNAME" if "COUNTYNAME" in county_gdf.columns else "COUNTY_NA"

# 建立篩選用的 GeoDataFrame
target_gdf = county_gdf[county_gdf[county_col].isin(target_names)][['geometry', county_col]]

## ============================== 繪圖函式 ============================== ##
def _draw_base_map(ax):
    county_shp_reader = Reader(county_shp_path)
    county_records = county_shp_reader.records()

    for record in county_records:
        # 嘗試抓縣市名稱欄位（各版 shapefile 命名略有不同）
        props = record.attributes
        name = props.get('COUNTYNAME', props.get('COUNTY_NA', ''))

        # 嘉義、台南縣市 → 綠色，其餘灰色
        if name  in ['嘉義縣', '嘉義市', '臺南市']:
            edge_color = 'r'
            lw = 0.5
            z = 3
        else:
            edge_color = 'gray'
            lw = 0.5
            z = 2
        ax.add_geometries(
            [record.geometry],
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor=edge_color,
            linewidth=lw,
            zorder=z
        )


def _plot_flash(ax, df,ic,cg):
    if df.empty:
        return
    df_ic = df[df['Cloud or Ground'] == 'Cloud']
    df_cg = df[df['Cloud or Ground'] == 'Ground']
    max_digits = len(str(max(ic, cg)))
    ic_label = f'$\\mathtt{{IC:{ic:>{max_digits}}}}$ 筆'
    cg_label = f'$\\mathtt{{CG:{cg:>{max_digits}}}}$ 筆'
    # IC (Cloud)
    ax.scatter(df_ic['Longitude'], df_ic['Latitude'], s=1,marker ='o',edgecolors='blue',facecolors='none', linewidths = 0.2, alpha=0.7,
               transform=ccrs.PlateCarree(), label=ic_label,zorder = 5)

    # CG (Ground)
    ax.scatter(df_cg['Longitude'], df_cg['Latitude'], s=1,marker = 'x', c='green',linewidths = 0.2, alpha=1,
               transform=ccrs.PlateCarree(), label=cg_label,zorder = 4)

def _draw(df_day,title,ic,cg,result_folder_path,out_name):
    fig, ax = plt.subplots( subplot_kw={'projection': ccrs.PlateCarree()})
    _draw_base_map(ax)
    _plot_flash(ax, df_day,ic,cg)
    ax.set_extent([lon_min_float, lon_max_float, lat_min_float, lat_max_float], crs=ccrs.PlateCarree())
    ax.set_title(title, fontproperties=title_font)
    ax.legend(
        loc='lower right',
        prop=myfont,        # 保持字型與字體大小
        markerscale=3.0,    # ← 圖例符號放大倍率（預設 1.0，可試 2~3）
        handlelength=1.8,   # 控制圖例符號與文字距離
        handletextpad=0.4   # 控制間距
        )

    out_path = os.path.join(result_folder_path, out_name)
    plt.savefig(out_path,dpi = 600,bbox_inches='tight')
    # plt.show()
    plt.close(fig)
    print(f"已輸出： {out_path}")

## ============================== 每年一張 ============================== ##
# ================= 2. 迴圈邏輯 =================
for year in range(2018, 2026):
    if year in [2018, 2019, 2020, 2021, 2022, 2023, 2024]:
        flash_path = f"{flash_data_root}/L{year}.csv"
    else:
        flash_path = f"{flash_data_root}/2025_0701-0811.csv"
    try:
        if year in [2018, 2019, 2020, 2021, 2022, 2023]:
            all_flash_data = pd.read_csv(
                flash_path,
                header=0, # 這裡一定要加，告訴程式忽略原本的第一行
                names=[
                    'Solution Key','Epoch Time','no title','Nanoseconds',
                    'Major Code','Minor Code','Latitude','Longitude',
                    'Altitude','Amplitude','Cloud or Ground','Major Axis',
                    'Minor Axis','Theta','GDOP', 
                    'Lineup Sensors','Redundant Verify Sensors'
                ]
            )
        elif year == 2024:
            all_flash_data = pd.read_csv(
                flash_path,
                header=0, # 這裡一定要加，告訴程式忽略原本的第一行
                names=[
                    'Solution Key','Epoch Time','wtf was that','Milliseconds',
                    'Major Code','Minor Code','Latitude','Longitude',
                    'Altitude','Amplitude','Cloud or Ground','Major Axis',
                    'Minor Axis','Theta','GDOP', 
                    'Lineup Sensors','Redundant Verify Sensors',
                    'Rcvr1','Rcvr2','Rcvr3','Rcvr4'
                ]

            )            
        elif year == 2025:
            all_flash_data = pd.read_csv(flash_path)
        # -----------------------------------------------------------
        # 修改部分：恢復時間處理並篩選 7、8 月
        # -----------------------------------------------------------
        
        # 1. 轉換時間格式 (必須先轉成 datetime 才能判斷月份)
        all_flash_data['time'] = pd.to_datetime(all_flash_data['Epoch Time'], utc=True)
        all_flash_data['time_lct'] = all_flash_data['time'].dt.tz_convert('Asia/Taipei')
        # print(all_flash_data['time_lct'].head())
        # 2. 篩選月份 (只留 7月 和 8月)
        # .dt.month 會回傳月份數字 (1-12)
        month_mask = all_flash_data['time_lct'].dt.month.isin([7, 8])
        all_flash_data = all_flash_data[month_mask].copy()
        
        # 如果篩選後沒資料，就跳過這一年
        if all_flash_data.empty:
            print(f"Year: {year} | 該年度 7-8 月無資料")
            continue

                # 轉成 GeoDataFrame
        gdf_points = gpd.GeoDataFrame(
            all_flash_data,
            geometry=gpd.points_from_xy(all_flash_data["Longitude"], all_flash_data["Latitude"]),
            crs="EPSG:4326"
        )
        
        # 空間交集 (Spatial Join)：只保留在 target_gdf (嘉義台南) 內的點
        gdf_final = gpd.sjoin(
            gdf_points, 
            target_gdf, 
            how="inner", 
            predicate="within"
        )

        ic = gdf_final[gdf_final['Cloud or Ground'] == 'Cloud'].shape[0]
        cg = gdf_final[gdf_final['Cloud or Ground'] == 'Ground'].shape[0]
        print(f"Year: {year} | 嘉義、台南 7-8月閃電筆數： IC={ic}，CG={cg}")
        out_name = f"{year}_78month_chiayi_tainan_flash.png"
        _draw(gdf_final, f"{year}年 7、8月\n嘉義、台南閃電分布",ic,cg,result_folder_path,out_name) #一年一張
        for month in [7,8]:
            month_result_folder_path = f"{result_folder_path}/{year}"
            os.makedirs(month_result_folder_path, exist_ok=True)
            month_mask = gdf_final['time_lct'].dt.month == month
            gdf_month = gdf_final[month_mask].copy()
            ic_month = gdf_month[gdf_month['Cloud or Ground'] == 'Cloud'].shape[0]
            cg_month = gdf_month[gdf_month['Cloud or Ground'] == 'Ground'].shape[0]
            out_name = f"{year}_{month:02d}_month_chiayi_tainan_flash.png"
            _draw(gdf_month, f"{year}年 {month}月\n嘉義、台南閃電分布",ic_month,cg_month,month_result_folder_path,out_name) #每月一張


        
    except FileNotFoundError:
        print(f"檔案不存在: {flash_path}")

print("全部完成！")