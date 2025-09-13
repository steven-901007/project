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
    flash_data_top_path=None
):
    """
    畫 composite reflectivity+剖面線+雷達位置，可疊加 EN 閃電點，
    並畫出以剖面線為對角線的正方形。

    - add_flash: 是否加閃電（預設 False）
    - flash_data_top_path: 閃電主目錄（必填，若 add_flash=True）
    """

    shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
    myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
    title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
    plt.rcParams['axes.unicode_minus'] = False

    vol_file = f"{data_top_path}/data/{year}{month}{day}_u.{station}/{year}{month}{day}{hh}{mm}{ss}.VOL"
    if not os.path.exists(vol_file):
        print(f"❌ 檔案不存在：{vol_file}")
        return

    try:
        radar = pyart.io.read_nexrad_archive(vol_file)
        time_str = os.path.basename(vol_file).split('.')[0]
        time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
        time_str_LCT = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")
        time_str_for_flash = (time_dt + timedelta(hours=8)).strftime("%Y%m%d%H%M")

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
        flash_colors = ['#000000','#8000FF', "#0011FF", '#FF69B4', "#C408F39B"]
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

        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())

        mesh = ax.pcolormesh(
            lon_grid, lat_grid, comp_reflect,
            cmap='NWSRef',
            vmin=0, vmax=65,
            transform=ccrs.PlateCarree()
        )

        ax.set_title(f"{time_str_LCT}", fontproperties=title_font)
        cbar = plt.colorbar(mesh, ax=ax, shrink=0.8)
        cbar.set_label("反射率 (dBZ)", fontproperties=myfont)
        cbar.set_ticks(np.arange(0, 70, 5))

        ax.add_geometries(
            Reader(shapefile_path).geometries(),
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor='green',
            linewidth=1,
        )

        ax.plot(radar_lon, radar_lat, 'ro', transform=ccrs.PlateCarree())
        circle = geodesic.Geodesic().circle(lon=radar_lon, lat=radar_lat, radius=36000, n_samples=360)
        circle_lons, circle_lats = zip(*circle)
        ax.plot(circle_lons, circle_lats, color='black', linewidth=2, linestyle='-', transform=ccrs.PlateCarree())

        # 原始範圍
        lon_min = np.min(lon_grid)
        lon_max = np.max(lon_grid)
        lat_min = np.min(lat_grid)
        lat_max = np.max(lat_grid)
        margin_lon = (lon_max - lon_min) * 0.02
        margin_lat = (lat_max - lat_min) * 0.02
        ax.set_extent([lon_min - margin_lon, lon_max + margin_lon,
                       lat_min - margin_lat, lat_max + margin_lat])
        gl = ax.gridlines(draw_labels=True)
        gl.right_labels = False

        # ==== 剖面線與正方形 ====
        ax.plot(radar_lon, radar_lat, 'x', color='r', zorder=5, markersize=15, label='Radar')
        for lon in [lon0, lon1]:
            ax.plot([lon]*2, [lat0, lat1], '-', color='black', zorder=4, linewidth=3, transform=ccrs.PlateCarree())
        for lat in [lat0, lat1]:
            ax.plot([lon0, lon1], [lat]*2, '-', color='black', zorder=4, linewidth=3, transform=ccrs.PlateCarree())
        
        
        # ==== 閃電點（每分鐘一種顏色）====
        if add_flash and (flash_data_all_df is not None) and (not flash_data_all_df.empty):
            for i in range(5):
                df_minute = flash_data_all_df[flash_data_all_df["minute_offset"] == -i]
                if not df_minute.empty:
                    ax.scatter(
                        df_minute['lon'], df_minute['lat'],
                        s=50,
                        c=[flash_colors[i]],
                        edgecolors='white',  # ✅ 加上白框
                        linewidths=0.5,       # ✅ 邊框線寬
                        label=f"-{i}",
                        transform=ccrs.PlateCarree(),
                        zorder=10-i
                    )
            ax.legend(loc='upper right', fontsize=10, prop=myfont)
        else:
            # 沒有閃電或未指定資料夾，不顯示 legend
            pass

        plt.tight_layout()
        save_dir = f"{data_top_path}/PID_square/{year}{month}{day}"
        os.makedirs(save_dir, exist_ok=True)
        save_path = f"{save_dir}/{time_str}_map.png"
        plt.savefig(save_path, dpi=150)
        print(f"✅ 儲存圖檔：{save_path}")
        if show:
            plt.show()
        plt.close()
    except Exception as e:
        print(f"❌ 讀取錯誤：{vol_file}\n原因：{e}")
