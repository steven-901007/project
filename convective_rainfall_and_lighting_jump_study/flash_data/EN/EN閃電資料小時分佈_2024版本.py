import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
import os

## 設定檔案路徑
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = 2024  # 2024 檔案格式不同
flash_type = 'CG'  # all or IC or CG

## 設定台灣主島經緯度範圍
lon_min, lon_max = 120.0, 122.03
lat_min, lat_max = 21.88, 25.32

## 初始化 DataFrame
all_year_hourly_counts = None

## 讀取所有 CSV 檔案
EN_flash_data_paths = f"{data_top_path}/閃電資料/raw_data/EN/{year}_EN/**.csv"
result = glob(EN_flash_data_paths)

for EN_flash_data in result:
    print(f"讀取檔案: {EN_flash_data}")
    month = EN_flash_data.split('/')[-1].split('\\')[-1].split('.')[0].split('_')[-1]
    ## 讀取 CSV
    EN_flash_datas = pd.read_csv(EN_flash_data)

    ## 過濾台灣主島範圍
    main_island_lon_lat_range = (
        (lon_min < EN_flash_datas['longitude']) & (EN_flash_datas['longitude'] < lon_max) &
        (lat_min < EN_flash_datas['latitude']) & (EN_flash_datas['latitude'] < lat_max)
    )
    flash_datas_main_island = EN_flash_datas[main_island_lon_lat_range]

    ## 修正時間格式
    flash_datas_main_island['time'] = flash_datas_main_island['time'].apply(
        lambda x: f"{x} 00:00:00" if len(x) == 10 else x
    )
    flash_datas_main_island['H'] = pd.to_datetime(flash_datas_main_island['time']).dt.hour

    ## 根據閃電型態計算每小時閃電數
    if flash_type == 'all':
        hourly_counts = flash_datas_main_island['H'].value_counts().sort_index()
    elif flash_type == 'IC':
        hourly_counts = flash_datas_main_island[flash_datas_main_island['type'] == 1]['H'].value_counts().sort_index()
    elif flash_type == 'CG':
        hourly_counts = flash_datas_main_island[flash_datas_main_island['type'] == 0]['H'].value_counts().sort_index()
    else:
        raise TypeError("未知的 flash_type 選項，應該是 'all', 'IC' 或 'CG'")

    ## 確保 X 軸完整 (0~23)，如果某個小時沒有資料則補 0
    hourly_counts = hourly_counts.reindex(range(24), fill_value=0)
    
    ## 轉換成 DataFrame 以便合併
    hourly_counts_df = pd.DataFrame({'H': range(24), f'{month}': hourly_counts.values})
    ## 逐步合併 DataFrame
    if all_year_hourly_counts is None:
        all_year_hourly_counts = hourly_counts_df
    else:
        all_year_hourly_counts = pd.merge(all_year_hourly_counts, hourly_counts_df, on="H", how="outer")

all_year_hourly_counts['total'] = all_year_hourly_counts.iloc[:, 1:].sum(axis=1)

## 顯示最終合併結果
print(all_year_hourly_counts)




plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號
## 繪製折線圖
plt.figure(figsize=(10, 5))
for col in all_year_hourly_counts.columns:
    if col != 'H':  # 略過時間欄位
        plt.plot(all_year_hourly_counts['H'], all_year_hourly_counts[col], marker='o', linestyle='-', label=col)

plt.xlabel('Hour of Day')
plt.ylabel('Lightning Counts')
plt.title(f"{year} EN 閃電資料小時分佈\nlightning type = {flash_type}")
plt.xticks(range(24))  # X 軸刻度設為 0~23
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()
