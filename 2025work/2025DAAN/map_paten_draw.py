import os, glob , sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import patheffects as path_effects  # 文字外框用

## ============================== 參數區（可自行修改） ============================== ##
data_top_path = r"/home/steven/python_data/2025DAAN_park"   # 你的資料根目錄
result_folder = rf"{data_top_path}/data"                    # 先前 data_set.py 產出的 CSV 位置
bg_image_path_str = os.path.join(data_top_path, "圖片", "background.png")  # 背景圖（像素座標）

## 要畫哪些測站（用 key 限定會去找對應 CSV；若 CSV 不存在就略過）
sensor_pos_dict = {
    "#1": (423,333), "#2": (392,446), "#3": (455,560),
    "#4": (360,652), "#5": (578,713),  "#6": (641,441),
    "#7": (541,267),
    # 如有 #8~#12 的座標再補進來
}



## === 變數選擇 ===
## param_mode: "Temp" or "Illuminance"
##   - 畫溫度：取欄位 'Temp_min1_mean'
##   - 畫光度：取欄位 'Illuminance_min1_mean'（W/m²）
param_mode = sys.argv[1] if len(sys.argv) > 1 else "Illuminance"
vmin, vmax = None, None  # ★ 若要固定色階（例：溫度 24~45），填數值；不指定就自動
marker_size = 1100         # 點大小
alpha = 1             # 透明度
## ================================================================================ ##
## 圖層輸出資料夾
output_dir = rf"{data_top_path}/result/MinuteMaps/{param_mode}"          # 每分鐘一張圖
os.makedirs(output_dir, exist_ok=True)

## 讀一個測站的 CSV（由 data_set.py 產生）
def load_sensor_csv(sensor_tag: str):
    """讀取單站 CSV；回傳 DataFrame 或 None（找不到檔案就略過）"""
    csv_path = os.path.join(result_folder, f"{sensor_tag}.csv")
    if not os.path.exists(csv_path):
        print(f"[WARN] 找不到檔案：{csv_path}，略過")
        return None
    df = pd.read_csv(csv_path)
    ## 欄位預期：Time, DateTime, Temp, Illuminance_Wm2, Temp_min1_mean, Illuminance_min1_mean, Minute
    ## 確保 Minute 為 datetime
    if "Minute" in df.columns:
        df["Minute"] = pd.to_datetime(df["Minute"], errors="coerce")
    else:
        ## 若沒有 Minute，就依 DateTime 轉
        df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")
        df["Minute"]   = df["DateTime"].dt.floor("min")
    return df


## 蒐集所有測站的每分鐘值（以 minute 為 key）
def build_minute_panel():
    """
    回傳:
      minutes_list: 升冪的所有分鐘（各站 union）
      minute_to_rows: dict[minute] -> list of dict({'tag','x','y','value'})
    """
    minute_to_rows = {}
    for tag, (x, y) in sensor_pos_dict.items():
        df = load_sensor_csv(tag)
        if df is None or df.empty:
            continue

        if param_mode == "Temp":
            val_col = "Temp_min1_mean"
        elif param_mode == "Illuminance":
            val_col = "Illuminance_min1_mean"
        else:
            raise ValueError("param_mode 只能是 'Temp' 或 'Illuminance'")

        # 只保留有該分鐘平均值的列
        sub = df.dropna(subset=["Minute", val_col])[["Minute", val_col]].copy()
        if sub.empty:
            continue

        # 以分鐘聚合（防重複）→ 取該分鐘的平均（理論上已是每分鐘平均，這裡只是保險）
        sub = sub.groupby("Minute", as_index=False).mean(numeric_only=True)

        for r in sub.itertuples(index=False):
            minute = r[0]
            value  = r[1]
            minute_to_rows.setdefault(minute, []).append({
                "tag": tag, "x": x, "y": y, "value": value
            })

    minutes_list = sorted(minute_to_rows.keys())
    return minutes_list, minute_to_rows


## 畫單一分鐘的點圖
def plot_one_minute(minute_ts, rows, bg_img, save_dir):
    """
    minute_ts: 該分鐘的 pandas.Timestamp
    rows: list of {'tag','x','y','value'}
    bg_img: plt.imread 讀入的影像陣列
    """
    if not rows:
        return

    h, w = bg_img.shape[:2]  # 以影像像素為座標                     # ← 重要：鎖定座標範圍
    fig = plt.figure(figsize=(w/100, h/100), dpi=100)               # 螢幕友善大小
    ax = plt.gca()

    ax.imshow(bg_img, origin="upper")
    ax.set_xlim(0, w)                                              # ← 重要
    ax.set_ylim(h, 0)                                              # ← 重要（y 軸往下增加）

    ## 準備資料
    xs = [r["x"] for r in rows]
    ys = [r["y"] for r in rows]
    vals = [r["value"] for r in rows]
    tags = [r["tag"] for r in rows]

    if param_mode == "Temp":
        vmin, vmax = 0, 45
    elif param_mode == "Illuminance":
        vmin, vmax = 0, 100

    ## 畫點（使用默認 colormap）
    sc = ax.scatter(xs, ys, c=vals, s=marker_size, alpha=alpha, vmin=vmin, vmax=vmax, zorder=4)

    ## 標上數值（置中於點，白色外框）
    fmt = "{:.1f}"
    for x, y, v in zip(xs, ys, vals):
        txt = ax.text(
            x, y, fmt.format(v),
            ha="center", va="center",
            fontsize=12, fontweight="bold",
            zorder=5
        )
        txt.set_path_effects([
            path_effects.Stroke(linewidth=2.5, foreground="white"),
            path_effects.Normal()
        ])

    ## colorbar 與標題/標籤
    cbar = plt.colorbar(sc, ax=ax)
    if param_mode == "Temp":
        cbar.set_label("Temperature (°C)")
        title_param = "Temperature"
    else:
        cbar.set_label("Illuminance (W/m²)")
        title_param = "Illuminance"

    plt.title(f"{minute_ts.strftime('%Y/%m/%d %H:%M')}  {title_param}", fontsize=28)
    plt.axis("off")

    ## 存檔（輸出高解析度）
    fn = f"{minute_ts.strftime('%Y%m%d_%H%M')}_{param_mode}.png"
    save_path = os.path.join(save_dir, fn)
    plt.tight_layout()
    plt.savefig(save_path, dpi=75, bbox_inches="tight", pad_inches=0.1)
    # plt.show()
    plt.close()
    print(f"[OK] {save_path}")
## ============================== 主流程 ============================== ##
if __name__ == "__main__":
    ## 讀背景圖
    if not os.path.exists(bg_image_path_str):
        raise FileNotFoundError(f"找不到背景圖：{bg_image_path_str}")
    bg_img = plt.imread(bg_image_path_str)

    ## 蒐集每分鐘資料
    minutes_list, minute_to_rows = build_minute_panel()
    if not minutes_list:
        raise SystemExit("[INFO] 沒有可畫的分鐘資料")

    ## 逐分鐘出圖
    for m in minutes_list:
        plot_one_minute(m, minute_to_rows[m], bg_img, output_dir)
