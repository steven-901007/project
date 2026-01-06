# 加上建立excel的功能


##繪製pixel數熱圖
def draw_PID_count_hotmap(
    data_top_path,
    year,
    month,
    day,
    hh,
    mm,
    ss,
    lon0,
    lat0,
    lon1,
    lat1,
    pid,
    station,
    selected_classes=None,  # ★ 新增參數：只顯示指定類別
):
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import pyart
    from matplotlib.font_manager import FontProperties
    import matplotlib.patheffects as path_effects
    from datetime import datetime, timedelta

    ## 主要參數
    cmap_name = 'ocean'
    myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
    title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
    plt.rcParams['axes.unicode_minus'] = False

    ## 時間/路徑
    time_str = f"{year}{month}{day}{hh}{mm}{ss}"
    time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
    time_str_LCT = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")
    file_path = f"{data_top_path}/PID/{year}{month}{day}_{station}_{pid}/{time_str}.nc"
    save_dir = f"{data_top_path}/PID_square/{year}{month}{day}"
    os.makedirs(save_dir, exist_ok=True)
    save_path_heatmap = f"{save_dir}/{time_str}_{pid}_PID_count_heatmap.png"

    ## 讀 radar 並 gridding
    radar = pyart.io.read(file_path)
    if station == 'RCWF':
        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(21, 400, 400),
            grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
            fields=["hydro_class"],
            gridding_algo="map_gates_to_grid",
            weighting_function="Nearest",
            roi_func="dist",        # ← 改用距離相依 ROI
            z_factor=0.04,          # 每↑1 m（高度），ROI 增 0.04 m
            xy_factor=0.005,         # 每↑1 m（水平距），ROI 增 0.005 m
            min_radius=500.0,       # ROI 不小於 500 m
            copy_field_data=True
        )
    elif station == 'RCCG':
        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(21, 400, 400),
            grid_limits=((0, 10000), (-125000, 125000), (-125000, 125000)),
            fields=["hydro_class"],
            gridding_algo="map_gates_to_grid",
            weighting_function="Nearest",
            roi_func="dist",        # ← 改用距離相依 ROI
            z_factor=0.04,          # 每↑1 m（高度），ROI 增 0.04 m
            xy_factor=0.009,         # 每↑1 m（水平距），ROI 增 0.009 m
            min_radius=600.0,       # ROI 不小於 600 m
            copy_field_data=True
        )

    hydro_data = grid.fields['hydro_class']['data']  # (z,y,x) 的 masked array
    gz = grid.z['data'] / 1000  # km
    gx = grid.x['data'] / 1000  # km
    gy = grid.y['data'] / 1000  # km

    radar_lon = radar.longitude['data'][0]
    radar_lat = radar.latitude['data'][0]

    ## 簡化版經緯度換算（近似 1 度 ~ 111km）
    lons = radar_lon + gx / 111
    lats = radar_lat + gy / 111
    lon2d, lat2d = np.meshgrid(lons, lats, indexing='xy')

    ## 方框遮罩
    lon_min_box = min(lon0, lon1)
    lon_max_box = max(lon0, lon1)
    lat_min_box = min(lat0, lat1)
    lat_max_box = max(lat0, lat1)
    mask_box = (lon2d >= lon_min_box) & (lon2d <= lon_max_box) & \
               (lat2d >= lat_min_box) & (lat2d <= lat_max_box)

    if pid == 'park':
        merged_class_names = ['Rain', 'Melting Layer', 'Snow', 'Graupel', 'Hail']
        ori2new_map_dict = {0: 0, 1: 1, 2: 2, 3: 2, 4: 3, 5: 4}
    elif pid == 'way':
        merged_class_names = ['Rain', 'Snow', 'Graupel', 'Hail','Rain-Hail\nMixture','Supercooled\nWater']
        ori2new_map_dict = {0: 0, 1: 0, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3, 9: 4, 10: 5}
    else:
        print(f"⚠️ 未支援的 pid: {pid}")
        return

    ## 先記下完整類別清單；矩陣欄數以完整清單為準
    full_class_names = merged_class_names[:]

    ## 若有指定 selected_classes → 篩選
    if selected_classes is not None:
        keep_idx = [i for i, name in enumerate(full_class_names) if name in selected_classes]
        merged_class_names = [full_class_names[i] for i in keep_idx]
        if len(keep_idx) == 0:
            print("⚠️ selected_classes 沒有對到任何類別，略過繪圖。")
            return
    else:
        keep_idx = list(range(len(full_class_names)))

    ## 建立向量化映射表（用 -1 表示「未知/不映射」）
    max_ori_pid = max(ori2new_map_dict.keys())
    ori2new_map_array = np.full(max_ori_pid + 1, -1, dtype=int)
    for k, v in ori2new_map_dict.items():
        if k >= 0:
            if k >= ori2new_map_array.size:
                grow = k + 1 - ori2new_map_array.size
                ori2new_map_array = np.concatenate([ori2new_map_array, np.full(grow, -1, dtype=int)])
            ori2new_map_array[k] = v

    ## 統計
    nz = hydro_data.shape[0]
    n_full_classes = len(full_class_names)
    count_matrix = np.zeros((nz, n_full_classes), dtype=int)

    for iz in range(nz):
        slice_data = hydro_data[iz]  # (y,x) masked array
        data_in_box = slice_data[mask_box]  # 取方框內資料
        valid_vals = data_in_box[~data_in_box.mask]  # 去掉 mask
        if valid_vals.size > 0:
            valid_vals = valid_vals.astype(int, copy=False)  # 確保是整數
            vmax = int(valid_vals.max())
            if vmax >= ori2new_map_array.size:
                grow = vmax + 1 - ori2new_map_array.size
                ori2new_map_array = np.concatenate([ori2new_map_array, np.full(grow, -1, dtype=int)])
            mapped_vals = ori2new_map_array[valid_vals]
            mapped_vals = mapped_vals[mapped_vals >= 0]  # 移除未知
            if mapped_vals.size > 0:
                counts = np.bincount(mapped_vals, minlength=n_full_classes)
                count_matrix[iz, :] = counts

    ## 修正邊界（pcolormesh 需要邊界數列）
    x_edges = np.arange(len(merged_class_names) + 1) - 0.5
    y_edges = np.append(gz, gz[-1] + (gz[-1] - gz[-2]))  # 在頂端補一層

    ## 篩選 matrix（只保留指定類別）
    count_matrix = count_matrix[:, keep_idx]

    ## 繪圖
    fig, ax = plt.subplots(figsize=(9, 6))
    pc = ax.pcolormesh(x_edges, y_edges, count_matrix, cmap=cmap_name, shading='auto')
    cbar = plt.colorbar(pc, ax=ax)
    cbar.set_label("數量(網格點)", fontproperties=myfont)
    ax.set_ylabel("高度 (km)", fontproperties=myfont)
    ax.set_title(f"{time_str_LCT} PID table = {pid}[pixel]", fontproperties=title_font)
    ax.set_xticks(np.arange(len(merged_class_names)))
    ax.set_xticklabels(merged_class_names, fontproperties=myfont)

    ## 每格加數字（置中）
    global_max_val = count_matrix.max() if count_matrix.size > 0 else 0
    for iz in range(nz):
        for ix in range(len(merged_class_names)):
            val = count_matrix[iz, ix]
            if iz < nz - 1:
                y_center = (gz[iz] + gz[iz + 1]) / 2
            else:
                y_center = gz[iz] + (gz[iz] - gz[iz - 1]) / 2
            txt = ax.text(
                ix, y_center, f"{val}",
                ha='center', va='center',
                color=('white' if (global_max_val > 0 and val >= 0.6 * global_max_val) else 'black'),
                fontsize=9, fontproperties=myfont
            )
            txt.set_path_effects([
                path_effects.Stroke(linewidth=2, foreground='white'),
                path_effects.Normal()
            ])

    plt.tight_layout()
    plt.savefig(save_path_heatmap, dpi=150)
    print(f"✅ 儲存熱圖：{save_path_heatmap}")
    plt.close()


