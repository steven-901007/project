from glob import glob
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import os


data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = 2021

flash_data_list = [[],[]]
flash_raw_data_year_paths = f"{data_top_path}/閃電資料/raw_data/EN/{year}_EN/**.csv"

flash_raw_data_month_paths = glob(flash_raw_data_year_paths)
for flash_raw_data_month_path in flash_raw_data_month_paths:
    # print(flash_raw_data_month_path)
    flash_time = os.path.basename(flash_raw_data_month_path).split('.')[0]
    # print(flash_time)
    flash_data_list[0].append(flash_time)

    flash_datas = pd.read_csv(flash_raw_data_month_path)
    # print(flash_datas)
    flash_data_count = flash_datas.shape[0]
    # print(flash_data_count)
    flash_data_list[1].append(flash_data_count)


##測試EN閃電資料依月分分類.py有沒有錯
EN_flash_raw_data = pd.read_csv(f"{data_top_path}/閃電資料/raw_data/EN/{year}_EN/{year}_EN.txt")
EN_flash_raw_data_count = EN_flash_raw_data.shape[0]
print(f"{year}總資料量 = {EN_flash_raw_data_count} 筆")
for month in range(len(flash_data_list[0])):
    print(f"{flash_data_list[0][month]} ({flash_data_list[1][month]})")



# print(flash_data_list)
plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號
fig = plt.figure() #底圖(一張空白map可以在上面自行加上各種ax)
ax = fig.add_subplot()
ax.bar(flash_data_list[0],flash_data_list[1])
plt.xticks(rotation=75,size = 30)  # 旋轉 x 軸標籤，讓它們更易讀
plt.tight_layout()  # 自動調整佈局
plt.title(f'{year}各月閃電布局(資料來源：EN)',size = 30)
plt.show()