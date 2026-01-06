import gzip
import shutil
import os


folder_path = "/home/steven/python_data/NTU_radar/data/RCNTU_20210530_31_rhi/RCNTU_data/raw_by_date/20210531/"  # 資料夾路徑

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