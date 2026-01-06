import pyart
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from glob import glob
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy import geodesic
from matplotlib.font_manager import FontProperties
import sys
import pandas as pd

"""
專門for 20250701~20250811的code
閃電資料為CWA資料 位置在project/2025work/2025CWA_flash_plan/flash_data/CWA
雷達資料         位置在project/radar/data
"""

## ==== 時間設定 ==== ##
year = sys.argv[1] if len(sys.argv) > 1 else '2025'
month = sys.argv[2] if len(sys.argv) > 2 else '07'
day = sys.argv[3] if len(sys.argv) > 3 else '28'
station = sys.argv[4] if len(sys.argv) > 4 else 'RCCG'
hh = '02'
mm = '00'
ss = '00'

draw_one_or_all = 'all'
flash_conclution_minutes = 5  # 閃電時間結束前多少分鐘內的閃電要畫在圖上
## ==== 路徑設定 ==== ##
data_top_path = "/home/steven/python_data/radar"
flash_path = "/home/steven/python_data/2025CWA_flash_plan/raw_data/flash/CWA/2025_0701-0811.csv"

county_shp_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
save_dir = f"/home/steven/python_data/2025CWA_flash_plan/result/CV_and_lightning/{year}{month}{day}"
os.makedirs(save_dir, exist_ok=True)

myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
plt.rcParams['axes.unicode_minus'] = False

# ----------------------------------------------------------------------
# ⚡️ 讀取閃電資料
all_flash_data = None
if os.path.exists(flash_path):
    try:
        all_flash_data = pd.read_csv(flash_path)
        
        all_flash_data['time'] = pd.to_datetime(all_flash_data['Epoch Time'], utc=True)
        all_flash_data['lat'] = all_flash_data['Latitude']
        all_flash_data['lon'] = all_flash_data['Longitude']
        all_flash_data['type'] = all_flash_data['Cloud or Ground']
        all_flash_data['time_lct'] = all_flash_data['time'].dt.tz_convert('Asia/Taipei')

        print(f"✅ 成功載入全部閃電資料，共 {len(all_flash_data)} 筆。")
    except Exception as e:
        print(f"⚠️ 讀取或轉換閃電檔案失敗：{flash_path}\n原因：{e}")
        all_flash_data = None
# ----------------------------------------------------------------------

def _draw_base_map(ax):
    county_shp_reader = Reader(county_shp_path)
    county_records = county_shp_reader.records()

    for record in county_records:
        props = record.attributes
        name = props.get('COUNTYNAME', props.get('COUNTY_NA', props.get('COUNTY', '')))

        target_names = ['嘉義縣', '嘉義市', '臺南市', '台南市', 'Chiayi County', 'Chiayi City', 'Tainan City']
        if name in target_names:
            edge_color = 'black'
            lw = 1.0
            z = 5 
        else:
            edge_color = 'gray'
            lw = 0.6
            z = 2

        ax.add_geometries(
            [record.geometry],
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor=edge_color,
            linewidth=lw,
            zorder=z
        )

def _plot_flash(ax, df_flash):
    """繪製雲閃與地閃"""
    if df_flash is None or df_flash.empty:
        return

    df_ic_df = df_flash[df_flash['type'] == 'Cloud'].copy()  # 雲閃
    df_cg_df = df_flash[df_flash['type'] == 'Ground'].copy() # 地閃
    
    if not df_cg_df.empty:
        ax.scatter(
            df_cg_df['lon'], df_cg_df['lat'],
            s=70, marker='x', c='red', linewidths=1.5,
            label=f'CG: {len(df_cg_df)} 筆', 
            transform=ccrs.PlateCarree(), zorder=7
        )
        ax.scatter(
            df_cg_df['lon'], df_cg_df['lat'],
            s=70, marker='x', c='w', linewidths=3.5,
            transform=ccrs.PlateCarree(), zorder=6
        )
    if not df_ic_df.empty:
        ax.scatter(
            df_ic_df['lon'], df_ic_df['lat'],
            s=10, marker='o', c='blue', alpha=1,
            label=f'IC: {len(df_ic_df)} 筆',
            transform=ccrs.PlateCarree(), zorder=6
        )
        ax.scatter(
            df_ic_df['lon'], df_ic_df['lat'],
            s=35, marker='o', c='w', alpha=1,
            transform=ccrs.PlateCarree(), zorder=5
        )

    if not df_cg_df.empty or not df_ic_df.empty:
        ax.legend(loc='upper right', fontsize=12, prop=myfont)


## ==== 找出要處理的 VOL 檔案清單 ==== ##
if draw_one_or_all == 'one':
    vol_file = f"{data_top_path}/data/{year}{month}{day}_u.{station}/{year}{month}{day}{hh}{mm}{ss}.VOL"
    vol_files = [vol_file]
elif draw_one_or_all == 'all':
    vol_folder = f"{data_top_path}/data/{year}{month}{day}_u.{station}"
    vol_files = sorted(glob(f"{vol_folder}/*.VOL"))

