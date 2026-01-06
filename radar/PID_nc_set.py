import pyart
import numpy as np
from scipy.ndimage import uniform_filter1d
import pandas as pd  # 用於處理 NaN 插值
import os
from glob import glob
import sys
import time
import pid_library 


## ==== 使用者參數設定 ==== ##
year = sys.argv[1] if len(sys.argv) > 1 else '2021'
month = sys.argv[2] if len(sys.argv) > 2 else '05'
day = sys.argv[3] if len(sys.argv) > 3 else '24'
mode = sys.argv[4] if len(sys.argv) > 4 else 'all'  # 'one' or 'all'
pid_arg = sys.argv[5] if len(sys.argv) > 5 else 'park' # 'park' or 'way'
station = sys.argv[6] if len(sys.argv) > 6 else 'RCWF'

target_date = f"{year}{month}{day}"

data_top_path = "/home/steven/python_data/radar"
vol_folder_path = f"{data_top_path}/data/{target_date}_u.{station}"
output_folder = f"{data_top_path}/PID/{target_date}_{station}_{pid_arg}"
stats_folder = f"{output_folder}/stats"
os.makedirs(output_folder, exist_ok=True)
os.makedirs(stats_folder, exist_ok=True)

## ==== 取得處理檔案清單 ==== ##
if mode == 'all':
    vol_files = sorted(glob(os.path.join(vol_folder_path, "*.VOL")))
else:
    hh = sys.argv[7] if len(sys.argv) > 6 else '04'
    mm = sys.argv[8] if len(sys.argv) > 7 else '37'
    ss = sys.argv[9] if len(sys.argv) > 8 else '00'
    single_vol_file = f"{target_date}{hh}{mm}{ss}.VOL"
    vol_files = [os.path.join(vol_folder_path, single_vol_file)]