###繪製百分比熱圖
def draw_PID_percent_hotmap(
    data_top_path,
    year,
    month,
    day,
    hh,
    mm,
    ss,
    lon0,
    lat0,
    lon1,
    lat1,
    pid,
    station,
    selected_classes=None,  # ★ 新增參數：只顯示指定類別
):
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import pyart
    from matplotlib.font_manager import FontProperties
    import matplotlib.patheffects as path_effects
    from datetime import datetime, timedelta

    ## 主要參數
    cmap_name = 'Purples'
    myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
    title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
    plt.rcParams['axes.unicode_minus'] = False

    ## 時間/路徑
    time_str = f"{year}{month}{day}{hh}{mm}{ss}"
    time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
    time_str_LCT = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")
    file_path = f"{data_top_path}/PID/{year}{month}{day}_{station}_{pid}/{time_str}.nc"
    save_dir = f"{data_top_path}/PID_square/{year}{month}{day}"
    os.makedirs(save_dir, exist_ok=True)
    save_path_heatmap = f"{save_dir}/{time_str}_{pid}_PID_percent_heatmap.png"

    ## 讀 radar 並 gridding
    radar = pyart.io.read(file_path)
    if station == 'RCWF':
        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(21, 400, 400),
            grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
            fields=["hydro_class"],
            gridding_algo="map_gates_to_grid",
            weighting_function="Nearest",
            roi_func="dist",        # ← 改用距離相依 ROI
            z_factor=0.04,          # 每↑1 m（高度），ROI 增 0.04 m
            xy_factor=0.005,         # 每↑1 m（水平距），ROI 增 0.005 m
            min_radius=500.0,       # ROI 不小於 500 m
            copy_field_data=True
        )
    elif station == 'RCCG':
        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(21, 400, 400),
            grid_limits=((0, 10000), (-125000, 125000), (-125000, 125000)),
            fields=["hydro_class"],
            gridding_algo="map_gates_to_grid",
            weighting_function="Nearest",
            roi_func="dist",        # ← 改用距離相依 ROI
            z_factor=0.04,          # 每↑1 m（高度），ROI 增 0.04 m
            xy_factor=0.009,         # 每↑1 m（水平距），ROI 增 0.009 m
            min_radius=600.0,       # ROI 不小於 600 m
            copy_field_data=True
        )

    hydro_data = grid.fields['hydro_class']['data']  # (z,y,x)
    gz = grid.z['data'] / 1000  # km
    gx = grid.x['data'] / 1000
    gy = grid.y['data'] / 1000

    radar_lon = radar.longitude['data'][0]
    radar_lat = radar.latitude['data'][0]

    ## 簡化版經緯度換算
    lons = radar_lon + gx / 111
    lats = radar_lat + gy / 111
    lon2d, lat2d = np.meshgrid(lons, lats, indexing='xy')

    ## 方框遮罩
    lon_min_box = min(lon0, lon1)
    lon_max_box = max(lon0, lon1)
    lat_min_box = min(lat0, lat1)
    lat_max_box = max(lat0, lat1)
    mask_box = (lon2d >= lon_min_box) & (lon2d <= lon_max_box) & \
               (lat2d >= lat_min_box) & (lat2d <= lat_max_box)

    if pid == 'park':
        merged_class_names_list = ['GC/AP', 'BS', 'DS', 'WS', 'CR', 'GR', 'BD', 'RA', 'HR', 'RH']  # 合併後類別
        ori2new_map_dict = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5,6:6,7:7,8:8,9:9}  # 原→新
    elif pid == 'way':
        merged_class_names = ['Rain', 'Snow', 'Graupel', 'Hail','Rain-Hail\nMixture','Supercooled\nWater']
        ori2new_map_dict = {0: 0, 1: 0, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3, 9: 4, 10: 5}
    else:
        print(f"⚠️ 未支援的 pid: {pid}")
        return

    ## 先記下完整類別清單；矩陣欄數以完整清單為準
    full_class_names = merged_class_names[:]

    ## 若有指定 selected_classes → 篩選
    if selected_classes is not None:
        keep_idx = [i for i, name in enumerate(full_class_names) if name in selected_classes]
        merged_class_names = [full_class_names[i] for i in keep_idx]
        if len(keep_idx) == 0:
            print("⚠️ selected_classes 沒有對到任何類別，略過繪圖。")
            return
    else:
        keep_idx = list(range(len(full_class_names)))

    ## 建立映射表
    max_ori_pid = max(ori2new_map_dict.keys())
    ori2new_map_array = np.full(max_ori_pid + 1, -1, dtype=int)
    for k, v in ori2new_map_dict.items():
        if k >= ori2new_map_array.size:
            grow = k + 1 - ori2new_map_array.size
            ori2new_map_array = np.concatenate([ori2new_map_array, np.full(grow, -1, dtype=int)])
        ori2new_map_array[k] = v

    ## 統計百分比（分母只計算 selected_classes；若無指定則用全部）
    nz = hydro_data.shape[0]
    n_full_classes = len(full_class_names)
    ratio_matrix = np.zeros((nz, n_full_classes), dtype=float)

    for iz in range(nz):
        slice_data = hydro_data[iz]  # (y,x) masked array
        data_in_box = slice_data[mask_box]
        valid_vals = data_in_box[~data_in_box.mask]  # 去掉 mask
        if valid_vals.size > 0:
            valid_vals = valid_vals.astype(int, copy=False)
            vmax = int(valid_vals.max())
            if vmax >= ori2new_map_array.size:
                grow = vmax + 1 - ori2new_map_array.size
                ori2new_map_array = np.concatenate([ori2new_map_array, np.full(grow, -1, dtype=int)])
            mapped_vals = ori2new_map_array[valid_vals]
            mapped_vals = mapped_vals[mapped_vals >= 0]  # 移除未知編碼
            if mapped_vals.size > 0:
                counts = np.bincount(mapped_vals, minlength=n_full_classes)  # 各類別數量（完整清單）
                if selected_classes is not None:
                    denom = counts[keep_idx].sum()  # 只用被選類別當分母
                else:
                    denom = mapped_vals.size       # 沒指定就用全部

                if denom > 0:
                    # 先把完整長度都建好，再在 keep_idx 填上比例；沒選到的維持 0
                    row_ratio = np.zeros(n_full_classes, dtype=float)
                    if selected_classes is not None:
                        row_ratio[keep_idx] = counts[keep_idx] * 100.0 / denom
                    else:
                        row_ratio = counts * 100.0 / denom
                    ratio_matrix[iz, :] = row_ratio
                # 若 denom==0，就留 0（全 0）

    ## 修正邊界
    x_edges = np.arange(len(merged_class_names) + 1) - 0.5
    y_edges = np.append(gz, gz[-1] + (gz[-1] - gz[-2]))

    ## 篩選 matrix（只保留指定類別）
    ratio_matrix = ratio_matrix[:, keep_idx]

    ## 繪圖
    fig, ax = plt.subplots(figsize=(9, 6))
    pc = ax.pcolormesh(x_edges, y_edges, ratio_matrix, cmap=cmap_name, vmin=0, vmax=100, shading='auto')
    cbar = plt.colorbar(pc, ax=ax)
    cbar.set_label("比例(%)", fontproperties=myfont)
    cbar.set_ticks([0, 20, 40, 60, 80, 100])
    cbar.ax.set_yticklabels([f"{int(x)}%" for x in cbar.get_ticks()])
    ax.set_ylabel("高度 (km)", fontproperties=myfont)
    ax.set_title(f"{time_str_LCT} PID table = {pid}[percent]", fontproperties=title_font)
    ax.set_xticks(np.arange(len(merged_class_names)))
    ax.set_xticklabels(merged_class_names, fontproperties=myfont)

    ## 每格加比例數字
    for iz in range(nz):
        for ix in range(len(merged_class_names)):
            val = ratio_matrix[iz, ix]
            if iz < nz - 1:
                y_center = (gz[iz] + gz[iz + 1]) / 2
            else:
                y_center = gz[iz] + (gz[iz] - gz[iz - 1]) / 2
            txt = ax.text(
                ix, y_center, f"{val:.1f}",
                ha='center', va='center',
                color=('white' if val >= 50 else 'black'),
                fontsize=9, fontproperties=myfont
            )
            txt.set_path_effects([
                path_effects.Stroke(linewidth=2, foreground='white'),
                path_effects.Normal()
            ])

    plt.tight_layout()
    plt.savefig(save_path_heatmap, dpi=150)
    print(f"✅ 儲存熱圖：{save_path_heatmap}")
    plt.close()


