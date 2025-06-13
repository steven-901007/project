import pyart
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime
from pyproj import Geod

# ==== 中文設定 ====
plt.rcParams['font.sans-serif'] = ['MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# ==== 參數設定 ====
file_path = "C:/Users/steve/python_data/radar/PID/20240523000200.nc"
lon0, lat0 = 121.7, 25.07
lon1, lat1 = 124.0, 25.07  # 可以修改任意兩點

# ==== 讀取雷達資料 ====
radar = pyart.io.read(file_path)
time_str = file_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

# ==== 初始化分類矩陣 ====
n_rays, n_bins = radar.fields['reflectivity']['data'].shape
vol_class = np.full((n_rays, n_bins), -1, dtype=int)
vol_mask = np.ones((n_rays, n_bins), dtype=bool)

# ==== 分類 sweep 中所有格點 ====
for sweep in range(radar.nsweeps):
    start = radar.sweep_start_ray_index['data'][sweep]
    end = radar.sweep_end_ray_index['data'][sweep] + 1

    try:
        z = radar.fields['reflectivity']['data'][start:end]
        zdr = radar.fields['differential_reflectivity']['data'][start:end]
        rhohv = radar.fields['cross_correlation_ratio']['data'][start:end]
        kdp = radar.fields['kdp_maesaka']['data'][start:end]
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
    vol_class[start:end] = classification
    vol_mask[start:end] = ~valid_mask

# ==== 放入雷達欄位 ====
masked_class = np.ma.masked_array(vol_class, mask=vol_mask)
radar.add_field('hydro_class', {
    'data': masked_class,
    'units': 'category',
    'long_name': 'hydrometeor_type',
    'standard_name': 'hydrometeor_type',
    'valid_min': 0,
    'valid_max': 5
}, replace_existing=True)

# ==== 做 gridding ====
grid = pyart.map.grid_from_radars(
    radar,
    grid_shape=(41, 201, 201),
    grid_limits=((0, 20000), (-100000, 100000), (-100000, 100000)),
    fields=['hydro_class']
)

# ==== 剖面座標計算 ====
geod = Geod(ellps='WGS84')
az12, _, dist = geod.inv(lon0, lat0, lon1, lat1)
npoints = 300
distances = np.linspace(0, dist, npoints)
lons, lats, _ = geod.fwd(
    np.full(npoints, lon0),
    np.full(npoints, lat0),
    np.full(npoints, az12),
    distances
)

# ==== 投影成 radar-centered coords ====
radar_lon = radar.longitude['data'][0]
radar_lat = radar.latitude['data'][0]
azs, _, dists = geod.inv(np.full(npoints, radar_lon), np.full(npoints, radar_lat), lons, lats)
x = dists * np.sin(np.radians(azs)) / 1000
y = dists * np.cos(np.radians(azs)) / 1000

# ==== 對應網格值 ====
gx = grid.x['data'] / 1000
gy = grid.y['data'] / 1000
gz = grid.z['data'] / 1000
hydro = grid.fields['hydro_class']['data']

cross_section = np.full((len(gz), len(x)), np.nan, dtype=float)
for i, (px, py) in enumerate(zip(x, y)):
    ix = np.argmin(np.abs(gx - px))
    iy = np.argmin(np.abs(gy - py))
    column = hydro[:, iy, ix]
    if np.ma.is_masked(column):
        column = column.astype(float).filled(np.nan)
    cross_section[:, i] = column

# ==== 畫圖 ====
fig, ax = plt.subplots(figsize=(12, 6))
cmap = plt.cm.get_cmap("tab10", 6)
zz, xx = np.meshgrid(gz, np.linspace(0, dist / 1000, len(x)), indexing='ij')
masked_cross_section = np.ma.masked_invalid(cross_section)

pc = ax.pcolormesh(xx, zz, masked_cross_section, cmap=cmap, vmin=0, vmax=5)
ax.set_xlabel("距離 (km)")
ax.set_ylabel("高度 (km)")
ax.set_title(f"Hydrometeor Cross-Section (Nearest Grid)\n{time_dt}")

label_names = ['Rain', 'Melting Layer', 'Wet Snow', 'Dry Snow', 'Graupel', 'Hail']
patches = [mpatches.Patch(color=cmap(i), label=label_names[i]) for i in range(6)]
ax.legend(handles=patches, loc='upper right', title='Hydrometeors')
plt.colorbar(pc, ax=ax, label='Hydrometeor Type')
plt.tight_layout()
plt.show()