for vol_file in vol_files:
    print(vol_file)
    try:
        radar = pyart.io.read_nexrad_archive(vol_file)
        time_str = os.path.basename(vol_file).split('.')[0]
        
        # 1. 取得雷達時間 (Naive)
        time_dt_naive = datetime.strptime(time_str, "%Y%m%d%H%M%S") 
        
        # 2. 轉為 UTC Aware
        time_dt_utc = pd.Timestamp(time_dt_naive).tz_localize('UTC')
        
        # 3. 標題與檔名用的 LCT 時間
        time_str_lct = (time_dt_utc + timedelta(hours=8)).strftime("%Y%m%d%H%M")


        ## ==== 製作 Grid 資料 ==== ##
        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(31, 241, 241),
            grid_limits=((0, 15000), (-150000, 150000), (-150000, 150000)),
            fields=['reflectivity'],
            weighting_function='Nearest',
        )

        ## ==== 計算 beam height 遮罩 ==== ##
        x = grid.x['data'] / 1000 
        y = grid.y['data'] / 1000
        z = grid.z['data'] 

        radar_lon = radar.longitude['data'][0]
        radar_lat = radar.latitude['data'][0]

        x2d, y2d = np.meshgrid(x * 1000, y * 1000) 
        r = np.sqrt(x2d**2 + y2d**2) 

        sweep_elevs = radar.fixed_angle['data']
        beam_heights = []
        R_e = 6371 * 1000 * 4 / 3 
        for elev in sweep_elevs:
            h_beam = np.sqrt(r**2 + R_e**2 + 2 * r * R_e * np.sin(np.radians(elev))) - R_e
            beam_heights.append(h_beam)
        min_beam_height = np.min(np.array(beam_heights), axis=0) 

        ## ==== 取得最大 reflectivity ==== ##
        reflectivity_data = grid.fields['reflectivity']['data'] 

        for i in range(reflectivity_data.shape[0]):
            height = z[i]
            reflectivity_data[i][height < min_beam_height] = np.nan

        comp_reflect = np.nanmax(reflectivity_data, axis=0)

        # 計算經緯度網格
        lon_grid = radar_lon + (x / 111) / np.cos(np.radians(radar_lat))
        lat_grid = radar_lat + (y / 111)

        # ----------------------------------------------------------------------
        # ⚡️ 閃電篩選 (時間 + 空間)
        
        flash_data_now = None
        if all_flash_data is not None:
            # 1. 時間篩選
            end_time_utc = time_dt_utc
            start_time_utc = end_time_utc - timedelta(minutes=flash_conclution_minutes)
            
            mask_time = (all_flash_data['time'] >= start_time_utc) & (all_flash_data['time'] < end_time_utc)
            flash_data_now = all_flash_data[mask_time].copy()

            # 2. 空間篩選 (您要求的 Mask)
            if not flash_data_now.empty:
                # 自動根據雷達 Grid 的範圍設定邊界
                lon_min, lon_max = np.min(lon_grid), np.max(lon_grid)
                lat_min, lat_max = np.min(lat_grid), np.max(lat_grid)

                # ==== 加入您指定的經緯度 Mask ====
                # 這裡使用 flash_data_now 替代您的 pts_df
                in_bbox_mask = (
                    (flash_data_now["lon"] >= lon_min) & (flash_data_now["lon"] <= lon_max) &
                    (flash_data_now["lat"] >= lat_min) & (flash_data_now["lat"] <= lat_max)
                )
                flash_data_now = flash_data_now.loc[in_bbox_mask].copy()
                # ===============================
                
                print(f"篩選後閃電數量: {len(flash_data_now)}")
            
        else:
            print("⚠️ 未載入閃電資料，跳過閃電繪製。")

        # ----------------------------------------------------------------------

        ## ==== 畫圖 ==== ##
        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())

        mesh = ax.pcolormesh(
            lon_grid,
            lat_grid,
            comp_reflect,
            cmap='NWSRef',
            alpha=0.7,
            vmin=0,
            vmax=65,
            transform=ccrs.PlateCarree()
        )

        # 畫出閃電點
        if flash_data_now is not None and not flash_data_now.empty:
            _plot_flash(ax, flash_data_now)

        # 標題與 colorbar
        time_str_title_lct = (time_dt_utc + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M LST")
        ax.set_title(f"合成雷達回波與{flash_conclution_minutes}min以內閃電分佈\n觀測時間: {time_str_title_lct}", fontproperties=title_font)
        
        cbar = plt.colorbar(mesh, ax=ax, shrink=0.8)
        cbar.set_label("反射率 (dBZ)", fontproperties=myfont)
        cbar.set_ticks(np.arange(0, 70, 5))
        
        _draw_base_map(ax)

        # 強制設定地圖範圍與 Grid 一致 (這樣圖才不會因為遠處沒有閃電而留白，也不會因為遠處有閃電而縮小)
        ax.set_extent([np.min(lon_grid), np.max(lon_grid), np.min(lat_grid), np.max(lat_grid)], crs=ccrs.PlateCarree())

        plt.tight_layout()
        output_path = f"{save_dir}/{time_str_lct}00.png"
        plt.savefig(output_path, dpi=150)
        if draw_one_or_all == 'one':
            plt.show()
        plt.close()
        print(f"✅ 儲存圖檔： {output_path}")
    except Exception as e:
        print(f"❌ 讀取錯誤：{vol_file}\n原因：{e}")