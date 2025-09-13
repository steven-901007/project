import os
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
import pyart

## =========================
## 參數（請確認路徑）
## =========================

vol_file_path = rf"C:\Users\steve\python_data\radar\data\20210531_u.RCWF\20210531000200.VOL"

## =========================
## 讀檔
## =========================
radar = pyart.io.read(vol_file_path)  # 讀 IRIS/Sigmet .VOL

## =========================
## 基本資訊
## =========================
nsweeps = radar.nsweeps
nrays = radar.nrays
ngates = radar.ngates

range_data = radar.range["data"]                # 每個 gate 中心到雷達的斜距（m）
gate_spacing = float(np.median(np.diff(range_data)))  # 徑向 gate 間距（m）
start_range = float(range_data[0])              # 第一個 gate 的中心距離（m）

## =========================
## 各 Sweep 仰角（取各自中位數）
## =========================
sweep_elev_list = []  # 仰角列表（度）
for i in range(nsweeps):
    sl = radar.get_slice(i)
    elevs = radar.elevation["data"][sl]
    sweep_elev_list.append(float(np.median(elevs)))
elevation_count = len(sweep_elev_list)  # 仰角種類數

## =========================
## Sweep 0 的方位角解析度與光束數
## =========================
s0 = radar.get_slice(0)
az0 = radar.azimuth["data"][s0]  # 0號 sweep 的每筆 ray 的方位角（度）
# 為避免 0/360 跳變，先排序再補 360
az_sorted = np.sort(az0)
daz = np.diff(np.r_[az_sorted, az_sorted[0] + 360.0])
azimuth_res_deg = float(np.median(daz))               # 每幾度一筆（中位數）
rays_per_sweep0 = len(az0)                            # Sweep0 的 ray 數
delta_theta_rad = math.radians(azimuth_res_deg)       # 角度→弧度

## =========================
## 時間（掃一圈 & 全部 volume）
## =========================
# radar.time['units'] 形如: "seconds since 2021-05-30T16:00:00Z"
units = radar.time["units"]
ref_str = units.split("since")[1].strip()
try:
    ref_dt = datetime.fromisoformat(ref_str.replace("Z", "+00:00"))
