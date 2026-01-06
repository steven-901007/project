import pandas as pd
import numpy as np
from glob import glob
import os

## ============================== 參數設定 ============================== ##
day = '20210530'
time = '040410'
lon_min, lon_max = 121.0, 122.0
lat_min, lat_max = 24.50, 25.50
# 修改處：確保 PID_table 設定為 dolan2009
PID_table = 'dolan2009'
max_height_km = 15

# 修改處：根據 Dolan and Rutledge (2009) 論文摘要定義的 7 種粒子類型 
if PID_table == 'dolan2009':
    hydrometeor_type_dict = {
        0: 'RN',   # Rain 
        1: 'DZ',   # Drizzle 
        2: 'AG',   # Aggregates 
        3: 'CR',   # Crystals 
        4: 'LDG',  # Low-density graupel 
        5: 'HDG',  # High-density graupel 
        6: 'VI'    # Vertical ice 
    }
    draw_hydrometeor_type = list(hydrometeor_type_dict.keys())

data_top_path = "/home/steven/python_data/NTU_radar"
data_folder_path = f"{data_top_path}/need_data/{day}/"
datas = glob(os.path.join(data_folder_path, f"{day}_{time}*.csv"))

## ============================== 初始化矩陣 ============================== ##
height_levels = range(max_height_km)
columns = [hydrometeor_type_dict[i] for i in draw_hydrometeor_type]
final_counts_df = pd.DataFrame(0, index=height_levels, columns=columns)

## ============================== 主程式 ============================== ##
if not datas:
    raise FileNotFoundError(f"找不到檔案：{data_folder_path}{day}_{time}*.csv")

for data in datas:
    print(f"📄 讀取檔案：{data}")
    df = pd.read_csv(data)

    # 1. 經緯度與高度篩選
    df = df[(df['lon'].between(lon_min, lon_max)) & 
            (df['lat'].between(lat_min, lat_max))].copy()
    
    # 2. 高度轉換與篩選 (hight 為公尺轉為 km 索引)
    df['height_km'] = (df['hight'] / 1000).astype(int)
    df = df[df['height_km'].between(0, max_height_km - 1)]

    # 3. ⚡ 統計分類分布
    if not df.empty:

        # 使用 crosstab 計算各高度與類別的頻次
        counts = pd.crosstab(df['height_km'], df['hydrometeor_type'])

        # 累計至總表
        final_counts_df = final_counts_df.add(counts, fill_value=0)

## ============================== 輸出結果 ============================== ##
print(f"📊 各高度 Hydrometeor ({PID_table}) 類別分布統計表：\n")
final_counts_df.index = [f"{i:02d} km" for i in final_counts_df.index]
print(final_counts_df.to_string(justify='center'))