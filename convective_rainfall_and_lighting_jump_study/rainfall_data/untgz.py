import tarfile
import zipfile
import os
import sys
import platform

year = sys.argv[1].zfill(2) if len(sys.argv) > 1 else "2024"

# 設定路徑
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"

data_path = rf"{data_top_path}/rain_data/raw_data/{year}/"

## 遍歷檔案
for file in os.listdir(data_path):

    # 唯一前置：只處理壓縮檔
    if not (file.endswith(".tgz") or file.endswith(".tar.gz") or 
            file.endswith(".gz") or file.endswith(".zip")):
        continue

    file_path = os.path.join(data_path, file)
    print(f"🔍 偵測到壓縮檔：{file}")

    # 用檔名當資料夾（去掉.gz / .tgz / .tar.gz）
    folder_name = file.replace(".tar.gz", "").replace(".tgz", "").replace(".gz", "").replace(".zip", "")
    output_path = os.path.join(data_path, folder_name)
    os.makedirs(output_path, exist_ok=True)

    print(f"📂 解壓縮到：{output_path}")

    # ---------------------
    #      tar.gz / tgz
    # ---------------------
    if file.endswith(".tar.gz") or file.endswith(".tgz") or file.endswith(".gz"):
        try:
            with tarfile.open(file_path, "r:*") as tar:
                tar.extractall(output_path)
            print("✅ 解壓成功（tar）")
        except Exception as e:
            print(f"❌ tar 解壓失敗：{e}")

    # ---------------------
    #         zip
    # ---------------------
    elif file.endswith(".zip"):
        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                z.extractall(output_path)
            print("✅ 解壓成功（zip）")
        except Exception as e:
            print(f"❌ zip 解壓失敗：{e}")
