import pandas as pd
import matplotlib.pyplot as plt


data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = 2021
flash_type = 'all' #all or IC or CG
title_name_time = 'Time'

lon_min, lon_max = 120.0, 122.03
lat_min, lat_max = 21.88, 25.32

EN_flash_datas = pd.read_csv(f"{data_top_path}/閃電資料/raw_data/EN/{year}_EN/{year}_EN.txt")
# print(EN_flash_datas)


main_island_lon_lat_range = (lon_min < EN_flash_datas['lon']) & (EN_flash_datas['lon'] < lon_max) & (lat_min < EN_flash_datas['lat']) & (EN_flash_datas['lat'] < lat_max)
flash_datas_main_island = EN_flash_datas[main_island_lon_lat_range]

flash_datas_main_island[title_name_time] = flash_datas_main_island[title_name_time].apply(
    lambda x: f"{x} 00:00:00" if len(x) == 10 else x
)


flash_datas_main_island['H'] = pd.to_datetime(flash_datas_main_island[title_name_time]).dt.hour

# print(flash_datas_main_island)


#閃電型態
if flash_type == 'all':
    hourly_counts = flash_datas_main_island['H'].value_counts().sort_index()
elif flash_type == 'IC':
    hourly_counts = flash_datas_main_island[flash_datas_main_island['lightning_type'] == 'IC']['H'].value_counts().sort_index()
elif flash_type == 'CG':
    hourly_counts = flash_datas_main_island[flash_datas_main_island['lightning_type'] == 'CG']['H'].value_counts().sort_index()
else:
    TypeError 

# print(hourly_counts)



# 確保 X 軸完整 (0~23)，如果某個小時沒有資料補 0
hourly_counts = hourly_counts.reindex(range(24), fill_value=0)
print(hourly_counts)

plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號



## 繪製折線圖
plt.figure(figsize=(10, 5))
plt.plot(hourly_counts.index, hourly_counts.values, marker='o', linestyle='-', color='b')

# 設定圖表標題與標籤
plt.xlabel('Hour of Day')
plt.title(f"{year} EN 閃電資料小時分佈\nlightning type = {flash_type}")
plt.xticks(range(24))  # X 軸刻度設為 0~23
plt.grid(True, linestyle='--', alpha=0.6)

plt.show()

