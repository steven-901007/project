from glob import glob
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import os


data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"


flash_data_list = [[],[]]
flash_raw_data_year_paths = glob(f"{data_top_path}/閃電資料/raw_data/EN/**")
for flash_raw_data_year_path in tqdm(flash_raw_data_year_paths,desc='資料讀取中...'):
    # print(flash_raw_data_year_path)
    flash_raw_data_month_paths = glob(flash_raw_data_year_path + "/**.csv")
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

# print(flash_data_list)
plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號
fig = plt.figure() #底圖(一張空白map可以在上面自行加上各種ax)
ax = fig.add_subplot()
ax.bar(flash_data_list[0],flash_data_list[1])
plt.xticks(rotation=75,size = 30)  # 旋轉 x 軸標籤，讓它們更易讀
plt.tight_layout()  # 自動調整佈局
plt.title('各月閃電布局(資料來源：EN)',size = 30)
plt.show()