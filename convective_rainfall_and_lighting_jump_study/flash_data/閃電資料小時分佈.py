import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
from glob import glob
from tqdm import tqdm

year = '2021'
month = '07'
dis = 36
flash_source = 'TLDS'
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"

##建立資料夾
def file_set(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print(file_path + " 已建立")
file_set(f"{data_top_path}/閃電資料/{flash_source}/閃電資料小時分佈/{year}{month}")

plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號


result_path = f"{data_top_path}/閃電資料/{flash_source}/lighting_jump/{flash_source}_{year}{month}_{dis}km/**.csv"
result = glob(result_path)
for data_path in tqdm(result,desc='資料處理中，請稍後...'):
    # print(data_path)
    station_name = data_path.split('/')[-1].split('\\')[-1].split('.')[0]
    # print(station_name)
    data_path = f"{data_top_path}/閃電資料/{flash_source}/lighting_jump/{flash_source}_{year}{month}_{dis}km/{station_name}.csv"
    data = pd.read_csv(data_path)

    # 確保時間格式正確
    data['LJ_time'] = pd.to_datetime(data['LJ_time'])

    # 依據小時進行分組並計算每小時的筆數
    data_hour_count = data.groupby(data['LJ_time'].dt.floor('h')).size().reset_index(name='count')

    # 🔹建立完整的時間範圍 (補齊所有可能的時間點)
    full_time_range = pd.date_range(start=data['LJ_time'].min().floor('D'), 
                                    end=data['LJ_time'].max().ceil('D'), 
                                    freq='h')

    # 轉為 DataFrame
    full_time_df = pd.DataFrame({'LJ_time': full_time_range})

    # 🔹合併，讓缺失的時間點補上 count=0
    data_hour_count = full_time_df.merge(data_hour_count, on='LJ_time', how='left').fillna(0)

    # 轉換日期 & 小時
    data_hour_count['date'] = data_hour_count['LJ_time'].dt.date
    data_hour_count['hour'] = data_hour_count['LJ_time'].dt.hour

    # 轉換為 Pivot Table
    pivot_table = data_hour_count.pivot(index='date', columns='hour', values='count')

    # 🔹繪製熱圖
    plt.figure(figsize=(12, 6))
    sns.heatmap(pivot_table, cmap="coolwarm", annot=True, fmt=".0f", linewidths=0.5)  # 用數字標記格子
    plt.xlabel("Hour")
    plt.ylabel("Day")
    plt.title(f"{year}/{month} station：{station_name}、flash source：{flash_source}")

    pic_save_path = f"{data_top_path}/閃電資料/{flash_source}/閃電資料小時分佈/{year}{month}/{station_name}.png"
    plt.savefig(pic_save_path, bbox_inches='tight', dpi=300)
    plt.close()

    # plt.show()
print(f"Time：{year}{month}、dis：{dis}、flash_source：{flash_source}")