## ==== 自定義 KDP 計算函式 (Jou et al. 2015) ==== ##
def calculate_kdp_jou(radar, phidp_field='differential_phase', 
                      ref_field='reflectivity', rhohv_field='cross_correlation_ratio'):
    """
    根據 Jou et al. (2015) 針對 RCWF S-band 雷達的方法計算 Kdp。
    方法：對 PhiDP 進行 3 次 25 點窗口的迭代勻滑，再進行距離微分。
    """
    # 1. 檢查必要欄位是否存在
    if phidp_field not in radar.fields:
        print(f"⚠️ 找不到 {phidp_field}，跳過 KDP 計算。")
        return None

    # 取得雷達資料
    # 注意：這裡假設輸入的 PhiDP 已經經過解摺疊 (Unfolded) 處理
    phidp = radar.fields[phidp_field]['data'].copy()
    
    # [修正] 處理 Masked Array 與 NaN
    # 直接填 NaN 會導致 uniform_filter1d 輸出整片 NaN (擴散效應)
    # 因此我們將 Masked Array 轉為一般 Array，並對 NaN 進行線性插值
    if np.ma.is_masked(phidp):
        phidp = phidp.filled(np.nan)
    
    # 使用 Pandas 對每一條徑向(Ray)進行線性插值以填補缺漏，避免平滑時數據遺失
    # 若資料量極大，這步會稍慢，但比 NaN 擴散更安全
    # axis=1 是 Range，我們希望沿著 Range 插值
    df_phidp = pd.DataFrame(phidp)
    # limit_direction='both' 確保頭尾的 NaN 也能被最近值填補
    phidp_interpolated = df_phidp.interpolate(method='linear', axis=1, limit_direction='both').values
    
    # 若插值後仍有 NaN (例如整條 ray 都是空的)，則填 0 防止報錯
    phidp_interpolated = np.nan_to_num(phidp_interpolated, nan=0.0)

    # 2. 執行 3 次 25 點窗口勻滑 (Iterative Smoothing) 
    window_size = 25
    iterations = 3
    
    smoothed_phidp = phidp_interpolated.copy()
    
    # 沿著雷達徑向 (axis=1) 進行平滑
    for i in range(iterations):
        # mode='nearest' 對邊界處理較好，避免邊緣數值驟降
        smoothed_phidp = uniform_filter1d(smoothed_phidp, size=window_size, axis=1, mode='nearest')

    # 3. 距離微分 (Range Differentiation)
    # Kdp = 0.5 * d(PhiDP) / dr
    
    # 取得徑向解析度 (公尺 轉 公里)
    dr_meters = radar.range['data'][1] - radar.range['data'][0]
    dr_km = dr_meters / 1000.0
    
    # 使用 numpy gradient 計算斜率 (中央差分)
    # axis=1 是 Range 方向
    d_phidp_dr = np.gradient(smoothed_phidp, axis=1)
    
    # 計算 Kdp (單位: deg/km)
    kdp_data = d_phidp_dr / (2.0 * dr_km)

    # 4. 品質控制與濾波 (Quality Control) 
    # 建立遮罩：濾除 Rhv < 0.95 或 Ref < 10 dBZ 的雜訊
    mask = np.zeros_like(kdp_data, dtype=bool)
    
    if rhohv_field in radar.fields:
        rhohv = radar.fields[rhohv_field]['data']
        # 處理 rhohv 可能也是 masked array 的情況
        if np.ma.is_masked(rhohv):
             rhohv = rhohv.filled(0)
        mask |= (rhohv < 0.95)
    
    if ref_field in radar.fields:
        ref = radar.fields[ref_field]['data']
        if np.ma.is_masked(ref):
             ref = ref.filled(-999)
        mask |= (ref < 10.0)

    # 將符合遮罩條件的區域設為 0 或 NaN (論文建議去除雜訊)
    kdp_data[mask] = 0.0
    
    # 將負值設為 0 (物理上降雨造成的 Kdp 應為正值) 
    kdp_data[kdp_data < 0] = 0.0

    # 建立 Py-ART 欄位字典
    kdp_dict = {
        'data': np.ma.masked_where(mask, kdp_data),
        'units': 'degrees/km',
        'long_name': 'Specific differential phase (Jou et al. 2015)',
        'standard_name': 'specific_differential_phase_hv',
        'valid_min': 0.0,
        'coordinates': 'elevation azimuth range'
    }
    
    return kdp_dict




