import pandas as pd
import os
from glob import glob
import matplotlib.pyplot as plt

"""
***-1.csv ==> 01秒存資料 資料包含 時間 溫度 含水量 雨
***-2.csv ==> 02秒存資料 資料包含 時間 溫度 相對溼度 風速 陣風速度 風向 參數 太陽輻射
"""

group = 'SL' #F、S、SL (R是對照組)
parameter = 'Temp'  # Temp、water_content、rain

## 中文時間轉 ISO 格式
def convert_chinese_time_to_iso(time_str):  # 把「09/12/25 下午01時00分01秒」轉成「09/12/25 PM01:00:01」
    time_str = str(time_str).strip()
    time_str = time_str.replace("上午", "AM").replace("下午", "PM")
    time_str = time_str.replace("時", ":").replace("分", ":").replace("秒", "")
    return time_str

def convert_datetime_series(time_series):  # 轉成 pandas 的 datetime
    time_series_norm = time_series.apply(convert_chinese_time_to_iso)
    return pd.to_datetime(time_series_norm, format="%m/%d/%y %p%I:%M:%S")

## ============================== 讀取所有 -1.csv ============================== ##
data_top_path = "/home/steven/python_data/2025Pingtung"
save_path = f"{data_top_path}/results"
os.makedirs(save_path, exist_ok=True)
data_folder_path = f"{data_top_path}/data/2025-11-4(DTF-CSV)/"
data_paths = glob(os.path.join(data_folder_path, "*-1.csv"))


all_group_data_dict = {}  # 存每個 group 的 DataFrame：{ group_name: df }

for data_path in sorted(data_paths):
    group_name = os.path.basename(data_path).split("-")[3]  # e.g. S2, S3, SL1, SL2
    print("讀取中：", group_name)

    data = pd.read_csv(
        data_path,
        skiprows=2,    # 跳過「繪圖標題」和欄位說明那一行
        sep=",",
        names=["時間", "Temp", "water_content", "rain"]  # 時間 溫度 含水量 雨
    )

    ## 轉時間格式
    data['time'] = convert_datetime_series(data['時間'])

    ## 只保留要用的欄位，並照時間排序
    data = data[['time', parameter]].sort_values('time')

    all_group_data_dict[group_name] = data  # 存起來

print("可用的 group_name：", list(all_group_data_dict.keys()))

## ============================== 選擇要畫的 group ============================== ##
if group == 'F':
    groups_to_plot_list = ["F1", "F2", "F3", "R1"]
elif group == 'S':
    groups_to_plot_list = ["S1", "S2", "S3", "R1"]
elif group == 'SL':
    groups_to_plot_list = ["SL1", "SL2", "R1"]


## ============================== 字型設定 ============================== ##
from matplotlib.font_manager import FontProperties
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
## ============================== 畫在同一張圖 ============================== ##
plt.figure(figsize=(12, 6))

for group_name in groups_to_plot_list:
    if group_name not in all_group_data_dict:
        print(f"⚠ 找不到 group {group_name}，略過")
        continue

    group_data_df = all_group_data_dict[group_name]
    color = "red" if group_name == "R1" else None
    plt.plot(group_data_df['time'], group_data_df[parameter], label=group_name, color=color)

plt.xlabel("時間", fontproperties=myfont)

#單位符號
if parameter == 'Temp':
    plt.ylabel("溫度 (°C)", fontproperties=myfont)
elif parameter == 'water_content':
    plt.ylabel("含水量 (%)", fontproperties=myfont)
elif parameter == 'rain':
    plt.ylabel("雨量 (mm)", fontproperties=myfont)
plt.title(f"各測點{parameter}時間序列", fontproperties=title_font)


plt.legend(title="Group")
plt.grid(True)
plt.tight_layout()
# plt.show()
save_png_path = f"{save_path}/{parameter}_group{group}.png"
plt.savefig(save_png_path, dpi=300)
print(f"✅ 完成，已輸出： {save_png_path}")