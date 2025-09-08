import pyart
import numpy as np
from datetime import datetime
from pyart.retrieve import kdp_maesaka
import os
from glob import glob
import pandas as pd
import sys



## ==== 使用者參數設定 ==== ##
year = sys.argv[1] if len(sys.argv) > 1 else '2021'
month = sys.argv[2] if len(sys.argv) > 2 else '05'
day = sys.argv[3] if len(sys.argv) > 3 else '30'
mode = sys.argv[4] if len(sys.argv) > 4 else 'all'  # 'one' or 'all'
pid = sys.argv[5] if len(sys.argv) > 5 else 'park' #park or way(魏) 使用哪個PID
station = sys.argv[6] if len(sys.argv) > 1 else 'RCWF'



target_date = f"{year}{month}{day}"

import platform
## ==== 系統路徑設定 ==== ##
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/radar"
else:
    data_top_path = "/home/steven/python_data/radar"

vol_folder_path = f"{data_top_path}/data/{target_date}_u.{station}"
output_folder = f"{data_top_path}/PID/{target_date}_{station}_{pid}"
stats_folder = f"{output_folder}/stats"
os.makedirs(output_folder, exist_ok=True)
os.makedirs(stats_folder, exist_ok=True)

## ==== 取得處理檔案清單 ==== ##
if mode == 'all':
    vol_files = sorted(glob(os.path.join(vol_folder_path, "*.VOL")))
