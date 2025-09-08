## RCNTU *.scn.nc → 包成 Py-ART Radar → grid_from_radars 建 3D 矩陣 → CV（<=0 不畫；漸層色盤）
import xarray as xr
import numpy as np
import pyart
import matplotlib.pyplot as plt
from glob import glob
import os
from datetime import datetime, timedelta
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
import matplotlib.colors as mcolors

## ==== 路徑與檔名設定（請依實際調整） ==== ##
data_top_path    = r"C:\Users\steve\python_data"
data_dir_path    = rf"{data_top_path}\NTU_radar\RCNTU_sample\RCNTU_sample\data"
shapefile_path   = rf"{data_top_path}\radar\Taiwan_map_data\COUNTY_MOI_1090820.shp"

task_id_str      = "0092"                 # 任務編號
time_tag_str     = "20250813_064200"      # 同一時刻（UTC）
batch_str        = "02"                   # 檔尾碼
file_pattern_str = rf"{data_dir_path}\{task_id_str}_{time_tag_str}_??_{batch_str}.scn.nc"

## ==== 找檔 ==== ##
scn_files = sorted(glob(file_pattern_str))
if not scn_files:
    raise FileNotFoundError(f"找不到檔案：{file_pattern_str}")
print(f"共找到 {len(scn_files)} 個仰角檔案")

## ==== 把每層 .scn.nc 包成單仰角 Py-ART Radar ==== ##
radar_list = []
for fp in scn_files:
    ds = xr.open_dataset(fp)

    # 必要欄位（強制 (ray,) / (gate,) / (ray,gate)）
    az   = ds["azimuth"].values.astype(float)                 # (ray,)
    elv  = ds["theta"].values.astype(float)                   # (ray,)
    rng  = ds["range"].values.astype(float)                   # (gate,)
    zhh2 = ds["Zhh"].transpose("ray","gate").values.astype(float)  # (ray, gate)

    # 雷達站中心（沿射線起點取中位數）
    lat0 = float(np.nanmedian(ds["lat"].transpose("ray","gate").values[:, 0]))
    lon0 = float(np.nanmedian(ds["lon"].transpose("ray","gate").values[:, 0]))
    utc_time_str = ds.attrs.get("UTC_TIME", "")
    ds.close()

    nray, ngate = zhh2.shape

    # 建立空的 PPI Radar（單一仰角掃描）
    radar = pyart.testing.make_empty_ppi_radar(ngate, nray, 1)
    radar.time["data"][:]       = np.arange(nray, dtype="float64")
    radar.latitude["data"][:]   = lat0
    radar.longitude["data"][:]  = lon0
    radar.altitude["data"][:]   = 0.0

    radar.range["data"][:]      = rng                       # (gate,)
    radar.azimuth["data"][:]    = az                        # (ray,)
    radar.elevation["data"][:]  = elv                       # (ray,)

    # 欄位名稱用 Py-ART 習慣：reflectivity
    radar.fields["reflectivity"] = {
        "data": np.ma.masked_invalid(zhh2),
        "units": "dBZ",
        "long_name": "Zhh"
    }

    radar_list.append(radar)
    # print(f"封裝：{os.path.basename(fp)} -> rays={nray}, gates={ngate}")

## ==== gridding：建立 3D 矩陣（nz, ny, nx） ==== ##
grid = pyart.map.grid_from_radars(
    radar_list,                           
    grid_shape=(41, 1001, 1001),                   
    grid_limits=((0, 15000), (-150000, 150000), (-150000, 150000)),
    fields=["reflectivity"],
    weighting_function="Nearest",
    # roi_func='constant',
    # constant_roi=500.0,  
)
print('grid')

# 取 3D 反射率場
ref3d = grid.fields["reflectivity"]["data"]    # (nz, ny, nx)，masked array

## ==== Composite（沿高度取 max；<=0 不畫） ==== ##
comp = np.nanmax(ref3d.filled(np.nan), axis=0)  # (ny, nx)
comp[comp <= 0] = np.nan

## ==== 把 grid x/y (m) 近似換成經緯度（以第一個雷達中心） ==== ##
lon0 = float(radar_list[0].longitude["data"][0])
lat0 = float(radar_list[0].latitude["data"][0])
x_km = grid.x["data"] / 1000.0
y_km = grid.y["data"] / 1000.0
deg_per_km_lat = 1.0 / 111.0
deg_per_km_lon = 1.0 / (111.0 * np.cos(np.radians(lat0)))
lon_1d = lon0 + x_km * deg_per_km_lon
lat_1d = lat0 + y_km * deg_per_km_lat

## ==== 時間（標題用） ==== ##
try:
    utc_dt = datetime.strptime(utc_time_str, "%Y-%m-%d_%H:%M:%S")
    lct_dt = utc_dt + timedelta(hours=8)
    title_time_str = lct_dt.strftime("%Y/%m/%d %H:%M:%S")
    outfile_time_str = lct_dt.strftime("%Y%m%d%H%M%S")
except Exception:
    title_time_str = utc_time_str
    outfile_time_str = time_tag_str.replace("_","")

## ==== 漸層色盤（0–65 dBZ） ==== ##
colors = [
    (0.00, "#00FFFF"),  # 青
    (0.08, "#0000FF"),  # 藍
    (0.25, "#00FF00"),  # 綠
    (0.40, "#FFFF00"),  # 黃
    (0.55, "#FFA500"),  # 橙
    (0.70, "#FF0000"),  # 紅
    (0.85, "#8B0000"),  # 暗紅
    (1.00, "#FF00FF"),  # 紫
]
cmap = mcolors.LinearSegmentedColormap.from_list("radar_cmap", colors)

## ==== 繪圖 ==== ##
fig = plt.figure(figsize=(10, 9))
ax = plt.axes(projection=ccrs.PlateCarree())

mesh = ax.pcolormesh(
    lon_1d, lat_1d, comp,
    cmap=cmap, vmin=0, vmax=65,
    transform=ccrs.PlateCarree()
)

# 台灣邊界
ax.add_geometries(
    Reader(shapefile_path).geometries(),
    crs=ccrs.PlateCarree(),
    facecolor="none",
    edgecolor="black",
    linewidth=1.2
)

# 經緯度虛線網格
gl = ax.gridlines(draw_labels=True, linestyle=":", linewidth=0.8)
gl.right_labels = False
gl.top_labels = False

ax.set_title(f"RCNTU Composite Reflectivity(dBZ)\nTime(LCT): {title_time_str}")
cbar = plt.colorbar(mesh, ax=ax, shrink=0.85)
cbar.set_label("reflectivity (dBZ)")
cbar.set_ticks(range(0, 70, 5))

plt.tight_layout()
out_png = os.path.join(data_dir_path, f"{outfile_time_str}_RCNTU_CV_grid.png")
plt.savefig(out_png, dpi=150)
try:
    plt.show()
except Exception:
    pass
plt.close()
print(f"✅ 圖檔已存：{out_png}")
