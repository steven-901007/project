import pyart
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from glob import glob
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
import platform
import sys
import pandas as pd
from tqdm import tqdm
# 引入必要的顏色控制模組
from matplotlib.colors import ListedColormap, BoundaryNorm 


## ==== 時間與參數設定 ==== ##
year = sys.argv[1] if len(sys.argv) > 1 else '2021'
month = sys.argv[2] if len(sys.argv) > 2 else '05'
day = sys.argv[3] if len(sys.argv) > 3 else '24'
station = sys.argv[4] if len(sys.argv) > 4 else 'RCWF'
draw_one_or_all = sys.argv[5] if len(sys.argv) > 5 else 'all'

# 設定高度層 (AMSL 海拔高度, 單位: m)
target_heights_amsl = np.arange(1000, 11000, 1000)
thickness_m = 500  # 上下 500m

hh = '04'
mm = '13'
ss = '00'

target_col = 'reflectivity' # reflectivity 或 differential_reflectivity 或 cross_correlation_ratio

lon_min, lon_max = 121.57, 121.74 
lat_min, lat_max = 24.96, 25.09   

data_top_path = "/home/steven/python_data/radar"

## 測站名
if station == 'RCWF':
    station_realname = '五分山'
elif station == 'RCCG':
    station_realname = '七股'
elif station == 'RCKT':
    station_realname = '墾丁'
elif station == 'RCHL':
    station_realname = '花蓮'

shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
# 存檔路徑
save_dir_root = f"{data_top_path}/CAPPI/{year}{month}{day}_{station}/{year}{month}{day}/{target_col}"
os.makedirs(save_dir_root, exist_ok=True)


## ============================== 手動定義 CWA (中央氣象署) Colormap ============================== ##
def get_cwa_ref_cmap():
    if target_col == 'reflectivity':
        """
        手動建立台灣中央氣象署 (CWA/CWB) 風格的雷達回波色階
        """
        # 定義色階 (這是根據你提供的圖檔與氣象署慣用色票整理的)
        cwa_colors = [
            '#00FFFF', # 00-05 dBZ (Cyan / 淺藍)
            '#0090FF', # 05-10 dBZ (Sky Blue / 天藍)
            '#0000FF', # 10-15 dBZ (Blue / 藍)
            '#00FF00', # 15-20 dBZ (Lime / 螢光綠)
            '#00C800', # 20-25 dBZ (Green / 綠)
            '#009000', # 25-30 dBZ (Dark Green / 深綠)
            '#FFFF00', # 30-35 dBZ (Yellow / 黃)
            '#FFD200', # 35-40 dBZ (Orange-Yellow / 橙黃)
            '#FF9000', # 40-45 dBZ (Orange / 橘)
            '#FF0000', # 45-50 dBZ (Red / 紅)
            '#C80000', # 50-55 dBZ (Dark Red / 深紅)
            '#900000', # 55-60 dBZ (Maroon / 褐紅) - 註: 有些版本這裡會轉紫，視具體年份而定，此處依圖示調整
            '#FF00FF', # 60-65 dBZ (Magenta / 洋紅)
            '#900090'  # 65+   dBZ (Purple / 紫)
        ]
        
        # 定義每個顏色對應的數值範圍 (0 到 70，每 5 一格)
        levels = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]

    elif target_col == 'differential_reflectivity': #Zdr
        """
        手動建立 CWA 雙偏振差異色階
        """
        cwa_colors = [
            '#0000FF',
            '#0090FF',
            '#00FFFF',
            '#00FF00', 
            '#FF0000', 
            '#FFA500', 
            '#FFFF00', 
            '#800080'  
        ]
        
        levels = [-3, -1, 0, 1, 2, 2.5, 5, 7.5, 10]
    elif target_col == 'cross_correlation_ratio':
        """
        手動建立 CWA 相關係數色階
        """
        cwa_colors = [
            '#FF0000', # 0.0 - 0.5 (Red / 紅)
            '#FFA500', # 0.5 - 0.7 (Orange / 橘)
            '#FFFF00', # 0.7 - 0.85 (Yellow / 黃)
            '#00FF00', # 0.85 - 0.95 (Green / 綠)
            '#0000FF'  # 0.95 - 1.0 (Blue / 藍)
        ]
        
        levels = [0.0, 0.25, 0.5, 0.75, 0.95, 1.0]
    
    # 建立 Colormap
    cmap = ListedColormap(cwa_colors)
    cmap.set_under('gray')
    cmap.set_over('gray')  
    
    # 建立 BoundaryNorm (關鍵！讓顏色變成色塊)
    norm = BoundaryNorm(levels, ncolors=len(cwa_colors), clip=False)
    
    return cmap, norm, levels


from matplotlib.font_manager import FontProperties
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
plt.rcParams['axes.unicode_minus'] = False

## ==== 找出要處理的 VOL 檔案清單 ==== ##
if draw_one_or_all == 'one':
    vol_file = f"{data_top_path}/data/{year}{month}{day}_u.{station}/{year}{month}{day}{hh}{mm}{ss}.VOL"
    vol_files = [vol_file]
else:
    vol_folder = f"{data_top_path}/data/{year}{month}{day}_u.{station}"
    vol_files = sorted(glob(f"{vol_folder}/*.VOL"))

# 取得 CWA 樣式設定
cwa_cmap, cwa_norm, cwa_levels = get_cwa_ref_cmap()
all_stats_data = []

