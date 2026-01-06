import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

## === 路徑設定 === ##
station = '#6'
data_dir = f"/home/steven/python_data/2025DAAN_park/20250805-0808/{station}/"
all_files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
data_top_path = r"/home/steven/python_data/2025DAAN_park"
output_folder_path = rf"{data_top_path}/result/qv_temp_time/"  # 每天輸出的圖檔資料夾
os.makedirs(output_folder_path, exist_ok=True)

## === 合併所有檔案 === ##
df_list = []
for file in all_files:
    print(file)
    df = pd.read_csv(file, header=None)
    df.columns = ["id", "temperature", "humidity", "pressure", "time",
                  "permanent_voltage", "battery_voltage", "internal_temp",
                  "signal", "light"]

    df["time"] = pd.to_datetime(df["time"], format="%Y%m%d%H%M%S")
    df_list.append(df[["time", "temperature", "humidity"]])

df_all = pd.concat(df_list).sort_values("time").reset_index(drop=True)

## === 1 分鐘平均 (resample) === ##
df_all = df_all.set_index("time").resample("min").mean()

## === 依照「日期」分組，每天一張圖 === ##
for date, df_day in df_all.groupby(df_all.index.date):
    fig, ax1 = plt.subplots(figsize=(12,6))

    # 左軸：溫度
    ax1.plot(df_day.index, df_day["temperature"], color="red", label="Temperature (°C)")
    ax1.set_ylabel("Temperature (°C)", color="red")
    ax1.tick_params(axis="y", labelcolor="red")

    # 右軸：相對濕度
    ax2 = ax1.twinx()
    ax2.plot(df_day.index, df_day["humidity"], color="blue", label="Relative Humidity (%)")
    ax2.set_ylabel("Relative Humidity (%)", color="blue")
    ax2.tick_params(axis="y", labelcolor="blue")

    plt.title(f"Station {station} Temperature & Relative Humidity (1-min average) - {date}")
    plt.xlabel("Time")
    fig.tight_layout()

    # 存檔（以日期命名）
    save_name_str = f'qv_temp_{station}_{date}.png'
    day_plot_save_path_str = os.path.join(output_folder_path, save_name_str)
    plt.savefig(day_plot_save_path_str, dpi=150)
    plt.close(fig)  # 避免記憶體爆掉
    print(day_plot_save_path_str)
