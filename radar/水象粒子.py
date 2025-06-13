import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime
from pyart.retrieve import kdp_maesaka
import matplotlib.patches as mpatches


# ==== 路徑與時間設定 ====
data_top_path = "C:/Users/steve/python_data/radar"
year, month, day = '2024', '05', '23'
hh, mm, ss = '00', '02', '00'
file_path = f"{data_top_path}/{year}{month}{day}_u.RCWF/{year}{month}{day}{hh}{mm}{ss}.VOL"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
sweep_num = 2

# ==== 中文設定 ====
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False


# ==== 讀取雷達資料 ====
radar = pyart.io.read(file_path)
time_str = file_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

# ==== 計算 KDP ====
print("⚙️ 正在計算 KDP（Maesaka 方法），請稍候...")
kdp_dict, _, _ = kdp_maesaka(radar)
radar.add_field('kdp_maesaka', kdp_dict)

# ==== 建立全 sweeps 水象粒子型態陣列 ====
n_rays, n_bins = radar.fields['reflectivity']['data'].shape
vol_class = np.full((n_rays, n_bins), -1, dtype=int)
vol_mask = np.ones((n_rays, n_bins), dtype=bool)  # 預設全部是 masked（True）

# ==== 逐 sweep 處理分類 ====
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

    classification = np.full(z.shape, -1, dtype=int)

    # 只根據 mask 判斷哪些資料是有效的
    z_mask = np.ma.getmaskarray(z)
    zdr_mask = np.ma.getmaskarray(zdr)
    rhohv_mask = np.ma.getmaskarray(rhohv)
    kdp_mask = np.ma.getmaskarray(kdp)

    valid_mask = ~(z_mask | zdr_mask | rhohv_mask | kdp_mask)

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
    vol_mask[start_idx:end_idx, :] = ~valid_mask  # 有資料的地方設為 False，不 mask

# ==== 加入 radar 欄位 ====
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

# ==== 畫圖（sweep 0）====

display = pyart.graph.RadarMapDisplay(radar)
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

cmap = plt.cm.get_cmap("tab10", 6)
display.plot_ppi_map(
    'hydro_class',
    sweep=sweep_num,
    ax=ax,
    vmin=0,
    vmax=5,
    cmap=cmap,
    colorbar_flag=False,
    title=f"水象粒子分佈\n{time_dt}",
    shapefile=shapefile_path,
    shapefile_kwargs={"facecolor": 'none', 'edgecolor': 'r'},
    embellish=False
)
ax.set_extent([119, 123.5, 21, 26.5])
gl = ax.gridlines(draw_labels=True)
gl.right_labels = False

# ==== 加 legend ====
label_names = ['Rain', 'Melting Layer', 'Wet Snow', 'Dry Snow', 'Graupel', 'Hail']
patches = [mpatches.Patch(color=cmap(i), label=label_names[i]) for i in range(6)]
plt.legend(handles=patches, loc='lower left', fontsize=10, title='Hydrometeors')

plt.tight_layout()
plt.show()
