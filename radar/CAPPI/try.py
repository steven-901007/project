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
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.font_manager import FontProperties
# [新增] 引入 Matplotlib 的矩形選取工具
from matplotlib.widgets import RectangleSelector

# 解決 Matplotlib 中文顯示問題 (請確保路徑正確)
data_top_path = "/home/steven/python_data/radar" # 原始路徑
# data_top_path = "." # 測試用，請改回你的原始路徑
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
plt.rcParams['axes.unicode_minus'] = False

## ==== 時間與參數設定 ==== ##
year = sys.argv[1] if len(sys.argv) > 1 else '2021'
month = sys.argv[2] if len(sys.argv) > 2 else '05'
day = sys.argv[3] if len(sys.argv) > 3 else '24'
station = sys.argv[4] if len(sys.argv) > 4 else 'RCWF'
draw_one_or_all = sys.argv[5] if len(sys.argv) > 5 else 'all'

# [修改] 設定高度層：只計算 3km (3000m)
target_heights_amsl = [3000] 
thickness_m = 500  

hh = '04'
mm = '13'
ss = '00'

target_col = 'reflectivity' 

shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp" # 原始路徑
# shapefile_path = f"COUNTY_MOI_1090820.shp" # 測試用

# 存檔路徑
save_dir_root = f"{data_top_path}/CAPPI/{year}{month}{day}_{station}/{year}{month}{day}/{target_col}"
os.makedirs(save_dir_root, exist_ok=True)

## ============================== CWA Colormap 定義 (維持不變) ============================== ##
def get_cwa_ref_cmap():
    if target_col == 'reflectivity':
        cwa_colors = ['#00FFFF', '#0090FF', '#0000FF', '#00FF00', '#00C800', '#009000', '#FFFF00', '#FFD200', '#FF9000', '#FF0000', '#C80000', '#900000', '#FF00FF', '#900090']
        levels = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
    elif target_col == 'differential_reflectivity':
        cwa_colors = ['#0000FF', '#0090FF', '#00FFFF', '#00FF00', '#FF0000', '#FFA500', '#FFFF00', '#800080']
        levels = [-3, -1, 0, 1, 2, 2.5, 5, 7.5, 10]
    elif target_col == 'cross_correlation_ratio':
        cwa_colors = ['#FF0000', '#FFA500', '#FFFF00', '#00FF00', '#0000FF']
        levels = [0.0, 0.25, 0.5, 0.75, 0.95, 1.0]
    
    cmap = ListedColormap(cwa_colors)
    cmap.set_under('gray')
    cmap.set_over('gray')  
    norm = BoundaryNorm(levels, ncolors=len(cwa_colors), clip=False)
    return cmap, norm, levels

# 取得 CWA 樣式設定
cwa_cmap, cwa_norm, cwa_levels = get_cwa_ref_cmap()

## ==== 找出要處理的 VOL 檔案清單 ==== ##
vol_folder_base = f"{data_top_path}/data/{year}{month}{day}_u.{station}" # 原始路徑
# vol_folder_base = "." # 測試用

if draw_one_or_all == 'one':
    vol_file = f"{vol_folder_base}/{year}{month}{day}{hh}{mm}{ss}.VOL"
    vol_files = [vol_file]
else:
    vol_files = sorted(glob(f"{vol_folder_base}/*.VOL"))

if not vol_files:
    print(f"❌ 找不到任何 .VOL 檔案在: {vol_folder_base}")
    sys.exit()

# ==========================================================================================
# [新增功能] 互動式選取區域函數
# ==========================================================================================
# 用來儲存選取結果的全域變數
# ... (前面的 import 與參數設定維持不變) ...

# ==========================================================================================
# [修改功能] 互動式選取區域函數 (改為接收 radar 物件以提升效率)
# ==========================================================================================
selected_region = {'lon_min': None, 'lon_max': None, 'lat_min': None, 'lat_max': None}

def line_select_callback(eclick, erelease):
    """
    當滑鼠放開時觸發的回呼函數，記錄選取的經緯度邊界
    """
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    
    selected_region['lon_min'] = min(x1, x2)
    selected_region['lon_max'] = max(x1, x2)
    selected_region['lat_min'] = min(y1, y2)
    selected_region['lat_max'] = max(y1, y2)
    
    print(f"   >>> 選取範圍: Lon [{selected_region['lon_min']:.3f} ~ {selected_region['lon_max']:.3f}], Lat [{selected_region['lat_min']:.3f} ~ {selected_region['lat_max']:.3f}]")

