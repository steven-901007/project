import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re
from tqdm import tqdm

## === 共同參數（只用光照資料） ===
start_time_str = "2025-08-15 06:00:00"
end_time_str   = "2025-08-18 06:00:00"

xlim_start = pd.Timestamp("2025-08-15 06:00:00")
xlim_end   = pd.Timestamp("2025-08-18 06:00:00")

data_top_path = r"/home/steven/python_data/2025DAAN_park"
base_folder = rf"{data_top_path}/20250815-0818觀測坪"

name = 'Lux'
long_name = 'Illuminance'
y_unit = 'W/m²'

## === 小工具：讀一個 tag 的原始 CSV、做 5min centered 平滑，再取 1min（只光照） ===
def _read_prepare_minute_df(tag: str, full_time_df: pd.DataFrame):
    csv_folder_path = os.path.join(base_folder, tag)
    all_files_list = sorted(glob.glob(os.path.join(csv_folder_path, "*.csv")))
    if not all_files_list:
        print(f"{tag}: 找不到 CSV 檔案，略過")
        return None

    df_list = []
    for file_path in tqdm(all_files_list):
        data_df = pd.read_csv(
            file_path,
            header=None,
            usecols=[4, 9],
            dtype={4: 'string'},
            converters={9: lambda x: pd.to_numeric(re.sub(r'[^0-9.\-]', '', str(x)), errors='coerce') / 668.5},
            engine='python',
            on_bad_lines='skip'
        )
        data_df.columns = ['Time', name]

        ## #1 特殊修正
        target_basename_str = "109_2025_08_05_03.csv"
        old_time_str = '20250805031108'
        new_time_str = '20250805031102'
        if tag == "#1" and os.path.basename(file_path) == target_basename_str:
            if str(data_df.at[0, 'Time']) == old_time_str:
                data_df.at[0, 'Time'] = new_time_str

        data_df['DateTime'] = pd.to_datetime(data_df['Time'], format='%Y%m%d%H%M%S', errors='coerce')
        df_list.append(data_df[['DateTime', name]])

    if not df_list:
        return None

    merged_data_df = pd.concat(df_list, ignore_index=True)
    merged_data_df = pd.merge(full_time_df, merged_data_df, on='DateTime', how='left')
    merged_data_df[name] = pd.to_numeric(merged_data_df[name], errors='coerce').astype(float)

    merged_data_df = merged_data_df.sort_values('DateTime').set_index('DateTime')
    smooth_series = merged_data_df[name].rolling('5min', center=True, min_periods=1).mean()
    minute_df = smooth_series.resample('1min').mean().to_frame(name=name).reset_index()
    return minute_df

## === 主功能：只看 all 群組（#1~#12），繪製差值 (other - ref) ===
def draw_diff_lux_all(ref_tag: str):
    full_time_df = pd.DataFrame({'DateTime': pd.date_range(start=start_time_str, end=end_time_str, freq='2s')})
    tags_list = [f"#{i}" for i in range(1, 13)]
    if ref_tag not in tags_list:
        tags_list = [ref_tag] + tags_list

    tag_minute_df_dict = {}
    for tag in tags_list:
        minute_df = _read_prepare_minute_df(tag, full_time_df)
        if minute_df is not None:
            tag_minute_df_dict[tag] = minute_df

    if ref_tag not in tag_minute_df_dict:
        print(f"參考儀器 {ref_tag} 沒有可用資料，結束。")
        return

    date_range_df = pd.DataFrame({'DateTime': pd.date_range(start=start_time_str, end=end_time_str, freq='D')})
    date_list = date_range_df['DateTime'].dt.normalize().unique()

    output_folder = rf"{data_top_path}\{long_name}_Diff\{ref_tag}"
    os.makedirs(output_folder, exist_ok=True)

    y_label_str = f"Δ{long_name} (other − {ref_tag}) [{y_unit}]"

    for d in tqdm(date_list):
        day_start = pd.Timestamp(d)
        day_end   = day_start + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        day_start = max(day_start, pd.Timestamp(xlim_start))
        day_end   = min(day_end,   pd.Timestamp(xlim_end))
        if day_start > day_end:
            continue

        plt.figure(figsize=(14, 7))
        ax = plt.gca()

        ref_df = tag_minute_df_dict[ref_tag]
        ref_sub_df = ref_df[(ref_df['DateTime'] >= day_start) & (ref_df['DateTime'] <= day_end)][['DateTime', name]]
        ref_sub_df = ref_sub_df.rename(columns={name: f'{name}_ref'})

        has_any = False
        for tag, minute_df in tag_minute_df_dict.items():
            if tag == ref_tag:
                continue
            sub_df = minute_df[(minute_df['DateTime'] >= day_start) & (minute_df['DateTime'] <= day_end)][['DateTime', name]]
            if sub_df.empty or ref_sub_df.empty:
                continue

            merged_df = pd.merge(sub_df, ref_sub_df, on='DateTime', how='inner')
            if merged_df.empty:
                continue

            merged_df['Diff'] = merged_df[name] - merged_df[f'{name}_ref']
            plt.plot(merged_df['DateTime'], merged_df['Diff'], label=f'{tag} − {ref_tag}')
            has_any = True

        if not has_any:
            plt.close()
            continue

        ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
        ax.set_xlim(day_start, day_end)
        plt.xlabel('Time')
        plt.ylabel(y_label_str)
        plt.title(f"{day_start.strftime('%Y-%m-%d')} {long_name} vs {ref_tag}")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        save_path = rf"{output_folder}/result\{day_start.strftime('%Y%m%d')}_all_diff_vs_{ref_tag}.png"
        plt.savefig(save_path)
        # plt.show()

## === 範例呼叫（只看 all 群組） ===
ref_tag = '#5'   # 設定參考儀器
draw_diff_lux_all(ref_tag)
ref_tag = '#6'   # 設定參考儀器
draw_diff_lux_all(ref_tag)