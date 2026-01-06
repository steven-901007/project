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
import pandas as pd
# 新增 CAPPI 繪圖需要的模組
from matplotlib.colors import ListedColormap, BoundaryNorm 

def square_map(
    data_top_path,
    year,
    month,
    day,
    hh,
    mm,
    ss,
    lon0, lat0, lon1, lat1,
    show,
    station,
    add_flash=False,
    flash_data_top_path=None,
    set_extent=None,
):
    """
    畫 composite reflectivity+剖面線+雷達位置，可疊加 EN 閃電點，
    並畫出以剖面線為對角線的正方形。
    建立區域內閃電量資料 csv 檔，位於flash_in_box資料夾內。
    ★★★ 之後接著繪製 1km-10km 的 CAPPI 圖 ★★★
    """

    shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
    myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
    title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
    plt.rcParams['axes.unicode_minus'] = False

    vol_file = f"{data_top_path}/data/{year}{month}{day}_u.{station}/{year}{month}{day}{hh}{mm}{ss}.VOL"
    if not os.path.exists(vol_file):
        print(f"❌ 檔案不存在：{vol_file}")
        return None 

    # === 先把統計結果的預設回傳容器準備好 ===
    flash_inrange_per_minute_dict = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0} 
    flash_inrange_total_int = 0                                     

    try:
        radar = pyart.io.read_nexrad_archive(vol_file)
        time_str = os.path.basename(vol_file).split('.')[0]
        time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
        time_str_LCT = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")
        time_str_for_flash = (time_dt + timedelta(hours=8)).strftime("%Y%m%d%H%M")
        
        # 紀錄稍後 CAPPI 存檔用的時間字串
        time_str_lct_file = (time_dt + timedelta(hours=8)).strftime("%Y%m%d%H%M")

        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(31, 241, 241),
            grid_limits=((0, 15000), (-150000, 150000), (-150000, 150000)),
            fields=['reflectivity'],
            weighting_function='Nearest',
        )

        x = grid.x['data'] / 1000
        y = grid.y['data'] / 1000
        z = grid.z['data']

        radar_lon = radar.longitude['data'][0]
        radar_lat = radar.latitude['data'][0]

        x2d, y2d = np.meshgrid(x * 1000, y * 1000)
        r = np.sqrt(x2d**2 + y2d**2)
        sweep_elevs = radar.fixed_angle['data']
        beam_heights = []
        for elev in sweep_elevs:
            h_beam = np.sqrt(r**2 + 8500000**2 + 2 * r * 8500000 * np.sin(np.radians(elev))) - 8500000
            beam_heights.append(h_beam)
        min_beam_height = np.min(np.array(beam_heights), axis=0)

        reflectivity_data = grid.fields['reflectivity']['data']
        for i in range(reflectivity_data.shape[0]):
            height = z[i]
            reflectivity_data[i][height < min_beam_height] = np.nan
        comp_reflect = np.nanmax(reflectivity_data, axis=0)

        lon_grid = radar_lon + (x / 111) / np.cos(np.radians(radar_lat))
        lat_grid = radar_lat + (y / 111)

        flash_data_all = []
        flash_colors = ['#000000', "#151515", "#232323", "#333333", "#3E3E3E"]
        if add_flash and flash_data_top_path is not None:
            try:
                base_time = datetime.strptime(time_str_for_flash, "%Y%m%d%H%M")
                for i in range(5):
                    flash_time = base_time - timedelta(minutes=i)
                    flash_min_str = flash_time.strftime("%Y%m%d%H%M")
                    flash_path = f"{flash_data_top_path}/flash_data/EN/sort_by_time/{year}/{month}/{flash_min_str}.csv"
                    if os.path.exists(flash_path):
                        flash_df = pd.read_csv(flash_path)
                        flash_df["minute_offset"] = -i
                        flash_data_all.append(flash_df)
                    else:
                        print(f"⚠️ 閃電資料不存在：{flash_path}")
                if flash_data_all:
                    flash_data_all_df = pd.concat(flash_data_all, ignore_index=True)
                else:
                    flash_data_all_df = None
            except Exception as e:
                print(f"⚠️ 閃電資料處理失敗: {e}")
                flash_data_all_df = None
        else:
            flash_data_all_df = None

        # ========================
        # ★★★ 新增：在範圍內的閃電數量統計 ★★★
        # ========================
        if (flash_data_all_df is not None) and (not flash_data_all_df.empty):
            lon_min_box = min(lon0, lon1)
            lon_max_box = max(lon0, lon1)
            lat_min_box = min(lat0, lat1)
            lat_max_box = max(lat0, lat1)

            in_box_mask = (
                (flash_data_all_df["lon"] >= lon_min_box) & (flash_data_all_df["lon"] <= lon_max_box) &
                (flash_data_all_df["lat"] >= lat_min_box) & (flash_data_all_df["lat"] <= lat_max_box)
            )
            flash_in_box_df = flash_data_all_df.loc[in_box_mask].copy()

            for i in range(5):
                cnt_i = (flash_in_box_df["minute_offset"] == -i).sum()
                flash_inrange_per_minute_dict[i] = int(cnt_i)

            flash_inrange_total_int = int(len(flash_in_box_df))
            
            output_flash_dir = f"{data_top_path}/PID_square/{year}{month}{day}/flash_in_box"
            os.makedirs(output_flash_dir, exist_ok=True)
            output_flash_path = f"{output_flash_dir}/{time_str}_{station}_flash_in_box.csv"
            flash_in_box_df.to_csv(output_flash_path, index=False)
            
            print("====== 閃電數量（框內）======")
            print(f"時間(LST)：{time_str_LCT}，站台：{station}")
            print(f"經緯度框：lon[{lon_min_box:.4f}, {lon_max_box:.4f}], lat[{lat_min_box:.4f}, {lat_max_box:.4f}]")
            for i in range(5):
                print(f"  - {i} 分鐘前（minute_offset = -{i}）：{flash_inrange_per_minute_dict[i]} 筆")
            print(f"  → 總數：{flash_inrange_total_int} 筆")

        # ========================

        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())

        mesh = ax.pcolormesh(
            lon_grid, lat_grid, comp_reflect,
            cmap='NWSRef',
            vmin=0, vmax=65,
            transform=ccrs.PlateCarree(),
            zorder = 2,alpha=0.8
        )

        ax.set_title(f"{time_str_LCT} LST CV", fontproperties=title_font)
        cbar = plt.colorbar(mesh, ax=ax, shrink=0.8)
        cbar.set_label("[dBZ]", fontproperties=myfont)
        cbar.set_ticks(np.arange(0, 70, 5))

        ax.add_geometries(
            Reader(shapefile_path).geometries(),
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor='green',
            linewidth=1,
        )

        # 原始範圍與 extent 紀錄
        if set_extent == None:
            lon_min = np.min(lon_grid)
            lon_max = np.max(lon_grid)
            lat_min = np.min(lat_grid)
            lat_max = np.max(lat_grid)
            margin_lon = (lon_max - lon_min) * 0.02
            margin_lat = (lat_max - lat_min) * 0.02
            final_extent = [lon_min - margin_lon, lon_max + margin_lon,
                            lat_min - margin_lat, lat_max + margin_lat]
        else:
            final_extent = set_extent
        
        ax.set_extent(final_extent)

        # ==== 剖面線與正方形 ====
        for lon in [lon0, lon1]:
            ax.plot([lon]*2, [lat0, lat1], '-', color='black', zorder=3, linewidth=2, transform=ccrs.PlateCarree())
        for lat in [lat0, lat1]:
            ax.plot([lon0, lon1], [lat]*2, '-', color='black', zorder=3, linewidth=2, transform=ccrs.PlateCarree())

        # ==== 閃電點（每分鐘一種顏色）====
        if add_flash and (flash_data_all_df is not None) and (not flash_data_all_df.empty):
            for i in range(5):
                df_minute = flash_data_all_df[flash_data_all_df["minute_offset"] == -i]

                if not df_minute.empty:
                    label = (time_dt - timedelta(minutes=i)+timedelta(hours=8)).strftime("%H:%M")
                    ax.scatter(
                        df_minute['lon'], df_minute['lat'],
                        s=100,
                        marker="x",
                        c=[flash_colors[i]],
                        edgecolors='black',
                        linewidths=2,
                        alpha = 1,
                        label= f'{label}',
                        transform=ccrs.PlateCarree(),
                        zorder=1
                    )

        ax.legend(
            loc='upper right',
            fontsize=10,
            prop=myfont,
            frameon=True,
            framealpha=0.8,
            facecolor="#D0EFD1FF",
            edgecolor='black'
        )
        plt.tight_layout()
        save_dir = f"{data_top_path}/PID_square/{year}{month}{day}/map"
        os.makedirs(save_dir, exist_ok=True)
        save_path = f"{save_dir}/{time_str}_{station}_map.png"
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ 儲存 CV 圖檔：{save_path}")
        if show:
            plt.show()
        plt.close()

        # =================================================================
        # ★★★ 新增：CAPPI 繪圖邏輯 (直接使用上方已讀取的 radar 物件) ★★★
        # =================================================================
        print(f"➜ 開始繪製 CAPPI ({time_str_LCT})...")
        
        # 1. 定義 CWA 風格 Colormap
        cwa_colors = [
            '#00FFFF', '#0090FF', '#0000FF', '#00FF00', '#00C800', '#009000',
            '#FFFF00', '#FFD200', '#FF9000', '#FF0000', '#C80000', '#900000',
            '#FF00FF', '#900090'
        ]
        cwa_levels = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70]
        cmap_cwa = ListedColormap(cwa_colors)
        cmap_cwa.set_under('gray')
        norm_cwa = BoundaryNorm(cwa_levels, ncolors=len(cwa_colors), clip=False)

        # 2. 準備 CAPPI 資料 (扁平化與清洗)
        target_heights_amsl = np.arange(1000, 11000, 1000) # 1km 到 10km
        thickness_m = 500
        
        # 提取原始資料 (使用 radar 物件)
        raw_lats = radar.gate_latitude['data'].flatten()
        raw_lons = radar.gate_longitude['data'].flatten()
        raw_alts = radar.gate_altitude['data'].flatten()
        raw_ref = radar.fields['reflectivity']['data'].filled(np.nan).flatten()
        
        valid_mask = ~np.isnan(raw_ref)
        lats_clean = raw_lats[valid_mask]
        lons_clean = raw_lons[valid_mask]
        alts_clean = raw_alts[valid_mask]
        ref_clean = raw_ref[valid_mask]

        # 3. 建立 CAPPI 存檔路徑
        cappi_save_root =  f"{data_top_path}/PID_square/{year}{month}{day}/cappi/{time_str}_{station}"
        os.makedirs(cappi_save_root, exist_ok=True)

        # 4. 迴圈繪製各層高度
        for target_h in target_heights_amsl:
            h_min = target_h - thickness_m
            h_max = target_h + thickness_m
            
            # 高度篩選
            height_mask = (alts_clean >= h_min) & (alts_clean <= h_max)
            plot_lons = lons_clean[height_mask]
            plot_lats = lats_clean[height_mask]
            plot_ref = ref_clean[height_mask]

            if len(plot_ref) == 0:
                continue

            # 排序：弱的回波在下，強的回波在上
            sort_idx = np.argsort(plot_ref)
            plot_lons = plot_lons[sort_idx]
            plot_lats = plot_lats[sort_idx]
            plot_ref = plot_ref[sort_idx]

            # 繪圖
            fig_cappi = plt.figure(figsize=(10, 8))
            ax_c = plt.axes(projection=ccrs.PlateCarree())

            # 畫地圖邊界
            ax_c.add_geometries(
                Reader(shapefile_path).geometries(),
                crs=ccrs.PlateCarree(),
                facecolor='none',
                edgecolor='black',
                linewidth=1.5,
                zorder=3
            )

            # 畫 Scatter
            sc = ax_c.scatter(
                plot_lons, plot_lats, c=plot_ref,
                cmap='NWSRef', 
                vmin=0, vmax=65,   # ★★★ 修改處：補上固定範圍，與 CV 一致
                # norm=norm_cwa,   # (註：你把這行註解掉代表不想用 CWA 色塊風格，若要用則需打開並換 cmap)
                s=1.5, edgecolors='none',
                transform=ccrs.PlateCarree(), zorder=2
            )


            # ==== 剖面線與正方形 ====
            for lon in [lon0, lon1]:
                # ★★★ 修正：將 ax 改為 ax_c
                ax_c.plot([lon]*2, [lat0, lat1], '-', color='black', zorder=4, linewidth=2, transform=ccrs.PlateCarree())
            for lat in [lat0, lat1]:
                # ★★★ 修正：將 ax 改為 ax_c
                ax_c.plot([lon0, lon1], [lat]*2, '-', color='black', zorder=4, linewidth=2, transform=ccrs.PlateCarree())

            # 設定範圍 (使用與 CV 圖相同的範圍)
            ax_c.set_extent(final_extent)

            # 標題與 Colorbar
            height_km = target_h / 1000.0
            ax_c.set_title(f"CAPPI {height_km:.0f}km\n{time_str_LCT} LCT", fontproperties=title_font)
            
            cbar_c = plt.colorbar(sc, ax=ax_c, fraction=0.046, pad=0.04, ticks=cwa_levels, spacing='uniform')
            cbar_c.ax.tick_params(labelsize=10)
            
            # 存檔
            cappi_filename = f"{time_str_lct_file}00_{int(height_km):02d}km.png"
            cappi_path = os.path.join(cappi_save_root, cappi_filename)
            plt.savefig(cappi_path, dpi=150, bbox_inches='tight')
            plt.close(fig_cappi)

        print(f"✅ CAPPI 繪製完成：{cappi_save_root}")

    except Exception as e:
        print(f"❌ 讀取或繪圖錯誤：{vol_file}\n原因：{e}")
        import traceback
        traceback.print_exc() # 修正拼寫錯誤，應為 print_exc，但保留原意
        return None