else:
    hh = sys.argv[7] if len(sys.argv) > 6 else '00'
    mm = sys.argv[8] if len(sys.argv) > 7 else '04'
    ss = sys.argv[9] if len(sys.argv) > 8 else '00'
    single_vol_file = f"{target_date}{hh}{mm}{ss}.VOL"
    vol_files = [os.path.join(vol_folder_path, single_vol_file)]
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
            if pid == 'park':
                ## ==== Prak 等 (2009) 分類法 ==== ##
                # KDP to LKDP
                lkdp_valid = 10 * np.log10(kdp_valid)

                # 計算函數值
                f1 = -0.5 + 2.5e-3 * z_valid + 7.5e-4 * z_valid**2
                f2 = 0.68 - 4.81e-2 * z_valid + 2.92e-3 * z_valid**2
                f3 = 1.42 + 6.67e-2 * z_valid + 4.85e-4 * z_valid**2
                g1 = -44 + 0.8 * z_valid
                g2 = -22 + 0.5 * z_valid

                # Rain (label 0)
                label[(z_valid >= 10) & (z_valid <= 45) &
                    (zdr_valid >= f1) & (zdr_valid <= f2) &
                    (rhohv_valid > 0.97) &
                    (lkdp_valid >= g1) & (lkdp_valid <= g2)] = 0

                # Melting Layer (label 1)
                label[(z_valid >= 25) & (z_valid <= 45) &
                    (zdr_valid >= f2) & (zdr_valid <= f3) &
                    (rhohv_valid > 0.95) &
                    (lkdp_valid >= g1) & (lkdp_valid <= g2)] = 1

                # Wet Snow (label 2)
                label[(z_valid >= 30) & (z_valid <= 40) &
                    (zdr_valid >= 1.0) & (zdr_valid <= 2.0) &
                    (rhohv_valid >= 0.92) & (rhohv_valid <= 0.95) &
                    (lkdp_valid >= -25) & (lkdp_valid <= 10)] = 2

                # Dry Snow (label 3)
                label[(z_valid >= 10) & (z_valid <= 35) &
                    (zdr_valid >= 0.0) & (zdr_valid <= 0.3) &
                    (rhohv_valid > 0.98) &
                    (lkdp_valid >= -25) & (lkdp_valid <= 10)] = 3

                # Graupel (label 4)
                label[(z_valid >= 35) & (z_valid <= 50) &
                    (zdr_valid >= 0.0) & (zdr_valid <= f1) &
                    (rhohv_valid > 0.97) &
                    (lkdp_valid >= -25) & (lkdp_valid <= 10)] = 4

                # Hail (label 5)
                label[(z_valid >= 50) & (z_valid <= 75) &
                    (zdr_valid >= f1) & (zdr_valid <= f2) &
                    (rhohv_valid > 0.95) &
                    (lkdp_valid >= g1) & (lkdp_valid <= g2)] = 5
            elif pid == 'way':
                label[(z_valid >= 5) & (z_valid <= 25) &
                    (zdr_valid >= 0.2) & (zdr_valid <= 0.7) &
                    (kdp_valid >= 0) & (kdp_valid <= 0.06) &
                    (rhohv_valid >= 0.98) & (rhohv_valid <= 0.99)] = 0  # Drizzle 毛雨

                label[(z_valid >= 25) & (z_valid <= 60) &
                    (zdr_valid >= 0.5) & (zdr_valid <= 4.0) &
                    (kdp_valid >= 1) & (kdp_valid <= 7) &
                    (rhohv_valid >= 0.98) & (rhohv_valid <= 0.99)] = 1  # Rain 雨

                label[(z_valid >= -10) & (z_valid <= 20) &
                    (zdr_valid >= -0.5) & (zdr_valid <= 0.5) &
                    (kdp_valid >= -1) & (kdp_valid <= 1) &
                    (rhohv_valid >= 0.97) & (rhohv_valid <= 0.99)] = 2  # Weak Snow 弱乾雪

                label[(z_valid >= -10) & (z_valid <= 30) &
                    (zdr_valid >= 0) & (zdr_valid <= 1) &
                    (kdp_valid >= 0) & (kdp_valid <= 0.4) &
                    (rhohv_valid >= 0.97) & (rhohv_valid <= 0.99)] = 3  # Strong Snow 強乾雪

                label[(z_valid >= 30) & (z_valid <= 40) &
                    (zdr_valid >= 0.5) & (zdr_valid <= 3.0) &
                    (kdp_valid >= 0) & (kdp_valid <= 2) &
                    (rhohv_valid >= 0.85) & (rhohv_valid <= 0.95)] = 4  # Wet Snow 濕雪

                label[(z_valid >= 25) & (z_valid <= 35) &
                    (zdr_valid >= -0.5) & (zdr_valid <= 1.0) &
                    (kdp_valid >= 0.7) & (kdp_valid <= 1.5) &
                    (rhohv_valid >= 0.94) & (rhohv_valid <= 0.98)] = 5  # Dry Graupel 乾軟雹

                label[(z_valid >= 45) & (z_valid <= 55) &
                    (zdr_valid >= 1.5) & (zdr_valid <= 4.5) &
                    (kdp_valid >= 2) & (kdp_valid <= 4) &
                    (rhohv_valid >= 0.85) & (rhohv_valid <= 0.95)] = 6  # Wet Graupel 濕軟雹

                label[(z_valid >= 50) & (z_valid <= 60) &
                    (zdr_valid >= -0.5) & (zdr_valid <= 0.5) &
                    (kdp_valid >= -1) & (kdp_valid <= 1) &
                    (rhohv_valid >= 0.92) & (rhohv_valid <= 0.96)] = 7  # Small Hail 小冰雹

                label[(z_valid >= 55) & (z_valid <= 65) &
                    (zdr_valid >= -1) & (zdr_valid <= 0.5) &
                    (kdp_valid >= -1) & (kdp_valid <= 2) &
                    (rhohv_valid >= 0.90) & (rhohv_valid <= 0.92)] = 8  # Large Hail 大冰雹

                label[(z_valid >= 55) & (z_valid <= 75) &
                    (zdr_valid >= 1) & (zdr_valid <= 6) &
                    (kdp_valid >= 3) & (kdp_valid <= 5) &
                    (rhohv_valid >= 0.80) & (rhohv_valid <= 0.95)] = 9  # Rain-Hail Mixture 雨雹共存

                label[(z_valid >= -20) & (z_valid <= 20) &
                    (zdr_valid >= -0.5) & (zdr_valid <= 1.5) &
                    (kdp_valid >= 0) & (kdp_valid <= 0.1) &
                    (rhohv_valid >= 0.98)] = 10  # Suppercooled water 過冷水
            
            classification[valid_mask] = label
            vol_class[start_idx:end_idx, :] = classification
            vol_mask[start_idx:end_idx, :] = ~valid_mask

        masked_class = np.ma.masked_array(vol_class, mask=vol_mask)
        if pid == 'park':
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
            label_map = {
                -1: 'Unknown',
                0: 'Rain',
                1: 'Melting Layer',
                2: 'Wet Snow',
                3: 'Dry Snow',
                4: 'Graupel',
                5: 'Hail'
            }
        elif pid == 'way':
            class_field = {
                'data': masked_class,
                'units': 'category',
                'long_name': 'hydrometeor_type',
                'standard_name': 'hydrometeor_type',
                'valid_min': 0,
                'valid_max': 10,
                '_FillValue': -999,
                'missing_value': -999
            }   
            label_map = {
                -1: 'Unknown',
                0: 'Drizzle',
                1: 'Rain',
                2: 'Weak Snow',
                3: 'Strong Snow',
                4: 'Wet Snow',
                5: 'Dry Graupel',
                6: 'Wet Graupel',
                7: 'Small Hail',
                8: 'Large Hail',
                9: 'Rain-Hail Mixture',
                10: 'Suppercooled water',
            }
         
        radar.add_field('hydro_class', class_field, replace_existing=True)

        # ==== 統計分類像素 ====
        hydro_data = radar.fields['hydro_class']['data'].filled(-1)
        unique, counts = np.unique(hydro_data, return_counts=True)

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
