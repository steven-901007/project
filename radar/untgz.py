import gzip
import shutil
import os
import sys

year = sys.argv[1] if len(sys.argv) > 1 else '2021'
month =  sys.argv[2] if len(sys.argv) > 1 else "05" 
day = sys.argv[3] if len(sys.argv) > 1 else "30" 

import platform
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/radar"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/radar"


## 資料夾位置
folder_path = f"{data_top_path}/data/{year}{month}{day}_u.RCWF"  # ← 修改成你的資料夾路徑

## 批次處理
for filename in os.listdir(folder_path):
    if filename.endswith(".gz"):
        gz_path = os.path.join(folder_path, filename)
        out_path = os.path.join(folder_path, filename[:-3])  # 去掉 .gz 副檔名

        # 解壓縮
        with gzip.open(gz_path, 'rb') as f_in:
            with open(out_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        print(f"解壓縮完成：{filename} ➜ {filename[:-3]}")