except Exception:
    ref_dt = datetime.strptime(ref_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

t_all = radar.time["data"]
times_all = np.array([ref_dt + timedelta(seconds=float(s)) for s in t_all])

# Sweep 0 的起訖時間
t0_start_idx = int(radar.sweep_start_ray_index["data"][0])
t0_end_idx   = int(radar.sweep_end_ray_index["data"][0])
t0_start = times_all[t0_start_idx]
t0_end   = times_all[t0_end_idx]
sweep0_duration_sec = (t0_end - t0_start).total_seconds()

# 整個 Volume 的起訖時間
vol_start = times_all[int(radar.sweep_start_ray_index["data"][0])]
vol_end   = times_all[int(radar.sweep_end_ray_index["data"][-1])]
volume_duration_sec = (vol_end - vol_start).total_seconds()

## =========================
## 「每一個 bin 有幾筆資料」的定義與計算（以 Sweep 0）
## =========================
# 固定某一個 range gate（bin），沿著一圈的 rays 數量 = 該 bin 的資料筆數
per_bin_count_sweep0 = rays_per_sweep0

## =========================
## 同一個 bin（固定 range）第一筆與最後一筆距離（sweep 內/跨 sweep）
## =========================
# 若以 Sweep 0 來看，同一個 range gate 的第一筆/最後一筆距離雷達的斜距會相同（都是該 gate 中心距離）
bin_idx = 0  # 你要看哪一個 gate（預設 0 = 最近一格）
range_same_bin_m = start_range + gate_spacing * bin_idx  # 斜距（m）

# 如果你想跨所有 sweep 比較同一 gate index 的距離，斜距仍相同（是儀器固定的 range 索引），
# 不過對應的高度會隨仰角不同（這裡只回報距離，不計高度）
same_bin_first_last_dist_m_tuple = (range_same_bin_m, range_same_bin_m)

## =========================
## 同一個 bin 每筆資料間距（同一 range，沿方位向的相鄰光束弧長）
## =========================
arc_len_same_bin_m = range_same_bin_m * delta_theta_rad  # 近距離示例（bin_idx=0）
# 一般我們也會看「最近一格」與「最遠一格」的方位向弧長
range_near_m = start_range + 0 * gate_spacing
range_far_m  = start_range + (ngates - 1) * gate_spacing
arc_len_near_m = range_near_m * delta_theta_rad
arc_len_far_m  = range_far_m  * delta_theta_rad

## =========================
## 「網格尺寸」（雷達視角）— Sweep 0 最近/最遠一格
## 徑向長度 = gate_spacing
## 方位向寬度 = r * Δθ（弧長）
## =========================
cell_near = {
    "與測站距離_m": float(range_near_m),
    "格點徑向長度_m": float(gate_spacing),
    "格點方位向寬度_m": float(arc_len_near_m),
}
cell_far = {
    "與測站距離_m": float(range_far_m),
    "格點徑向長度_m": float(gate_spacing),
    "格點方位向寬度_m": float(arc_len_far_m),
}

## =========================
## 表格整理 & 輸出
## =========================
summary_rows = [
    ["檔名", os.path.basename(vol_file_path)],
    ["Sweep 數量(=仰角種數)", nsweeps],
    ["每 ray 的 bin 數(ngates)", ngates],
    ["Sweep0 的 ray 數(=每個 bin 的資料筆數)", per_bin_count_sweep0],
    ["方位角解析度(度/筆)", round(azimuth_res_deg, 4)],
    ["Sweep0 掃一圈耗時(秒)", round(sweep0_duration_sec, 3)],
    ["整個 Volume 耗時(秒)", round(volume_duration_sec, 3)],
    ["gate spacing(徑向, m)", round(gate_spacing, 3)],
    ["start range(第0格中心, m)", round(start_range, 3)],
]
summary_df = pd.DataFrame(summary_rows, columns=["項目", "數值"])

elev_df = pd.DataFrame({
    "Sweep索引": list(range(nsweeps)),
    "仰角(度;中位數)": np.round(sweep_elev_list, 3),
})

cell_df = pd.DataFrame([
    ["最近一格(gate 0)", round(range_near_m, 3), round(gate_spacing, 3), round(arc_len_near_m, 3)],
    [f"最遠一格(gate {ngates-1})", round(range_far_m, 3), round(gate_spacing, 3), round(arc_len_far_m, 3)],
], columns=["位置", "與測站距離(斜距,m)", "格點徑向長度(m)", "格點方位向寬度(m)"])

bin_spacing_df = pd.DataFrame([
    ["最近range(gate 0)", round(arc_len_near_m, 3)],
    [f"最遠range(gate {ngates-1})", round(arc_len_far_m, 3)],
], columns=["同一range gate（相鄰光束）", "距離(弧長,m)"])

# 印出
print("=== 概要指標 ===")
print(summary_df.to_string(index=False))
print("\n=== 各Sweep仰角(度) ===")
print(elev_df.to_string(index=False))
print("\n=== Sweep0 近/遠 range 的格點尺寸（雷達視角） ===")
print(cell_df.to_string(index=False))
print("\n=== 同一 range gate 相鄰光束距離（Sweep0） ===")
print(bin_spacing_df.to_string(index=False))

# 另存 CSV
out_dir = os.path.join(os.path.dirname(vol_file_path), "_VOL_metrics_out")
os.makedirs(out_dir, exist_ok=True)
summary_df.to_csv(os.path.join(out_dir, "summary.csv"), index=False, encoding="utf-8-sig")
elev_df.to_csv(os.path.join(out_dir, "elevations.csv"), index=False, encoding="utf-8-sig")
cell_df.to_csv(os.path.join(out_dir, "cell_sizes_sweep0.csv"), index=False, encoding="utf-8-sig")
bin_spacing_df.to_csv(os.path.join(out_dir, "bin_adjacent_spacing_sweep0.csv"), index=False, encoding="utf-8-sig")

## =========================
## 額外：若你想指定 bin_idx 來看「同一 bin 第一筆與最後一筆距離」
## =========================
print("\n=== 同一個 bin（固定 gate index）第一/最後一筆距離（Sweep0 內） ===")
print(f"bin_idx={bin_idx} -> 距離(斜距,m) first/last = ({range_same_bin_m:.3f}, {range_same_bin_m:.3f})")
