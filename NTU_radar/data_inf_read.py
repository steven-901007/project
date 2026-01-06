# -*- coding: utf-8 -*-
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import os
import glob

## ============================== 路徑與時間設定 ============================== ##
data_top_path = "/home/steven/python_data/NTU_radar"

# rhi.nc 檔案所在資料夾
# rhi_folder_path = "/home/steven/python_data/NTU_radar/data/RCNTU_20210530_31_rhi/RCNTU_data/raw_by_date/20210530"
rhi_folder_path = "/home/steven/python_data/NTU_radar/data/RCNTU_sample/data/"

# time_str = "20210530"
# radar_style = 'rhi' # 'rhi' 或 'scn'
time_str ="20250707"
radar_style = 'rhi'


# 找出這個時間點的所有 rhi.nc 檔案
pattern = os.path.join(rhi_folder_path, f"*{time_str}*.{radar_style}.nc")
nc_files = sorted(glob.glob(pattern))

print("🔍 找到的檔案：")
for fp in nc_files:
    print("  ", fp)

if not nc_files:
    raise FileNotFoundError(f"在 {rhi_folder_path} 找不到符合 {pattern} 的檔案")

## ============================== 字型與輸出資料夾 ============================== ##
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)

save_path = f"/home/steven/python_data/NTU_radar/data_inf_draw/{time_str}"
os.makedirs(save_path, exist_ok=True)

## ============================== 先用第一個檔案抓變數名 ============================== ##
with Dataset(nc_files[0]) as ds0:
    var_names = list(ds0.variables.keys())

print("📘 檔案變數列表：")
print(var_names)
print("=" * 60)

## ============================== 逐變數彙整所有檔案的數值 ============================== ##
for var_name in var_names:
    all_values_list = []

    # 逐檔讀取這個變數
    for nc_path in nc_files:
        with Dataset(nc_path) as ds:
            if var_name not in ds.variables:
                continue  # 理論上應該都有，但保險起見

            var = ds.variables[var_name]
            data = var[:]

            # 攤平並處理 masked array
            flat = data.compressed() if hasattr(data, 'compressed') else data.flatten()

            # 只留數值型資料
            if flat.size == 0 or not np.issubdtype(flat.dtype, np.number):
                continue

            # 去掉 NaN / inf
            valid_values = flat[np.isfinite(flat)]
            if valid_values.size == 0:
                continue

            all_values_list.append(valid_values)

    # 如果這個變數在所有檔案裡都沒有有效數值，就略過
    if not all_values_list:
        print(f"🧩 變數：{var_name} 在所有檔案中沒有有效數值，略過")
        print("-" * 60)
        continue

    # 把所有檔案的數值串在一起
    all_values = np.concatenate(all_values_list)

    print(f"🧩 變數：{var_name}")
    print(f"  從 {len(nc_files)} 個檔案收集的總筆數：{all_values.size}")
    print(f"  max：{np.nanmax(all_values)}, min：{np.nanmin(all_values)}")
    print("-" * 60)

    # ==================「值 vs 出現次數」折線圖（所有檔案合併）================== #
    unique_vals, counts = np.unique(all_values, return_counts=True)

    # 依照 X 值排序
    sort_idx = np.argsort(unique_vals)
    unique_vals = unique_vals[sort_idx]
    counts = counts[sort_idx]

    # 畫折線圖
    plt.figure()
    plt.plot(unique_vals, counts, linestyle="-")
    plt.xlabel("變數值", fontproperties=myfont)
    plt.ylabel("出現次數", fontproperties=myfont)

    ##設定正常資料範圍
    if var_name == "Zhh":
        plt.xlim(0,75)  
        plt.ylim(0,500) #這是猜的數值
    if var_name == "zdr":
        plt.xlim(-10, 10)


    plt.title(f"{var_name} (N={all_values.size})", fontproperties=title_font)
    plt.grid(True)
    plt.tight_layout()

    out_png = f"{save_path}/data_inf_read_{var_name}_{time_str}.png"
    plt.savefig(out_png, dpi=300)
    plt.show()
    plt.close()

print("✅ 全部變數繪圖完成")




# # -*- coding: utf-8 -*-
# from netCDF4 import Dataset
# import numpy as np
# import matplotlib.pyplot as plt

# nc_path = "/home/steven/python_data/NTU_radar/data/RCNTU_sample/data/0092_20250707_000307_000.rhi.nc" #檔案路徑

# data_top_path = "/home/steven/python_data/NTU_radar"
# ds = Dataset(nc_path)

# print("📘 檔案內容：")
# print(ds.variables.keys())
# print("="*60)

# from matplotlib.font_manager import FontProperties
# myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
# title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)


# import os
# save_path = f"{data_top_path}/data_inf_draw"                # 確保目錄存在
# os.makedirs(save_path, exist_ok=True)

# for var_name in ds.variables.keys():
#     var = ds.variables[var_name]
#     data = var[:]

#     print(f"🧩 變數：{var_name}")
#     print(f"  shape：{data.shape}")

#     # 只印有效資料（去掉 masked）
#     flat = data.compressed() if hasattr(data, 'compressed') else data.flatten()
#     if flat.size > 0:
#         print(f"  前五筆：{flat[:5]}")
#         print(f"  後五筆：{flat[-5:]}")
#         print(f"max：{np.nanmax(data)}, min：{np.nanmin(data)}")
#     else:
#         print("  （無有效資料）")
#     print("-"*60)

#     # ================== 這裡開始做「值 vs 次數」折線圖 ================== #
#     # 只對數值型變數畫圖（排除字串、時間之類）
#     if flat.size == 0 or not np.issubdtype(flat.dtype, np.number):
#         continue

#     # 去掉 NaN
#     valid_values = flat[np.isfinite(flat)]
#     if valid_values.size == 0:
#         continue

#     # 找出「每一個數值」和「出現次數」
#     unique_vals, counts = np.unique(valid_values, return_counts=True)

#     # 依照 X 值排序（保險起見）
#     sort_idx = np.argsort(unique_vals)
#     unique_vals = unique_vals[sort_idx]
#     counts = counts[sort_idx]

#     # 畫折線圖
#     plt.figure()
#     plt.plot(unique_vals, counts, marker="", linestyle="-")
#     plt.xlabel("變數值", fontproperties=myfont)
#     plt.ylabel("出現次數", fontproperties=myfont)
#     plt.title(f"{var_name} (N={valid_values.size})",fontproperties=title_font)
#     plt.grid(True)
#     plt.tight_layout()
#     plt.savefig(f"{save_path}/data_inf_read_{var_name}.png", dpi=300)
#     # ========================================================== #

# # 一次把所有 figure 跳出來
#     plt.show()

# plt.close('all')