def select_region_interactively(radar, target_h_amsl, thickness, time_label):
    """
    使用已讀取的 radar 物件畫圖並啟動選取器
    """
    # 每次呼叫前，先重置選取狀態 (避免誤用上一次的範圍)
    for key in selected_region:
        selected_region[key] = None

    try:
        # 提取資料 (只為了畫選取用的底圖)
        raw_lats = radar.gate_latitude['data'].flatten()
        raw_lons = radar.gate_longitude['data'].flatten()
        raw_alts = radar.gate_altitude['data'].flatten()
        raw_ref = radar.fields[target_col]['data'].filled(np.nan).flatten()
        
        # 高度篩選
        h_min = target_h_amsl - thickness
        h_max = target_h_amsl + thickness
        mask = (raw_alts >= h_min) & (raw_alts <= h_max) & (~np.isnan(raw_ref))
        
        plot_lons = raw_lons[mask]
        plot_lats = raw_lats[mask]
        plot_ref = raw_ref[mask]

        # 繪圖準備
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
        
        try:
            ax.add_geometries(Reader(shapefile_path).geometries(), ccrs.PlateCarree(),
                              facecolor='none', edgecolor='black', linewidth=1)
        except:
            ax.coastlines(resolution='10m', color='black')

        ax.scatter(plot_lons, plot_lats, c=plot_ref, cmap=cwa_cmap, norm=cwa_norm, s=2, zorder=2, alpha=0.7)
        
        # 設定初始視野
        ax.set_extent([121.5, 122.5, 24.8, 25.4])
        ax.gridlines(draw_labels=True)
        
        title_str = f"時間: {time_label}\n請框選此時間點的計算區域 ({target_h_amsl}m)"
        ax.set_title(title_str, fontproperties=title_font, color='red')

        # 啟動矩形選取器 (Matplotlib 新版寫法)
        rs = RectangleSelector(ax, line_select_callback,
                               useblit=True,
                               button=[1], minspanx=5, minspany=5,
                               spancoords='pixels', interactive=True,
                               props=dict(facecolor='red', edgecolor='black', alpha=0.3, fill=True))
        
        print(f"\n請在跳出的視窗中框選 [{time_label}] 的範圍，選好後請關閉視窗...")
        plt.show(block=True) # 等待視窗關閉

    except Exception as e:
        print(f"❌ 互動選取過程發生錯誤: {e}")
        # 如果出錯，這裡不強制退出，讓迴圈可能有機會跑下一個

# ==========================================================================================
# 主程式流程 (修改版)
# ==========================================================================================

print("開始批次處理 (每張圖皆需手動框選)...\n")
all_stats_data = []

