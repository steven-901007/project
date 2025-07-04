import pyart
import numpy as np
from datetime import datetime
from pyart.retrieve import kdp_maesaka
import os
from glob import glob
import pandas as pd

# ==== 路徑與時間設定 ====
data_top_path = "C:/Users/steve/python_data/radar"
# data_top_path = "home/steven/python_data/radar"

one_day_or_not = True  # True = 一次處理一天 False = 一次處理一個時間點
target_date = "20240523"  #一次處理一天用這個
single_vol_file_name = "20210523000200.VOL" #一次處理一筆資料用這個

if one_day_or_not == False:
    target_date = single_vol_file_name[:8]
vol_folder_path = f"{data_top_path}/{target_date}_u.RCWF"
output_folder = f"{data_top_path}/PID/{target_date}"
stats_folder = f"{output_folder}/stats"
os.makedirs(output_folder, exist_ok=True)
os.makedirs(stats_folder, exist_ok=True)

# ==== 取得要處理的檔案清單 ====
if one_day_or_not:
    vol_files = sorted(glob(os.path.join(vol_folder_path, "*.VOL")))
else:

    vol_files = [os.path.join(vol_folder_path, single_vol_file_name)]

# ==== 處理每一個 VOL 檔 ====
for vol_path in vol_files:
    try:
        print(f"📂 處理檔案：{os.path.basename(vol_path)}")
        radar = pyart.io.read(vol_path)
        time_str = os.path.basename(vol_path).split(".")[0]
        output_path = f"{output_folder}/{time_str}.nc"
        stats_csv_path = f"{stats_folder}/{time_str}_stats.csv"

        # ==== 計算 KDP（Maesaka 方法） ====
        print("⚙️ 計算 KDP（Maesaka 方法）...")
        kdp_dict, _, _ = kdp_maesaka(radar)
        radar.add_field('kdp_maesaka', kdp_dict, replace_existing=True)

        # ==== 建立分類陣列 ====
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

            valid_mask = ~(
                np.ma.getmaskarray(z) |
                np.ma.getmaskarray(zdr) |
                np.ma.getmaskarray(rhohv) |
                np.ma.getmaskarray(kdp)
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
            vol_class[start_idx:end_idx, :] = classification
            vol_mask[start_idx:end_idx, :] = ~valid_mask

        masked_class = np.ma.masked_array(vol_class, mask=vol_mask)
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

        # ==== 統計分類像素 ====
        hydro_data = radar.fields['hydro_class']['data'].filled(-1)
        unique, counts = np.unique(hydro_data, return_counts=True)
        label_map = {
            -1: 'Unknown',
            0: 'Rain',
            1: 'Melting Layer',
            2: 'Wet Snow',
            3: 'Dry Snow',
            4: 'Graupel',
            5: 'Hail'
        }

        stats_dict = {
            'class_code': [],
            'class_name': [],
            'pixel_count': []
        }
        for code, count in zip(unique, counts):
            name = label_map.get(code, f"Unknown ({code})")
            print(f"{name:<15}: {count}")
            stats_dict['class_code'].append(code)
            stats_dict['class_name'].append(name)
            stats_dict['pixel_count'].append(count)

        stats_df = pd.DataFrame(stats_dict)
        stats_df.to_csv(stats_csv_path, index=False)

        # 儲存 NetCDF
        pyart.io.write_cfradial(output_path, radar)
        print(f"✅ 已儲存至：{output_path}")
        print(f"📄 統計 CSV 已儲存至：{stats_csv_path}\n")

    except Exception as e:
        print(f"❌ 發生錯誤：{e}\n")
