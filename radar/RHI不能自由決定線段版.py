import pyart
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime

# ==== 中文設定 ====
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# ==== 檔案設定 ====
file_path = "C:/Users/steve/python_data/radar/PID/20240523000200.nc"
time_str = file_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

# ==== 讀取雷達 ====
radar = pyart.io.read(file_path)

# ==== 加入 hydro_class 分類欄位 ====
n_rays, n_bins = radar.fields['reflectivity']['data'].shape
vol_class = np.full((n_rays, n_bins), -1, dtype=int)
vol_mask = np.ones((n_rays, n_bins), dtype=bool)

for sweep in range(radar.nsweeps):
    start_idx = radar.sweep_start_ray_index['data'][sweep]
    end_idx = radar.sweep_end_ray_index['data'][sweep] + 1

    try:
        z = radar.fields['reflectivity']['data'][start_idx:end_idx]
        zdr = radar.fields['differential_reflectivity']['data'][start_idx:end_idx]
        rhohv = radar.fields['cross_correlation_ratio']['data'][start_idx:end_idx]
        kdp = radar.fields['kdp_maesaka']['data'][start_idx:end_idx]
    except KeyError:
        continue

    z_mask = np.ma.getmaskarray(z)
    zdr_mask = np.ma.getmaskarray(zdr)
    rhohv_mask = np.ma.getmaskarray(rhohv)
    kdp_mask = np.ma.getmaskarray(kdp)
    valid_mask = ~(z_mask | zdr_mask | rhohv_mask | kdp_mask)

    classification = np.full(z.shape, -1, dtype=int)
    z_valid = z[valid_mask]
    zdr_valid = zdr[valid_mask]
    rhohv_valid = rhohv[valid_mask]
    kdp_valid = kdp[valid_mask]

    label = np.full(z_valid.shape, -1)
    label[(z_valid >= 20) & (z_valid <= 45) & (zdr_valid >= 0.5) & (zdr_valid <= 2.5) & (rhohv_valid > 0.97) & (kdp_valid > 0.5)] = 0
    label[(z_valid >= 25) & (z_valid <= 40) & (zdr_valid > 1) & (rhohv_valid >= 0.90) & (rhohv_valid <= 0.96)] = 1
    label[(z_valid >= 15) & (z_valid <= 35) & (zdr_valid >= 0.5) & (zdr_valid <= 1.5) & (rhohv_valid >= 0.90) & (rhohv_valid <= 0.96)] = 2
    label[(z_valid >= 10) & (z_valid <= 30) & (zdr_valid >= 0.0) & (zdr_valid <= 0.5) & (rhohv_valid > 0.97)] = 3
    label[(z_valid >= 30) & (z_valid <= 45) & (zdr_valid >= 0.0) & (zdr_valid <= 0.3) & (rhohv_valid >= 0.85) & (rhohv_valid <= 0.95)] = 4
    label[(z_valid >= 50) & (zdr_valid >= -1.0) & (zdr_valid <= 1.0) & (rhohv_valid < 0.90)] = 5

    classification[valid_mask] = label
    vol_class[start_idx:end_idx, :] = classification
    vol_mask[start_idx:end_idx, :] = ~valid_mask

# ==== 放入 radar 欄位 ====
masked_class = np.ma.masked_array(vol_class, mask=vol_mask)
class_field = {
    'data': masked_class,
    'units': 'category',
    'long_name': 'hydrometeor_type',
    'standard_name': 'hydrometeor_type',
    'valid_min': 0,
    'valid_max': 5
}
radar.add_field('hydro_class', class_field, replace_existing=True)
print(radar.fields['hydro_class'])
# # ==== gridding（建立立體格點）====
# grid = pyart.map.grid_from_radars(
#     radar,
#     grid_shape=(41, 201, 201),  # z, y, x
#     grid_limits=((0, 20000), (-100000, 100000), (-100000, 100000)),
#     fields=['hydro_class']
# )

# # ==== 抽東西向剖面 ====
# hydro_data = grid.fields['hydro_class']['data']
# z = grid.z['data'] / 1000
# x = grid.x['data'] / 1000
# hydro_slice = hydro_data[:, hydro_data.shape[1] // 2, :]
# hydro_slice = np.ma.masked_where(hydro_slice == -1, hydro_slice)  # 加這行處理無效值

# # ==== 畫圖 ====
# fig, ax = plt.subplots(figsize=(10, 6))
# cmap = plt.cm.get_cmap("tab10", 6)
# pc = ax.pcolormesh(x, z, hydro_slice, cmap=cmap, vmin=0, vmax=5)

# ax.set_xlabel("距離 (km)")
# ax.set_ylabel("高度 (km)")
# ax.set_title(f"水象粒子垂直剖面（東西向）\n{time_dt}")

# label_names = ['Rain', 'Melting Layer', 'Wet Snow', 'Dry Snow', 'Graupel', 'Hail']
# patches = [mpatches.Patch(color=cmap(i), label=label_names[i]) for i in range(6)]
# ax.legend(handles=patches, loc='upper right', title='Hydrometeors')

# plt.colorbar(pc, ax=ax, label='Hydrometeor Type')
# plt.tight_layout()
# plt.show()
