import pandas as pd
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
import numpy as np
## ====== 參數設定 ======
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump/flash_data/raw_data"

target_type = "CG"  # 可選 "IC" 或 "CG"

lon_min, lon_max = 120.0, 122.1
lat_min, lat_max = 21.5, 25.5

## ====== CWA 資料處理 ======
cwa_path = os.path.join(data_top_path, "CWA")
cwa_counts = {}
flash_type_code = {
    'IC': 'Cloud',
    'CG': 'Ground'
} 

for file in tqdm(os.listdir(cwa_path),desc='CWA'):
    if file.endswith(".csv"):
        year = file.split(".")[0][-4:]
        file_path = os.path.join(cwa_path, file)
        df = pd.read_csv(file_path)

        # 確保欄位為字串再比對
        df["Major Code"] = df["Major Code"].astype(str).str.strip()

        df_filtered = df[
            (df["Cloud or Ground"] == flash_type_code[target_type]) &
            (df["Longitude"] >= lon_min) &
            (df["Longitude"] <= lon_max) &
            (df["Latitude"] >= lat_min) &
            (df["Latitude"] <= lat_max)
        ]
        cwa_counts[year] = len(df_filtered)

## ====== EN 資料處理 ======
en_path = os.path.join(data_top_path, "EN")
en_counts = {}

for file in tqdm(os.listdir(en_path),desc='EN'):
    if file.endswith(".txt"):
        year = file.split("_")[1].split(".")[0]
        file_path = os.path.join(en_path, file)
        df = pd.read_csv(file_path)

        df_filtered = df[
            (df["lightning_type"].str.strip() == target_type) &
            (df["lon"] >= lon_min) &
            (df["lon"] <= lon_max) &
            (df["lat"] >= lat_min) &
            (df["lat"] <= lat_max)
        ]
        en_counts[year] = len(df_filtered)

## ====== TLDS 資料處理 ======
tlds_path = os.path.join(data_top_path, "TLDS")
tlds_counts = {}

for year_folder in tqdm(os.listdir(tlds_path),desc='TLDS'):
    year_path = os.path.join(tlds_path, year_folder)
    if not os.path.isdir(year_path):
        continue

    count = 0
    for file in os.listdir(year_path):
        if file.endswith(".txt"):
            file_path = os.path.join(year_path, file)
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='big5')

            df_filtered = df[
                (df["雷擊型態"].str.strip() == target_type) &
                (df["經度"] >= lon_min) &
                (df["經度"] <= lon_max) &
                (df["緯度"] >= lat_min) &
                (df["緯度"] <= lat_max)
            ]
        elif file.endswith(".csv"):
            file_path = os.path.join(year_path, file)
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding='big5')

            df_filtered = df[
                (df["類型"].str.strip() == target_type) &
                (df["經度"] >= lon_min) &
                (df["經度"] <= lon_max) &
                (df["緯度"] >= lat_min) &
                (df["緯度"] <= lat_max)
            ]
        count += len(df_filtered)
    tlds_counts[year_folder] = count

## ====== 畫圖 ======
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False


# 確認所有年份
all_years = sorted(set(cwa_counts.keys()) | set(en_counts.keys()) | set(tlds_counts.keys()))

# 各資料來源的數量，沒有資料設為0
cwa_values = [cwa_counts.get(y, 0) for y in all_years]
en_values = [en_counts.get(y, 0) for y in all_years]
tlds_values = [tlds_counts.get(y, 0) for y in all_years]

print('cwa',cwa_values)
print('en',en_values)
print('tlds',tlds_values)

x = np.arange(len(all_years))
width = 0.25

import matplotlib.ticker as mtick

fig, ax = plt.subplots(figsize=(10, 6))

bar1 = ax.bar(x - width, cwa_values, width, label="CWA")
bar2 = ax.bar(x, en_values, width, label="EN")
bar3 = ax.bar(x + width, tlds_values, width, label="TLDS")

ax.set_xticks(x)
ax.set_xticklabels(all_years)
ax.set_xlabel("Year")
ax.set_ylabel(f"{target_type} Count (萬)")
ax.set_title(f"2018~2024 {target_type} 閃電資料統計")

ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{x/10000}'))

# ax.ticklabel_format(style='plain', axis='y')
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))  # 讓Y軸刻度整齊

# 上方數字（單位：萬）
# ax.bar_label(bar1, padding=3, labels=[f'{v}' for v in cwa_values])
# ax.bar_label(bar2, padding=3, labels=[f'{v}' for v in en_values])
# ax.bar_label(bar3, padding=3, labels=[f'{v}' for v in tlds_values])

ax.legend()
plt.tight_layout()
plt.show()
