import os, glob, re
import pandas as pd
import sys

## ============================== 參數區（可自行修改） ============================== ##
data_top_path_str = r"/home/steven/python_data/2025DAAN_park"  # 資料總路徑
event_folder_str  = r"20250805-0808"                           # 事件資料夾（含 #1 ~ #12）
sensor_tag_str = sys.argv[1] if len(sys.argv) > 1 else "#1"    # ★ 想整理哪一個感測器：'#1'、'#2' ... '#12'
sensor_folder_path_str = rf"{data_top_path_str}/{event_folder_str}/{sensor_tag_str}"

save_csv_path_str = rf"{data_top_path_str}/data/{sensor_tag_str}.csv"  # ★ 輸出路徑
## ================================================================================ ##

## 讀一個 CSV：抓欄 1(Temp)、4(Time)、9(Lux)；原始檔沒有標題，所以 header=None，並直接給 names
def read_one_csv(file_path_str):
    """讀一個 CSV，回傳欄位：['Temp','Time','Lux_raw']"""
    data_df = pd.read_csv(
        file_path_str,
        header=None,                             # 檔案沒有標題列
        usecols=[1, 4, 9],                       # Temp(1), Time(4), Lux(9)
        names=['Temp', 'Time', 'Lux_raw'],       # 直接命名欄位
        dtype={'Time': 'string'},                # 避免時間被當科學記號
        engine='python',
        on_bad_lines='skip'
    )
    return data_df

def clean_numeric_to_float(_x):
    """移除 '$' 等非數字字元後轉 float；失敗回 NaN"""
    try:
        return float(re.sub(r'[^0-9.\-]', '', str(_x)))
    except Exception:
        return float('nan')

## 讀全部檔案並整理
def build_sensor_df(sensor_folder_path_str):
    """讀取指定感測器資料夾下所有 CSV，回傳整併後的 DataFrame"""
    csv_path_list = sorted(glob.glob(os.path.join(sensor_folder_path_str, "*.csv")))
    if not csv_path_list:
        raise FileNotFoundError(f"找不到 CSV：{sensor_folder_path_str}")

    df_list = []
    for file_path_str in csv_path_list:
        one_df = read_one_csv(file_path_str)

        ## ★★ 指定檔的首列時間修正 ★★
        # 檔名：109_2025_08_05_03.csv
        # 第一筆 Time 由 20250805031108 → 20250805031102
        if os.path.basename(file_path_str) == "109_2025_08_05_03.csv":
            if not one_df.empty and str(one_df.at[0, 'Time']) == '20250805031108':  # 只修正第一筆
                one_df.at[0, 'Time'] = '20250805031102'  # 單行註解放後面 # 修正首列時間

        df_list.append(one_df)

    merged_df = pd.concat(df_list, ignore_index=True)

    ## 轉型與清理
    merged_df['Temp'] = pd.to_numeric(merged_df['Temp'], errors='coerce')  # 溫度為數值
    merged_df['Lux_raw'] = merged_df['Lux_raw'].map(clean_numeric_to_float)  # 去掉 $ 等符號
    merged_df['Illuminance_Wm2'] = merged_df['Lux_raw'] / 668.5  # 單位換算

    ## 時間欄位處理
    merged_df['DateTime'] = pd.to_datetime(merged_df['Time'], format='%Y%m%d%H%M%S', errors='coerce')
    merged_df = merged_df.dropna(subset=['DateTime'])  # 移除無法解析的時間

    ## 依時間排序
    merged_df = merged_df.sort_values('DateTime').reset_index(drop=True)

    return merged_df


## 計算每分鐘平均並回填到每筆資料
def attach_minute_means(input_df):
    """對 input_df 依分鐘聚合，計算 Temp / Illum 每分鐘平均，並 merge 回原表"""
    df = input_df.copy()
    df['Minute'] = df['DateTime'].dt.floor('min')  # 取該筆所在分鐘（YYYY-mm-dd HH:MM:00）

    ## groupby Minute 計算平均
    minute_mean_df = df.groupby('Minute', as_index=False).agg(
        Temp_min1_mean=('Temp', 'mean'),
        Illuminance_min1_mean=('Illuminance_Wm2', 'mean')
    )

    ## merge 回原始每筆資料（同一分鐘的每筆都帶相同的平均值）
    out_df = pd.merge(
        df,
        minute_mean_df,
        on='Minute',
        how='left'
    )

    ## 欄位順序整理
    out_df = out_df[['Time', 'DateTime', 'Temp', 'Illuminance_Wm2',
                     'Temp_min1_mean', 'Illuminance_min1_mean', 'Minute']]

    return out_df

## ============================== 主流程 ============================== ##
if __name__ == "__main__":
    ## 讀全部檔案
    all_data_df = build_sensor_df(sensor_folder_path_str)  # 取得：Time, DateTime, Temp, Lux_raw, Illuminance_Wm2

    ## 計算每分鐘平均並回填
    result_df = attach_minute_means(all_data_df)

    ## 建立資料夾並輸出 CSV
    os.makedirs(os.path.dirname(save_csv_path_str), exist_ok=True)
    result_df.to_csv(save_csv_path_str, index=False)

    print(f"[OK] {sensor_tag_str} 已整理完成，總筆數：{len(result_df)}")
    print(f"[OK] 已輸出：{save_csv_path_str}")
        # === 統計：原始值 與 每分鐘平均 的最大/最小 ===
    # 原始值（逐筆）
    raw_cols = ['Temp', 'Illuminance_Wm2']
    raw_min = result_df[raw_cols].min(numeric_only=True, skipna=True)
    raw_max = result_df[raw_cols].max(numeric_only=True, skipna=True)

    # 每分鐘平均（以分鐘為唯一鍵，避免重複列）
    avg_cols = ['Temp_min1_mean', 'Illuminance_min1_mean']
    by_minute_unique = result_df.drop_duplicates(subset=['Minute'])
    avg_min = by_minute_unique[avg_cols].min(numeric_only=True, skipna=True)
    avg_max = by_minute_unique[avg_cols].max(numeric_only=True, skipna=True)

    # 格式化輸出
    def f(x): 
        try:
            return f"{float(x):.3f}"
        except Exception:
            return "nan"

    print("\n=== 原始值（逐筆）Min/Max ===")
    print(f"Temp (°C)              : min={f(raw_min['Temp'])}  max={f(raw_max['Temp'])}")
    print(f"Illuminance (W/m²)     : min={f(raw_min['Illuminance_Wm2'])}  max={f(raw_max['Illuminance_Wm2'])}")

    print("\n=== 每分鐘平均（去重）Min/Max ===")
    print(f"Temp_min1_mean (°C)    : min={f(avg_min['Temp_min1_mean'])}  max={f(avg_max['Temp_min1_mean'])}")
    print(f"Illum_min1_mean (W/m²) : min={f(avg_min['Illuminance_min1_mean'])}  max={f(avg_max['Illuminance_min1_mean'])}")
