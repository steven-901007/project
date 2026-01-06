"""
畫2015~2024 CWA、EN(2018~2024)、TLDS 台東花蓮閃電bar圖
"""

import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np # 需要補上這行
from matplotlib.font_manager import FontProperties

# 1. 設定
data_top_path = "/home/steven/python_data/2025CWA_flash_plan"
folder_path = f"{data_top_path}/city_counts/" 

# ==========================================
# 指定要計算的縣市
# ==========================================
target_counties = ['臺東縣', '花蓮縣'] 

# 2. 讀取與處理
files = glob.glob(os.path.join(folder_path, "*.csv"))
data = []

for f in files:
    fname = os.path.basename(f)
    try:
        parts = fname.replace(".csv", "").split("_")
        year, source = parts[0], parts[1]
    except:
        continue 

    try:
        df = pd.read_csv(f, encoding='utf-8')
    except:
        try:
            df = pd.read_csv(f, encoding='big5') # 增加容錯
        except:
             continue

    # ==========================================
    # 根據列表篩選資料
    # ==========================================
    if target_counties:
        df = df[df['COUNTYNAME'].isin(target_counties)]

    # 計算篩選後的總和
    data.append({
        'Year': int(year),
        'Source': source,
        'CG': df['CG'].sum(),
        'IC': df['IC'].sum()
    })

df_res = pd.DataFrame(data)

# ==========================================
# 修改重點：補齊缺失資料 (例如 EN 2015-2017) 避免繪圖報錯
# ==========================================
# 建立完整的年份與來源索引
all_years = range(2015, 2025)
all_sources = ['CWA', 'EN', 'TLDS']
full_index = pd.MultiIndex.from_product([all_years, all_sources], names=['Year', 'Source'])

# 將現有資料重新索引，缺失補 0
df_res = df_res.set_index(['Year', 'Source']).reindex(full_index, fill_value=0).reset_index()
df_res = df_res.sort_values(['Year', 'Source'])

print(df_res)

# 3. 繪圖
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)

fig, ax = plt.subplots(figsize=(12, 6)) # 調整畫布大小讓 Bar 不會太擠
year_list = list(all_years)

width = 0.25 # 調整寬度

# 設定顏色字典 (格式: Source: (IC Color, CG Color))
# CWA: 藍色系, EN: 綠色系, TLDS: 紅/橘色系
color_map = {
    'CWA':  ('tab:blue', 'lightskyblue'),
    'EN':   ('tab:green', 'lightgreen'),
    'TLDS': ('tab:orange', 'navajowhite')
}

# 設定位置偏移量 (讓三個 Bar 並排)
offset_map = {
    'CWA': -width,
    'EN': 0,
    'TLDS': width
}

for source_draw in all_sources:
    # 取得該 Source 的資料
    source_data = df_res[df_res['Source'] == source_draw]
    
    # 確保資料是按照年份排序的
    ic_data = source_data['IC'].values
    cg_data = source_data['CG'].values
    
    # 計算 X 軸位置
    x_pos = np.array(year_list) + offset_map[source_draw]
    
    c_ic, c_cg = color_map[source_draw]

    # 畫 IC
    ax.bar(x_pos, ic_data, width, label=f'{source_draw} IC', color=c_ic, edgecolor='grey', linewidth=0.5)
    
    # 畫 CG (堆疊在 IC 上)
    ax.bar(x_pos, cg_data, width, bottom=ic_data, label=f'{source_draw} CG', color=c_cg, edgecolor='grey', linewidth=0.5)

# 設定 X 軸刻度
plt.xticks(year_list, fontproperties=myfont)
plt.ylabel('閃電數量[筆]', fontproperties=myfont)
plt.title('臺東、花蓮閃電數量統計 (2015-2024)', fontproperties=title_font)

# 圖例 (放外面避免擋住)
plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left', borderaxespad=0.)

plt.tight_layout()

# 儲存
save_folder = f"{data_top_path}/result/Taitung_Hualien"
os.makedirs(save_folder, exist_ok=True)
save_path = f"{save_folder}/3_source_2015_2024_flash.png"
plt.savefig(save_path, dpi=300)
print(f"Saved to: {save_path}")