# ==== 處理每一個 VOL 檔 ====
for vol_path in vol_files:
    try:
        time_start = time.time()
        print(f"📂 處理檔案：{os.path.basename(vol_path)}")
        radar = pyart.io.read(vol_path)
        time_str = os.path.basename(vol_path).split(".")[0]
        output_path = f"{output_folder}/{time_str}.nc"
        stats_csv_path = f"{stats_folder}/{time_str}_stats.csv" 

        # ==== 計算 KDP（Jou et al. 2015 方法） ====
        # 檢查是否已存在，若無則計算
        # 這裡的欄位名稱 'kdp_jou' 可依需求修改
        if 'kdp_jou' not in radar.fields:
            print("⚙️ 計算 KDP（Jou et al. 2015 / 3-iter Smoothing）...")
            
            kdp_dict = calculate_kdp_jou(
                radar, 
                phidp_field='differential_phase', # 請確認 Py-ART 讀取後的欄位名稱正確
                ref_field='reflectivity',         
                rhohv_field='cross_correlation_ratio' 
            )
            
            if kdp_dict is not None:
                radar.add_field('kdp_jou', kdp_dict, replace_existing=True)
                print("✅ KDP 計算完成")
            else:
                print("❌ KDP 計算失敗 (缺少必要欄位)")

        time_kdp_end = time.time()
        print(f"⏱️ KDP 計算時間: {time_kdp_end - time_start:.2f} 秒")
        
        # ==== 準備全體積容器 (Full Volume Arrays) ====
        # 提取數據並處理 Masked Array (填入 NaN 以利計算)
        Z = radar.fields['reflectivity']['data']
        Zdr = radar.fields['differential_reflectivity']['data']
        rhohv = radar.fields['cross_correlation_ratio']['data']
        
        # [修正] 這裡是關鍵錯誤，必須讀取剛剛算好的 'kdp_jou'
        if 'kdp_jou' in radar.fields:
            Kdp = radar.fields['kdp_jou']['data'] 
        else:
            print("⚠️ 警告：找不到 kdp_jou，PID 可能會失敗或使用全 NaN")
            Kdp = np.full_like(Z, np.nan)

        # 轉成一般 numpy array，無效值填 NaN (pid_library 會處理 NaN -> 0分)
        Z_filled = np.ma.filled(Z, np.nan)
        Zdr_filled = np.ma.filled(Zdr, np.nan)
        rhohv_filled = np.ma.filled(rhohv, np.nan)
        Kdp_filled = np.ma.filled(Kdp, np.nan)

        print(f"🧠 執行 PID 模糊邏輯分類 ({pid_arg})...")
        
        # ==== 呼叫 PID Library ====
        if pid_arg == 'park':
            prob_dict, class_names = pid_library.pid_method_park(
                Z_filled, Zdr_filled, Kdp_filled, rhohv_filled
            )
        elif pid_arg == 'way':
            print("Warning: 'way' 方法尚未實作於 pid_library，暫時使用 Park 方法")
            prob_dict, class_names = pid_library.pid_method_park(
                Z_filled, Zdr_filled, Kdp_filled, rhohv_filled
            )
        else:
            raise ValueError(f"未知的 PID 方法: {pid_arg}")

        # ==== 找出最高分分類 (Winner Take All) ====
        print("🔍 判定最高分分類...")
        stacked_probs = np.stack([prob_dict[cls] for cls in class_names])
        max_indices = np.argmax(stacked_probs, axis=0)
        max_scores = np.max(stacked_probs, axis=0)

        # ==== 建立最終分類陣列 ====
        final_class = np.full(Z.shape, -1, dtype=np.int16)
        valid_mask = (max_scores > 0) & (~np.isnan(Z_filled))
        final_class[valid_mask] = max_indices[valid_mask]

        # ==== 建立 Py-ART Field ====
        mask = (final_class == -1)
        masked_class_data = np.ma.masked_array(final_class, mask=mask)

        class_field = {
            'data': masked_class_data,
            'units': 'category',
            'long_name': 'hydrometeor_type',
            'standard_name': 'hydrometeor_type',
            'valid_min': 0,
            'valid_max': len(class_names) - 1,
            '_FillValue': -1,
            'missing_value': -1,
            'legend': ', '.join([f"{i}:{name}" for i, name in enumerate(class_names)])
        }

        radar.add_field('hydro_class', class_field, replace_existing=True)

        # ==== 統計分類像素 ====
        hydro_data = final_class.flatten()
        hydro_data_valid = hydro_data[hydro_data != -1]
        unique, counts = np.unique(hydro_data_valid, return_counts=True)
        idx_to_name = {i: name for i, name in enumerate(class_names)}

        stats_dict = {
            'class_code': [],
            'class_name': [],
            'pixel_count': []
        }
        
        print(f"{'Class':<15}: Count")
        print("-" * 25)
        for code, count in zip(unique, counts):
            name = idx_to_name.get(code, f"Unknown ({code})")
            print(f"{name:<15}: {count}")
            stats_dict['class_code'].append(code)
            stats_dict['class_name'].append(name)
            stats_dict['pixel_count'].append(count)

        stats_df = pd.DataFrame(stats_dict)
        stats_df.to_csv(stats_csv_path, index=False)

        # ==== 儲存 NetCDF ====
        pyart.io.write_cfradial(output_path, radar)
        print(f"✅ 已儲存至：{output_path}")
        print(f"📄 統計 CSV 已儲存至：{stats_csv_path}\n")
        time_end = time.time()
        print(f"⏱️ 處理時間: {time_end - time_kdp_end:.2f} 秒\n")

    except Exception as e:
        import traceback
        print(f"❌ 發生錯誤：{e}")
        print(traceback.format_exc())
        continue