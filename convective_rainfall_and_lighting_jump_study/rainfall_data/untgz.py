import tarfile
import os
import sys

data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
# data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"
year = sys.argv[1].zfill(2) if len(sys.argv) > 1 else "2021"

## 資料夾設定
data_path = rf"{data_top_path}/rain_data/raw_data/{year}/"

## 遍歷資料夾內所有 .tgz 檔案
for file in os.listdir(data_path):
    if file.endswith(".tgz"):
        file_path = os.path.join(data_path, file)
        print(f"正在解壓縮：{file_path}")

        ## 用檔名當資料夾名
        folder_name = os.path.splitext(file)[0]
        output_path = os.path.join(data_path, folder_name)
        os.makedirs(output_path, exist_ok=True)

        with tarfile.open(file_path, "r:gz") as tar:
            tar.extractall(output_path)