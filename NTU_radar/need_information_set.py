#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## 將 RCNTU .nc 轉為扁平 CSV，並根據 Park et al. (2009) 分類法（移除 rhohv 條件、無等號）分類
## 欄位：lon, lat, hight(=dist*tan(theta)), Zhh, Zdr, rho, phi, Kdp, hydrometeor_type

from netCDF4 import Dataset
import numpy as np
import pandas as pd
import os
from glob import glob
import hydrometeor_class as PID  # 分類函式

PID_class_chouse = 'dolan' 

## --- 設定區 ---
# 台大雷達站座標 (NTU Main Campus)
NTU_LON = 121.5397
NTU_LAT = 25.0174

vol_folder_path = f"/home/steven/python_data/NTU_radar/data/RCNTU_20210530_31_rhi/RCNTU_data/raw_by_date/20210530/"  ##資料來源 每次都不一樣
save_path = "/home/steven/python_data/NTU_radar/need_data/20210530"

vol_files = sorted(glob(os.path.join(vol_folder_path, "*.nc")))

os.makedirs(save_path, exist_ok=True)

def _to_ndarray_with_nan(data_any):  # 將 masked array → ndarray 並以 NaN 補
    return np.ma.filled(data_any, np.nan) if np.ma.isMaskedArray(data_any) else np.asarray(data_any)

def calculate_haversine_distance(lon1, lat1, lon2, lat2):
    """
    計算兩點經緯度之間的地表距離 (Haversine formula)
    Input: lon1, lat1 (雷達站); lon2, lat2 (資料點, 可為陣列)
    Output: 距離 (公尺)
    """
    R = 6371000.0  # 地球平均半徑 (公尺)
    
    # 將角度轉為弧度
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    
    # Haversine 公式
    a = np.sin(delta_phi / 2.0)**2 + \
        np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    distance_m = R * c
    return distance_m

## --- 主程式 ---

for nc_path_str in vol_files:
    print(nc_path_str)
    try:
        base_name = os.path.basename(nc_path_str)
        time = base_name.split(".")[0][5:]
        print(f"處理檔案： {nc_path_str}")
        print(f"時間字串： {time}")

        ## 讀檔
        ds = Dataset(nc_path_str, "r")

        ## 幾何 (仰角)
        theta_deg_ray_1d = _to_ndarray_with_nan(ds["theta"][:])
        
        ## 經緯度 (2D array)
        lon_data_2d = _to_ndarray_with_nan(ds["lon"][:])
        lat_data_2d = _to_ndarray_with_nan(ds["lat"][:])

        ## 物理量
        Zhh_data_2d = _to_ndarray_with_nan(ds["Zhh"][:])
        Zdr_data_2d = _to_ndarray_with_nan(ds["zdr"][:])
        rho_data_2d = _to_ndarray_with_nan(ds["rho"][:])
        phi_data_2d = _to_ndarray_with_nan(ds["phi"][:])
        KDP_data_2d = _to_ndarray_with_nan(ds["KDP"][:])
        
        ## --- 高度計算修改 ---
        dist_m_2d = calculate_haversine_distance(NTU_LON, NTU_LAT, lon_data_2d, lat_data_2d)
        theta_fixed = np.array(theta_deg_ray_1d)
        theta_fixed = np.where(theta_fixed > 90, 180 - theta_fixed, theta_fixed)
        theta_rad_ray_1d = np.deg2rad(theta_fixed)
        hight_m_2d = dist_m_2d * np.tan(theta_rad_ray_1d)[:, None]

        ## ---- X-band HID
        z_valid   = Zhh_data_2d
        zdr_valid = Zdr_data_2d
        kdp_valid = KDP_data_2d
        rho_valid = rho_data_2d

        if PID_class_chouse == 'dolan':
            label = PID.pid_method_dolan_2009(z_valid, zdr_valid, kdp_valid, rho_valid, T=0)
            # 【修正標註】：處理回傳值為 tuple 的情況，取第一個元素作為標籤陣列
            if isinstance(label, tuple):
                label = label[0]

        ## 展平成一維
        lon_flat   = lon_data_2d.ravel()
        lat_flat   = lat_data_2d.ravel()
        hight_flat = hight_m_2d.ravel()
        Zhh_flat   = Zhh_data_2d.ravel()
        Zdr_flat   = Zdr_data_2d.ravel()
        rho_flat   = rho_data_2d.ravel()
        phi_flat   = phi_data_2d.ravel()
        Kdp_flat   = KDP_data_2d.ravel()
        label_flat = label.ravel()

        ## 組 DataFrame
        csv_df = pd.DataFrame({
            "lon":   lon_flat,
            "lat":   lat_flat,
            "hight": hight_flat,
            "Zhh":   Zhh_flat,
            "Zdr":   Zdr_flat,
            "rho":   rho_flat,
            "phi":   phi_flat,
            "Kdp":   Kdp_flat,
            "hydrometeor_type": label_flat,
        })

        ## 輸出
        csv_path_str = f"{save_path}/{time}.csv"
        csv_df.to_csv(csv_path_str, index=False, float_format="%.6f")
        print(f"✅ Done. CSV 儲存到： {csv_path_str}")
        print(f"   總列數：{len(csv_df):,}（= ray × gate）")

    except Exception as e:
        print(f"❌ 處理檔案 {nc_path_str} 時發生錯誤： {e}")