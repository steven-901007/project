import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime
from cartopy.io.shapereader import Reader
from pyart.graph import GridMapDisplay

# ==== 時間與路徑設定 ====
data_top_path = "C:/Users/steve/python_data/radar"
year, month, day = '2024', '05', '23'
hh, mm, ss = '00', '02', '00'
time_str = f"{year}{month}{day}{hh}{mm}{ss}"
file_path = f"{data_top_path}/PID/{time_str}.nc"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

# ==== 中文顯示設定 ====
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# ==== 讀取雷達資料 ====
radar = pyart.io.read(file_path)
time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

# ==== 水象粒子分類（分類欄位：hydro_class）====
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
        continue  # 如果有缺欄位就跳過

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
    label[(z_valid >= 20) & (z_valid <= 45) & (zdr_valid >= 0.5) & (zdr_valid <= 2.5) & (rhohv_valid > 0.97) & (kdp_valid > 0.5)] = 0  # Rain
    label[(z_valid >= 25) & (z_valid <= 40) & (zdr_valid > 1) & (rhohv_valid >= 0.90) & (rhohv_valid <= 0.96)] = 1  # Melting Layer
    label[(z_valid >= 15) & (z_valid <= 35) & (zdr_valid >= 0.5) & (zdr_valid <= 1.5) & (rhohv_valid >= 0.90) & (rhohv_valid <= 0.96)] = 2  # Wet Snow
    label[(z_valid >= 10) & (z_valid <= 30) & (zdr_valid >= 0.0) & (zdr_valid <= 0.5) & (rhohv_valid > 0.97)] = 3  # Dry Snow
    label[(z_valid >= 30) & (z_valid <= 45) & (zdr_valid >= 0.0) & (zdr_valid <= 0.3) & (rhohv_valid >= 0.85) & (rhohv_valid <= 0.95)] = 4  # Graupel
    label[(z_valid >= 50) & (zdr_valid >= -1.0) & (zdr_valid <= 1.0) & (rhohv_valid < 0.90)] = 5  # Hail
    classification[~valid_mask] = -1  # 強制不合法的區域為 -1，不進行分類

    classification[valid_mask] = label
    vol_class[start_idx:end_idx, :] = classification
    vol_mask[start_idx:end_idx, :] = ~valid_mask

# 放入 radar field
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

# ==== 製作 Grid（用分類資料）====
grid = pyart.map.grid_from_radars(
    radar,
    grid_shape=(41, 400, 400),
    grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
    fields=['hydro_class'],
    weighting_function='nearest',
    gridding_algo='map_gates_to_grid'
)

# ==== 抽出 z 層 ====
z_target = 4000  # 公尺
z_levels = grid.z['data']
z_index = np.abs(z_levels - z_target).argmin()
print(f"選擇切層 z_index={z_index}, 對應高度為 {z_levels[z_index]} m")

# ==== 畫水象粒子 CAPPI ====
display = GridMapDisplay(grid)
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

# 顏色設定：tab10 有 10 種離散色適合類別圖
cmap = plt.cm.get_cmap("tab10", 6)

display.plot_grid(
    field='hydro_class',
    level=z_index,
    ax=ax,
    cmap=cmap,
    vmin=0,
    vmax=5,
    title=f"CAPPI 水象粒子分類 @ {z_levels[z_index]/1000:.1f} km\n{time_dt}",
    colorbar_label='Hydrometeor Type',
    embellish=False
)

# 疊加縣市界
shp = Reader(shapefile_path)
ax.add_geometries(
    shp.geometries(),
    crs=ccrs.PlateCarree(),
    facecolor='none',
    edgecolor='red'
)

# 顯示範圍
center_lon = radar.longitude['data'][0]
center_lat = radar.latitude['data'][0]
ax.set_extent([center_lon - 1.5, center_lon + 1.5, center_lat - 1.5, center_lat + 1.5])

# 加圖例
import matplotlib.patches as mpatches
label_names = ['Rain', 'Melting Layer', 'Wet Snow', 'Dry Snow', 'Graupel', 'Hail']
patches = [mpatches.Patch(color=cmap(i), label=label_names[i]) for i in range(6)]
plt.legend(handles=patches, loc='lower left', fontsize=10, title='Hydrometeors')

plt.tight_layout()
plt.show()
