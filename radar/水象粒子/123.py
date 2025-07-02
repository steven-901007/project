import wradlib as wrl

vol_path = r"C:\Users\steve\python_data\radar\20170602_u.RCWF\2017_0602\2C_CDD.vol\2017060201574000dBZ.vol\2017060201574000dBZ.vol" # 替換成你的路徑



import wradlib as wrl



try:
    attrs = wrl.io.read_rainbow(vol_path)
    result = f"✅ 成功讀取 Rainbow 資料，包含 {len(attrs)} 個主要層級。"
except ValueError as e:
    result = f"⚠️ 資料結構錯誤：{e}"
except Exception as e:
    result = f"❌ 其他錯誤：{e}"

print(result)

import os
print("實際讀取路徑：", vol_path)
print("檔案大小（bytes）：", os.path.getsize(vol_path))