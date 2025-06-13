import pyart
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime

# ==== 路徑與時間設定 ====
file_path = "C:/Users/steve/python_data/radar/PID/20240523000200.nc"
time_str = file_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

# ==== 讀取雷達 ====
radar = pyart.io.read(file_path)

# ==== gridding 成 3D 資料 ====
grid = pyart.map.grid_from_radars(
    radar,
    grid_shape=(41, 201, 201),  # (高度層數, y, x)
    grid_limits=((0, 20000), (-100000, 100000), (-100000, 100000)),  # 單位：公尺
    fields=['hydro_class']
)

# ==== 抽出垂直剖面（東西向）====
hydro_data = grid.fields['hydro_class']['data']  # shape: (z, y, x)
z = grid.z['data'] / 1000  # 高度 (km)
x = grid.x['data'] / 1000  # 水平距離 (km)
hydro_slice = hydro_data[:, hydro_data.shape[1] // 2, :]  # 抽中間一條 y 切面（東西向）

# ==== 畫圖 ====
fig, ax = plt.subplots(figsize=(10, 6))
cmap = plt.cm.get_cmap("tab10", 6)
pc = ax.pcolormesh(x, z, hydro_slice, cmap=cmap, vmin=0, vmax=5)

ax.set_xlabel("距離 (km)")
ax.set_ylabel("高度 (km)")
ax.set_title(f"水象粒子垂直剖面（東西向）\n{time_dt}")

# 加圖例
label_names = ['Rain', 'Melting Layer', 'Wet Snow', 'Dry Snow', 'Graupel', 'Hail']
patches = [mpatches.Patch(color=cmap(i), label=label_names[i]) for i in range(6)]
ax.legend(handles=patches, loc='upper right', title='Hydrometeors')

plt.colorbar(pc, ax=ax, label='Hydrometeor Type')
plt.tight_layout()
plt.show()