for vol_file in vol_files:
    try:
        # 1. 讀取雷達檔案
        radar = pyart.io.read_nexrad_archive(vol_file)
        time_str = os.path.basename(vol_file).split('.')[0]
        time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
        time_str_lct = (time_dt + timedelta(hours=8)).strftime("%Y%m%d%H%M")
        
        # 2. 取得雷達海拔高度 (m)
        radar_alt_m = radar.altitude['data'][0]
        print(f"處理: {time_str_lct}, 測站高: {radar_alt_m:.1f}m")

        # 3. 提取原始資料
        raw_lats = radar.gate_latitude['data']
        raw_lons = radar.gate_longitude['data']
        raw_alts = radar.gate_altitude['data'] # AMSL
        raw_ref = radar.fields[target_col]['data']

        # 4. 資料扁平化與初步清洗
        ref_flatten = raw_ref.filled(np.nan).flatten()
        
        # 過濾掉 NaN
        valid_mask = ~np.isnan(ref_flatten)
        
        lats_clean = raw_lats.flatten()[valid_mask]
        lons_clean = raw_lons.flatten()[valid_mask]
        alts_clean = raw_alts.flatten()[valid_mask]
        ref_clean = ref_flatten[valid_mask]
        time_file = f'{save_dir_root}/{time_str_lct}'
        os.makedirs(time_file, exist_ok=True)
        print(f"  原始點數: {len(ref_flatten)}, 有效點數: {len(ref_clean)}")



        ## ==== 迴圈：針對每個高度畫圖 ==== ##
        for target_h in tqdm(target_heights_amsl,desc="繪製高度層 CAPPI"):
            if target_h == 3000:
                h_min = target_h - thickness_m
                h_max = target_h + thickness_m

                # 5. 高度篩選
                height_mask = (alts_clean >= h_min) & (alts_clean <= h_max)
                
                # 取得該層數據
                plot_lons = lons_clean[height_mask]
                plot_lats = lats_clean[height_mask]
                plot_ref = ref_clean[height_mask]

                if len(plot_ref) == 0:
                    print(f"  高度 {target_h}m 無資料點，跳過。")
                    continue

                # 【重要步驟】 排序：將強度小的排前面，強度大的排後面
                # 這樣畫圖時，強回波才會蓋在上面，不會被弱回波遮住
                sort_idx = np.argsort(plot_ref)
                plot_lons = plot_lons[sort_idx]
                plot_lats = plot_lats[sort_idx]
                plot_ref = plot_ref[sort_idx]

                ## ==== 畫圖 (Scatter) ==== ##
                fig = plt.figure(figsize=(10, 8))
                ax = plt.axes(projection=ccrs.PlateCarree())


                # 統計各顏色區間點數 (邏輯修改)
                counts, bins = np.histogram(plot_ref, bins=cwa_levels)
                
                # 建立這一列的資料 (包含時間、高度)
                row_data = {
                    'Time_LCT': time_str_lct,
                    'Height_m': target_h
                }
                # 將各區間的數量加入字典，例如 "0_5": 1234
                for i in range(len(counts)):
                    col_name = f"{bins[i]}_{bins[i+1]}"
                    row_data[col_name] = counts[i]
                
                all_stats_data.append(row_data)
                # -----------------------------------


                # 台灣邊界
                ax.add_geometries(
                    Reader(shapefile_path).geometries(),
                    crs=ccrs.PlateCarree(),
                    facecolor='none',
                    edgecolor='black',
                    linewidth=1.5,
                    zorder=5 
                )

                # SCATTER PLOT
                sc = ax.scatter(
                    plot_lons,
                    plot_lats,
                    c=plot_ref,
                    cmap=cwa_cmap,   # 使用 CWA Colormap
                    norm=cwa_norm,   # 使用 CWA Norm (關鍵)
                    s=1.5,           # 建議稍微調大一點點 (原本0.1可能太小看不清楚)
                    edgecolors='none',
                    transform=ccrs.PlateCarree(),
                    zorder=2
                )

                # 標題與資訊
                height_km = target_h / 1000.0
                time_title = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")
                
                title_str = (f"CAPPI {height_km:.0f}km({target_col})\n"
                            f"{time_title} LCT")
                
                ax.set_title(title_str, fontproperties=title_font)
                
                # # 設定範圍
                # radar_lon = radar.longitude['data'][0]
                # radar_lat = radar.latitude['data'][0]
                # ax.set_extent([radar_lon - 1.5, radar_lon + 1.5, radar_lat - 1.5, radar_lat + 1.5])

                # 設定範圍
                ax.set_xlim(lon_min, lon_max)
                ax.set_ylim(lat_min, lat_max)

                # 5. 加入 Colorbar (配合 levels)
                cbar = plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04, 
                                    ticks=cwa_levels, spacing='uniform')


                gl = ax.gridlines(draw_labels=True)
                gl.right_labels = False

                output_filename = f"{time_str_lct}00_{int(height_km):02d}km.png"
                output_path = os.path.join(time_file, output_filename)
                
                plt.savefig(output_path, dpi=150, bbox_inches='tight')
                plt.close()



        print(f"✅ 完成 {time_str_lct}")

    except Exception as e:
        print(f"❌ 錯誤：{vol_file}\n原因：{e}")
        import traceback
        traceback.print_exc()
# --- 新增：將所有統計結果存成 CSV ---

if all_stats_data:
    df_stats = pd.DataFrame(all_stats_data)
    print(df_stats)

    csv_file_path = f"{save_dir_root}/CAPPI_point_of_{target_col}.csv"
    df_stats.to_csv(csv_file_path, index=False, encoding='utf-8-sig')