### 繪製百分比顏色 + 像素數文字熱圖
def draw_PID_hotmap_percentColor_countText(
    data_top_path,
    year,
    month,
    day,
    hh,
    mm,
    ss,
    lon0,
    lat0,
    lon1,
    lat1,
    pid,
    station,
    selected_classes=None,  # ★ 只顯示指定類別；顏色=百分比、文字=像素數
):
    """
    繪製 PID 熱圖，顏色表示百分比，文字表示像素數。

    建立水象粒子CSV檔案
    檔案說明：
    - Height index 0~20
    - 高度     0~10km，每0.5km一筆資料，共21層
    """
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import pyart
    from matplotlib.font_manager import FontProperties
    import matplotlib.patheffects as path_effects
    from datetime import datetime, timedelta

    ## ============================== 主要參數 ============================== ##
    cmap_name = 'Purples'  # 顏色用百分比（0~100%）
    myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
    title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
    plt.rcParams['axes.unicode_minus'] = False

    ## ============================== 時間/路徑 ============================== ##
    time_str = f"{year}{month}{day}{hh}{mm}{ss}"  # 例：20240602082400
    time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
    time_str_LCT = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")  # LCT 顯示
    file_path = f"{data_top_path}/PID/{year}{month}{day}_{station}_{pid}/{time_str}.nc"
    save_dir = f"{data_top_path}/PID_square/{year}{month}{day}/heatmap"
    os.makedirs(save_dir, exist_ok=True)
    save_path_heatmap = f"{save_dir}/{time_str}_{pid}_{station}_PID_heatmap.png"

    ## ============================== 讀 radar 並 gridding ============================== ##
    radar = pyart.io.read(file_path)  # 讀 VOL/NC
    if station == 'RCWF':
        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(21, 400, 400),
            grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
            fields=["hydro_class"],
            gridding_algo="map_gates_to_grid",
            weighting_function="Nearest",
            roi_func="dist",        # 距離相依 ROI
            z_factor=0.04,          # 每↑1 m（高度），ROI 增 0.04 m
            xy_factor=0.005,        # 每↑1 m（水平距），ROI 增 0.005 m
            min_radius=500.0,       # ROI 不小於 500 m
            copy_field_data=True
        )
    elif station == 'RCCG':
        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(21, 400, 400),
            grid_limits=((0, 10000), (-125000, 125000), (-125000, 125000)),
            fields=["hydro_class"],
            gridding_algo="map_gates_to_grid",
            weighting_function="Nearest",
            roi_func="dist",
            z_factor=0.04,
            xy_factor=0.009,
            min_radius=600.0,
            copy_field_data=True
        )
    else:
        print(f"⚠️ 未支援的 station: {station}")
        return

    hydro_data = grid.fields['hydro_class']['data']  # (z,y,x) 的 masked array
    gz = grid.z['data'] / 1000.0  # km
    gx = grid.x['data'] / 1000.0  # km
    gy = grid.y['data'] / 1000.0  # km

    radar_lon = radar.longitude['data'][0]
    radar_lat = radar.latitude['data'][0]

    ## ============================== 簡化版經緯度換算 ============================== ##
    lons_1d = radar_lon + gx / 111.0                   # 東西向近似換算
    lats_1d = radar_lat + gy / 111.0                   # 南北向近似換算
    lon2d, lat2d = np.meshgrid(lons_1d, lats_1d, indexing='xy')

    ## ============================== 方框遮罩 ============================== ##
    lon_min_box = min(lon0, lon1)
    lon_max_box = max(lon0, lon1)
    lat_min_box = min(lat0, lat1)
    lat_max_box = max(lat0, lat1)
    mask_box = (lon2d >= lon_min_box) & (lon2d <= lon_max_box) & \
               (lat2d >= lat_min_box) & (lat2d <= lat_max_box)

    ## ============================== 類別合併與映射 ============================== ##
    if pid == 'park':
        merged_class_names_list = ['GC/AP', 'BS', 'DS', 'WS', 'CR', 'GR', 'BD', 'RA', 'HR', 'RH']  # 合併後類別
        ori2new_map_dict = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5,6:6,7:7,8:8,9:9}  # 原→新
    elif pid == 'way':
        merged_class_names_list = ['Rain', 'Snow', 'Graupel', 'Hail', 'Rain-Hail\nMixture', 'Supercooled\nWater']

        ori2new_map_dict = {0: 0, 1: 0, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3, 9: 4, 10: 5}
    else:
        print(f"⚠️ 未支援的 pid: {pid}")
        return

    full_class_names_list = merged_class_names_list[:]  # 完整清單（作為矩陣欄數基準）

    ## 依使用者指定類別做篩選（顯示用）
    if selected_classes is not None:
        keep_index_list = [i for i, name in enumerate(full_class_names_list) if name in selected_classes]  # 要顯示的欄索引
        merged_class_names_list = [full_class_names_list[i] for i in keep_index_list]
        if len(keep_index_list) == 0:
            print("⚠️ selected_classes 沒有對到任何類別，略過繪圖。")
            return
    else:
        keep_index_list = list(range(len(full_class_names_list)))

    ## 建立向量化映射表（未知填 -1；遇到更大原始值會自動擴增）
    max_ori_pid_int = max(ori2new_map_dict.keys())
    ori2new_map_array = np.full(max_ori_pid_int + 1, -1, dtype=int)
    for k, v in ori2new_map_dict.items():
        if k >= 0:
            if k >= ori2new_map_array.size:
                grow_int = k + 1 - ori2new_map_array.size
                ori2new_map_array = np.concatenate([ori2new_map_array, np.full(grow_int, -1, dtype=int)])
            ori2new_map_array[k] = v

    ## ============================== 統計（同時計算 count 與 percent） ============================== ##
    nz_int = hydro_data.shape[0]
    n_full_classes_int = len(full_class_names_list)

    count_matrix_iz_by_cls = np.zeros((nz_int, n_full_classes_int), dtype=int)   # 每層各類別像素數
    ratio_matrix_iz_by_cls = np.zeros((nz_int, n_full_classes_int), dtype=float) # 每層各類別百分比（0~100）

    for iz in range(nz_int):
        slice_data_ma = hydro_data[iz]                   # (y,x) masked array
        data_in_box_ma = slice_data_ma[mask_box]         # 取方框
        valid_vals_arr = data_in_box_ma[~data_in_box_ma.mask]  # 去掉 mask
        if valid_vals_arr.size > 0:
            valid_vals_arr = valid_vals_arr.astype(int, copy=False)
            vmax_int = int(valid_vals_arr.max())
            if vmax_int >= ori2new_map_array.size:
                grow_int = vmax_int + 1 - ori2new_map_array.size
                ori2new_map_array = np.concatenate([ori2new_map_array, np.full(grow_int, -1, dtype=int)])
            mapped_vals_arr = ori2new_map_array[valid_vals_arr]
            mapped_vals_arr = mapped_vals_arr[mapped_vals_arr >= 0]  # 移除未知

            if mapped_vals_arr.size > 0:
                counts_full_arr = np.bincount(mapped_vals_arr, minlength=n_full_classes_int)  # 各類別像素數（完整欄）
                count_matrix_iz_by_cls[iz, :] = counts_full_arr

                # 分母（百分比）：若選了 selected_classes → 只用被選類別之和；否則用全部
                if selected_classes is not None:
                    denom_int = counts_full_arr[keep_index_list].sum()
                else:
                    denom_int = mapped_vals_arr.size

                if denom_int > 0:
                    ratio_row_arr = np.zeros(n_full_classes_int, dtype=float)
                    if selected_classes is not None:
                        ratio_row_arr[keep_index_list] = counts_full_arr[keep_index_list] * 100.0 / denom_int
                    else:
                        ratio_row_arr = counts_full_arr * 100.0 / denom_int
                    ratio_matrix_iz_by_cls[iz, :] = ratio_row_arr
                # denom==0 → 保持 0

    ## ============================== 修正邊界（pcolormesh 需要邊界） ============================== ##
    x_edges_arr = np.arange(len(merged_class_names_list) + 1) - 0.5
    if len(gz) >= 2:
        y_edges_arr = np.append(gz, gz[-1] + (gz[-1] - gz[-2]))  # 在頂端補一層
    else:
        y_edges_arr = np.append(gz, gz[-1] + 0.5)  # 保險

    ## 只保留指定類別欄位（顯示用）
    count_matrix_show = count_matrix_iz_by_cls[:, keep_index_list]
    ratio_matrix_show = ratio_matrix_iz_by_cls[:, keep_index_list]

    ## ============================== 繪圖：色彩=百分比、文字=像素數 ============================== ##
    fig, ax = plt.subplots(figsize=(9, 6))
    pc = ax.pcolormesh(x_edges_arr, y_edges_arr, ratio_matrix_show, cmap=cmap_name, vmin=0, vmax=100, shading='auto')  # 顏色=%
    cbar = plt.colorbar(pc, ax=ax)
    cbar.set_label("水平比例[%]", fontproperties=myfont)
    cbar.set_ticks([0, 20, 40, 60, 80, 100])
    cbar.ax.set_yticklabels([f"{int(x)}%" for x in cbar.get_ticks()])

    ax.set_ylabel("海拔高度 [km]", fontproperties=myfont)
    ax.set_title(f"{time_str_LCT} PID table = {pid}", fontproperties=title_font)
    ax.set_xticks(np.arange(len(merged_class_names_list)))
    ax.set_xticklabels(merged_class_names_list, fontproperties=myfont)

    ## 在每格中心標註「像素數」
    nz = ratio_matrix_show.shape[0]
    ncols = ratio_matrix_show.shape[1]
    # 文字配色規則：以該格百分比 threshold（例如 >=50% 用白字）  # 你可改門檻
    for iz in range(nz):
        for ix in range(ncols):
            count_val_int = count_matrix_show[iz, ix]                 # 顯示用的像素數
            percent_val_float = ratio_matrix_show[iz, ix]             # 該格百分比（決定文字顏色）
            if iz < nz - 1:
                y_center = (gz[iz] + gz[iz + 1]) / 2.0
            else:
                y_center = gz[iz] + (gz[iz] - gz[iz - 1]) / 2.0 if iz > 0 else gz[iz] + 0.25

            txt = ax.text(
                ix, y_center, f"{count_val_int}",                     # ★ 文字=像素數
                ha='center', va='center',
                color='black',
                fontsize=9, fontproperties=myfont
            )
            txt.set_path_effects([
                path_effects.Stroke(linewidth=2, foreground='white'),
                path_effects.Normal()
            ])
    
    

    plt.tight_layout()
    plt.savefig(save_path_heatmap, dpi=150)
    print(f"✅ 儲存熱圖：{save_path_heatmap}")
    plt.close()

    save_dir = f"{data_top_path}/PID_square/{year}{month}{day}/csv"
    os.makedirs(save_dir, exist_ok=True)

    ## 儲存完整像素數矩陣為 CSV
    import pandas as pd
    save_dir_path = f"{save_dir}/{time_str}_{station}_{pid}.csv"
    pd.DataFrame(count_matrix_iz_by_cls, columns=full_class_names_list).to_csv(save_dir_path, index_label='Height_Index')

