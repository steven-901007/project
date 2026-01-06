"""
比較20257/28~8/4 與其他年份(2018~2025)的閃電嘉義台南區域年際變化差異程度
"""

import pandas as pd
import geopandas as gpd

data_top_path = "/home/steven/python_data/2025CWA_flash_plan"
flash_data_root = f"{data_top_path}/raw_data/flash/CWA/"
county_shp_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

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

print(f"已載入篩選區域: {target_names}")
print("-" * 30)

year_list = []
IC_7_list = []
IC_8_list = []
CG_7_list = []
CG_8_list = []

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
            
        # -----------------------------------------------------------

        # ================= 3. 加入嘉義台南篩選 =================

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
        
        print(f"Year: {year} (7-8月) | 原始筆數: {len(gdf_points)} -> 嘉義台南筆數: {len(gdf_final)}")
        
        # 印出結果檢查
        need_flash_ic = gdf_final[gdf_final['Cloud or Ground'] == 'Cloud']
        need_flash_cg = gdf_final[gdf_final['Cloud or Ground'] == 'Ground']
        need_flash_ic_7 = need_flash_ic[need_flash_ic['time_lct'].dt.month == 7]
        need_flash_ic_8 = need_flash_ic[need_flash_ic['time_lct'].dt.month == 8]
        need_flash_cg_7 = need_flash_cg[need_flash_cg['time_lct'].dt.month == 7]
        need_flash_cg_8 = need_flash_cg[need_flash_cg['time_lct'].dt.month == 8]

        # print(need_flash_ic)
        print(f"  - 雲閃總數: {len(need_flash_ic)} (7月: {len(need_flash_ic_7)}，8月: {len(need_flash_ic_8)})")
        print(f"  - 地閃總數: {len(need_flash_cg)} (7月: {len(need_flash_cg_7)}，8月: {len(need_flash_cg_8)})")

        year_list.append(year)
        IC_7_list.append(len(need_flash_ic_7))
        IC_8_list.append(len(need_flash_ic_8))
        CG_7_list.append(len(need_flash_cg_7))
        CG_8_list.append(len(need_flash_cg_8))
            
    except FileNotFoundError:
        print(f"檔案不存在: {flash_path}")

print("-" * 30)
for i in range(len(year_list)):
    print(f"Year: {year_list[i]} | IC_7: {IC_7_list[i]} | IC_8: {IC_8_list[i]} | CG_7: {CG_7_list[i]} | CG_8: {CG_8_list[i]}")


import matplotlib.pyplot as plt
import os
from matplotlib.font_manager import FontProperties
import numpy as np
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
plt.rcParams['axes.unicode_minus'] = False

# 繪製柱狀圖

width = 0.2  # 柱狀圖寬度
fig, ax = plt.subplots(figsize=(12, 6))


ax.bar([i + width/2 for i in year_list], IC_7_list, width, label='7月IC', color='blue')
ax.bar([i + width/2 for i in year_list], IC_8_list, width,bottom=np.array(IC_7_list), label='8月IC', color='skyblue')

ax.bar([i - width/2 for i in year_list], CG_7_list, width, label='7月CG', color='red')
ax.bar([i - width/2 for i in year_list], CG_8_list, width,bottom=np.array(CG_7_list), label='8月CG', color='lightcoral')

plt.legend(prop=myfont)
plt.ylabel('閃電數量', fontproperties=myfont)
plt.title('2018-2025年 7、8月 \n嘉義台南 閃電數量 source = CWA', fontproperties=title_font)

os.makedirs(f"{data_top_path}/result/2018_2025_78month_flash", exist_ok=True)
save_path = f"{data_top_path}/result/2018_2025_78month_flash/2018_2025_78month_flash_IC_CG.png"

plt.savefig(save_path,dpi = 300)
print(save_path + " 已儲存完成")