# 【開始正式迴圈】
for vol_file in vol_files:
    try:
        # 1. 先讀取雷達檔案 (這樣物件可以傳給選取器，也可以傳給後面處理，不用讀兩次)
        radar = pyart.io.read_nexrad_archive(vol_file)
        
        time_str = os.path.basename(vol_file).split('.')[0]
        time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
        time_str_lct = (time_dt + timedelta(hours=8)).strftime("%Y%m%d%H%M")
        radar_alt_m = radar.altitude['data'][0]
        
        print(f"==========================================")
        print(f"正在處理: {time_str_lct}")

        # 2. 【關鍵修改】在迴圈內呼叫選取函數
        select_region_interactively(radar, target_heights_amsl[0], thickness_m, time_str_lct)

        # 檢查是否有選取
        if selected_region['lon_min'] is None:
            print(f"⚠️ 警告: 您未針對 {time_str_lct} 選取任何區域，跳過此檔案。")
            plt.close('all') # 確保視窗關閉
            continue

        # 取得當次選取的範圍
        lon_min, lon_max = selected_region['lon_min'], selected_region['lon_max']
        lat_min, lat_max = selected_region['lat_min'], selected_region['lat_max']
        
        print(f"✅ 套用範圍: Lon[{lon_min:.2f}-{lon_max:.2f}], Lat[{lat_min:.2f}-{lat_max:.2f}]")

        # 3. 繼續原本的資料處理 (使用同一個 radar 物件)
        raw_lats = radar.gate_latitude['data']
        raw_lons = radar.gate_longitude['data']
        raw_alts = radar.gate_altitude['data']
        raw_ref = radar.fields[target_col]['data']

        ref_flatten = raw_ref.filled(np.nan).flatten()
        valid_mask = ~np.isnan(ref_flatten)
        
        lats_clean = raw_lats.flatten()[valid_mask]
        lons_clean = raw_lons.flatten()[valid_mask]
        alts_clean = raw_alts.flatten()[valid_mask]
        ref_clean = ref_flatten[valid_mask]
        
        time_file = f'{save_dir_root}/{time_str_lct}'
        os.makedirs(time_file, exist_ok=True)

        ## ==== 迴圈：針對每個高度畫圖 (這裡只會跑 3km) ==== ##
        for target_h in tqdm(target_heights_amsl, desc="繪製與計算"):
            h_min = target_h - thickness_m
            h_max = target_h + thickness_m

            # 高度篩選
            height_mask = (alts_clean >= h_min) & (alts_clean <= h_max)
            plot_lons = lons_clean[height_mask]
            plot_lats = lats_clean[height_mask]
            plot_ref = ref_clean[height_mask]

            # ==== 使用剛剛選取的經緯度進行篩選 ====
            roi_mask = (plot_lons >= lon_min) & (plot_lons <= lon_max) & \
                       (plot_lats >= lat_min) & (plot_lats <= lat_max)
            
            plot_lons = plot_lons[roi_mask]
            plot_lats = plot_lats[roi_mask]
            plot_ref = plot_ref[roi_mask]
            # ====================================

            if len(plot_ref) == 0:
                print(f"  高度 {target_h}m (在選取範圍內) 無資料點。")
                # 即使無資料，可能也需要記錄一筆空的統計 (看你需求，這裡維持跳過)
                continue

            # 排序
            sort_idx = np.argsort(plot_ref)
            plot_lons = plot_lons[sort_idx]
            plot_lats = plot_lats[sort_idx]
            plot_ref = plot_ref[sort_idx]

            ## ==== 畫圖 (Scatter) ==== ##
            fig = plt.figure(figsize=(10, 8))
            ax = plt.axes(projection=ccrs.PlateCarree())

            # 統計
            counts, bins = np.histogram(plot_ref, bins=cwa_levels)
            row_data = {'Time_LCT': time_str_lct, 'Height_m': target_h}
            for i in range(len(counts)):
                col_name = f"{bins[i]}_{bins[i+1]}"
                row_data[col_name] = counts[i]
            
            # [新增] 將選取的範圍也記錄到 CSV，方便日後檢查
            row_data['ROI_Lon_Min'] = lon_min
            row_data['ROI_Lon_Max'] = lon_max
            row_data['ROI_Lat_Min'] = lat_min
            row_data['ROI_Lat_Max'] = lat_max
            
            all_stats_data.append(row_data)

            # 台灣邊界
            try:
                ax.add_geometries(Reader(shapefile_path).geometries(), crs=ccrs.PlateCarree(),
                                facecolor='none', edgecolor='black', linewidth=1.5, zorder=5)
            except:
                 ax.coastlines(resolution='10m', color='black', zorder=5)

            # SCATTER PLOT
            sc = ax.scatter(plot_lons, plot_lats, c=plot_ref, cmap=cwa_cmap, norm=cwa_norm,
                            s=2.5, edgecolors='none', transform=ccrs.PlateCarree(), zorder=2)

            # 標題與資訊
            height_km = target_h / 1000.0
            time_title = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")
            title_str = (f"CAPPI {height_km:.0f}km({target_col})\n{time_title} LCT\n(ROI Selected)")
            ax.set_title(title_str, fontproperties=title_font)

            ax.set_xlim(lon_min, lon_max)
            ax.set_ylim(lat_min, lat_max)

            # Colorbar
            cbar = plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04, ticks=cwa_levels, spacing='uniform')
            gl = ax.gridlines(draw_labels=True)
            gl.right_labels = False

            output_filename = f"{time_str_lct}00_{int(height_km):02d}km_ROI.png"
            output_path = os.path.join(time_file, output_filename)
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

    except Exception as e:
        print(f"❌ 錯誤：{vol_file}\n原因：{e}")
        # import traceback
        # traceback.print_exc()

# ... (後面的儲存 CSV 維持不變) ...

# --- 儲存 CSV ---
if all_stats_data:
    df_stats = pd.DataFrame(all_stats_data)
    print("\n--- 統計結果預覽 ---")
    print(df_stats.head())
    csv_file_path = f"{save_dir_root}/CAPPI_point_of_{target_col}_ROI.csv"
    df_stats.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ 統計結果已儲存至: {csv_file_path}")
else:
    print("\n⚠️ 沒有產生任何統計數據 (可能選取區域內無資料)。")