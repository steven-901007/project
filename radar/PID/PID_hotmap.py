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
    file_path = f"{data_top_path}/PID/{year}{month}{day}_{pid}/{time_str}.nc"
    save_dir = f"{data_top_path}/PID_square/{year}{month}{day}"
    os.makedirs(save_dir, exist_ok=True)
    save_path_heatmap = f"{save_dir}/{time_str}_{pid}_PID_count_heatmap.png"

    ## 讀 radar 並 gridding
    radar = pyart.io.read(file_path)
    grid = pyart.map.grid_from_radars(
        radar,
        grid_shape=(21, 400, 400),
        grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
        fields=['hydro_class'],
        gridding_algo='map_gates_to_grid',
        weighting_function='Barnes',
        roi_func='dist_beam',
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
        ## === 合併類別設定：Wet Snow(2) 與 Dry Snow(3) -> Snow(新索引 2) ===
        # 原本索引: 0:Rain, 1:Melting Layer, 2:Wet Snow, 3:Dry Snow, 4:Graupel, 5:Hail
        merged_class_names = ['Rain', 'Melting Layer', 'Snow', 'Graupel', 'Hail']
        ori2new_map_dict = {0: 0, 1: 1, 2: 2, 3: 2, 4: 3, 5: 4}
    elif pid == 'way':
        merged_class_names = ['Rain', 'Snow', 'Graupel', 'Hail','Rain-Hail\nMixture','Supercooled\nWater']
        ori2new_map_dict = {0: 0, 1: 0, 2: 1, 3: 1, 4: 1, 5: 2,6:2,7:3,8:3,9:4,10:5}

    ## 建立向量化映射表（用 -1 表示「未知/不映射」）
    max_ori_pid = max(ori2new_map_dict.keys())
    # 先用最小長度建立，之後在看到資料時再「必要時擴充」
    ori2new_map_array = np.full(max_ori_pid + 1, -1, dtype=int)
    for k, v in ori2new_map_dict.items():
        if k >= 0:
            if k >= ori2new_map_array.size:
                # 動態擴充（理論上不會進來，保險）
                grow = k + 1 - ori2new_map_array.size
                ori2new_map_array = np.concatenate([ori2new_map_array, np.full(grow, -1, dtype=int)])
            ori2new_map_array[k] = v

    ## 統計
    nz = hydro_data.shape[0]
    count_matrix = np.zeros((nz, len(merged_class_names)), dtype=int)

    for iz in range(nz):
        slice_data = hydro_data[iz]              # (y,x) masked array
        data_in_box = slice_data[mask_box]       # 取方框內資料
        valid_vals = data_in_box[~data_in_box.mask]  # 去掉 mask
        if valid_vals.size > 0:
            ## 1) 確保是整數（有些檔會是 float，直接轉 int）
            valid_vals = valid_vals.astype(int, copy=False)

            ## 2) 如資料中的最大 PID 超過映射表長度，擴充並以 -1 充填
            vmax = int(valid_vals.max())
            if vmax >= ori2new_map_array.size:
                grow = vmax + 1 - ori2new_map_array.size
                ori2new_map_array = np.concatenate([ori2new_map_array, np.full(grow, -1, dtype=int)])

            ## 3) 查表映射；把「未知/未映射(-1)」的值濾掉，不計入任何類別
            mapped_vals = ori2new_map_array[valid_vals]
            mapped_vals = mapped_vals[mapped_vals >= 0]
            if mapped_vals.size > 0:
                counts = np.bincount(mapped_vals, minlength=len(merged_class_names))
                count_matrix[iz, :] = counts
            # else：這層在方框內雖有點，但都屬未知 PID，維持 0

        # else：該高度層在方框內沒有有效點，維持 0

    ## 修正邊界（pcolormesh 需要邊界數列）
    x_edges = np.arange(len(merged_class_names) + 1) - 0.5
    y_edges = np.append(gz, gz[-1] + (gz[-1] - gz[-2]))  # 在頂端補一層

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
    # 註：這裡用 count_matrix 的全域最大值做對比，避免使用 pc.norm 屬性造成不必要的錯誤
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
            # 加白色外框（PathEffects），提高可讀性
            txt.set_path_effects([
                path_effects.Stroke(linewidth=2, foreground='white'),
                path_effects.Normal()
            ])

    plt.tight_layout()
    plt.savefig(save_path_heatmap, dpi=150)
    print(f"✅ 儲存熱圖：{save_path_heatmap}")
    plt.close()


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
    pid
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
    file_path = f"{data_top_path}/PID/{year}{month}{day}_{pid}/{time_str}.nc"
    save_dir = f"{data_top_path}/PID_square/{year}{month}{day}"
    os.makedirs(save_dir, exist_ok=True)
    save_path_heatmap = f"{save_dir}/{time_str}_{pid}_PID_percent_heatmap.png"

    ## 讀 radar 並 gridding
    radar = pyart.io.read(file_path)
    grid = pyart.map.grid_from_radars(
        radar,
        grid_shape=(21, 400, 400),
        grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
        fields=['hydro_class'],
        gridding_algo='map_gates_to_grid',
        weighting_function='Barnes',
        roi_func='dist_beam',
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

    ## 類別設定（沿用 count 版的對應）
    if pid == 'park':
        merged_class_names = ['Rain', 'Melting Layer', 'Snow', 'Graupel', 'Hail']
        ori2new_map_dict = {0: 0, 1: 1, 2: 2, 3: 2, 4: 3, 5: 4}
    elif pid == 'way':
        merged_class_names = ['Rain', 'Snow', 'Graupel', 'Hail','Rain-Hail\nMixture','Supercooled\nWater']
        ori2new_map_dict = {0: 0, 1: 0, 2: 1, 3: 1, 4: 1, 5: 2,6:2,7:3,8:3,9:4,10:5}

    ## 建立映射表
    max_ori_pid = max(ori2new_map_dict.keys())
    ori2new_map_array = np.full(max_ori_pid + 1, -1, dtype=int)
    for k, v in ori2new_map_dict.items():
        if k >= ori2new_map_array.size:
            grow = k + 1 - ori2new_map_array.size
            ori2new_map_array = np.concatenate([ori2new_map_array, np.full(grow, -1, dtype=int)])
        ori2new_map_array[k] = v

    ## 統計百分比
    nz = hydro_data.shape[0]
    ratio_matrix = np.zeros((nz, len(merged_class_names)), dtype=float)

    for iz in range(nz):
        slice_data = hydro_data[iz]
        data_in_box = slice_data[mask_box]
        valid_vals = data_in_box[~data_in_box.mask]
        if valid_vals.size > 0:
            valid_vals = valid_vals.astype(int, copy=False)
            vmax = int(valid_vals.max())
            if vmax >= ori2new_map_array.size:
                grow = vmax + 1 - ori2new_map_array.size
                ori2new_map_array = np.concatenate([ori2new_map_array, np.full(grow, -1, dtype=int)])
            mapped_vals = ori2new_map_array[valid_vals]
            mapped_vals = mapped_vals[mapped_vals >= 0]
            if mapped_vals.size > 0:
                counts = np.bincount(mapped_vals, minlength=len(merged_class_names))
                ratio_matrix[iz, :] = counts * 100.0 / mapped_vals.size

    ## 修正邊界
    x_edges = np.arange(len(merged_class_names) + 1) - 0.5
    y_edges = np.append(gz, gz[-1] + (gz[-1] - gz[-2]))

    ## 繪圖
    fig, ax = plt.subplots(figsize=(9, 6))
    pc = ax.pcolormesh(x_edges, y_edges, ratio_matrix, cmap=cmap_name, vmin=0, vmax=100, shading='auto')
    cbar = plt.colorbar(pc, ax=ax)
    cbar.set_label("比例(%)", fontproperties=myfont)
    cbar.set_ticks([0,20,40,60,80,100])
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
