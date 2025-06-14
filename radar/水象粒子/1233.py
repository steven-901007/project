import pyart
import numpy as np
from datetime import datetime
from pyart.retrieve import kdp_maesaka
import os

# ==== 時間與路徑設定 ====
data_top_path = "C:/Users/steve/python_data/radar"
year, month, day = '2024', '05', '23'
hh, mm, ss = '00', '02', '00'
time_str = f"{year}{month}{day}{hh}{mm}{ss}"

# ==== 檔案路徑 ====
vol_path = f"{data_top_path}/{year}{month}{day}_u.RCWF/{time_str}.VOL"
output_path = f"{data_top_path}/PID/{time_str}.nc"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# ==== 讀取 VOL 資料 ====
radar = pyart.io.read(vol_path)

# ==== 原始欄位處理（Z, ZDR, RhoHV）====
base_fields = ['reflectivity', 'differential_reflectivity', 'cross_correlation_ratio']
for field in base_fields:
    if field in radar.fields:
        data = radar.fields[field]['data']
        data_filled = np.ma.filled(data, fill_value=-999)
        radar.fields[field]['data'] = np.ma.masked_equal(data_filled, -999)
        radar.fields[field]['_FillValue'] = -999
        radar.fields[field]['missing_value'] = -999

# ==== 計算 KDP（Maesaka 方法）====
print("⚙️ 正在計算 KDP（Maesaka 方法）...")
kdp_dict, _, _ = kdp_maesaka(radar)
kdp = kdp_dict['data']
kdp_filled = np.ma.filled(kdp, fill_value=-999)
kdp_masked = np.ma.masked_equal(kdp_filled, -999)
kdp_dict['data'] = kdp_masked
kdp_dict['_FillValue'] = -999
kdp_dict['missing_value'] = -999
kdp_dict['long_name'] = 'specific_differential_phase_maesaka'
kdp_dict['units'] = 'degree/km'
radar.add_field('kdp_maesaka', kdp_dict, replace_existing=True)

# ==== 水象粒子分類 hydro_class ====
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
    gate_dists = radar.range['data']
    gate_dists_2d = np.broadcast_to(gate_dists, z.shape)

    valid_mask = (
        ~(z_mask | zdr_mask | rhohv_mask | kdp_mask) &
        (gate_dists_2d > 5000) &
        (z > 0) & (z < 60) &
        (rhohv > 0.85)
    )

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

    classification[valid_mask] = label
    classification[~valid_mask] = -999  # 強制無效區為 -999
    vol_class[start_idx:end_idx, :] = classification
    vol_mask[start_idx:end_idx, :] = (classification == -999)

masked_class = np.ma.masked_equal(vol_class, -999)
class_field = {
    'data': masked_class,
    'units': 'category',
    'long_name': 'hydrometeor_type',
    'standard_name': 'hydrometeor_type',
    'valid_min': 0,
    'valid_max': 5,
    '_FillValue': -999,
    'missing_value': -999
}
radar.add_field('hydro_class', class_field, replace_existing=True)

# ==== 移除其他不需要的欄位 ====
fields_to_keep = ['reflectivity', 'differential_reflectivity', 'cross_correlation_ratio', 'kdp_maesaka', 'hydro_class']
for field in list(radar.fields.keys()):
    if field not in fields_to_keep:
        del radar.fields[field]

# ==== 輸出為 NetCDF（CFRadial 格式） ====
pyart.io.write_cfradial(output_path, radar)
print(f"✅ 儲存成功：{output_path}")
