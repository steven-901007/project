import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from glob import glob

data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = 2021
flash_type = 'CG'  # 可選 'IC', 'CG', 'all'
# flash_type = 'IC'
title_name_time = 'Time'

# ==== 設定資料夾路徑與檔案列表 ====
data_folder = f"{data_top_path}/閃電資料/raw_data/EN/{year}_EN/"
file_paths = sorted(glob(os.path.join(data_folder, "2021*.csv")))

# ==== 建立空 DataFrame 收集所有資料 ====
all_data = []

for file_path in file_paths:
    df = pd.read_csv(file_path)
    
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
    df = df.dropna(subset=['Time'])

    df['hour'] = df['Time'].dt.hour
    df['month'] = df['Time'].dt.month

    all_data.append(df)

lightning_data_df = pd.concat(all_data, ignore_index=True)

# ==== 繪圖函式 ====
def plot_heatmap(data, title, ax):
    count_table = data.groupby(['month', 'hour']).size().unstack(fill_value=0)

    sns.heatmap(
        count_table,
        ax=ax,
        cmap='YlOrRd',
        linewidths=0.5,
        annot=False,
        xticklabels=True,
        yticklabels=True
    )

    ax.set_title(f"{year} EN {title} Lightning Count")
    ax.set_xlabel("Hour")
    ax.set_ylabel("Month")

    # # === 顯示完整 x 軸刻度 ===
    # ax.set_xticks(range(24))
    # ax.set_xticklabels(range(24))

    # # === 顯示完整 y 軸刻度並反轉讓 1 月在下 ===
    # ax.set_yticks(range(12))
    # ax.set_yticklabels(range(1, 13))
    ax.invert_yaxis()  # 顛倒 y 軸方向

# ==== 畫圖 ====
fig, ax = plt.subplots(figsize=(9, 6))

if flash_type == 'IC':
    df_plot = lightning_data_df[lightning_data_df['lightning_type'] == 'IC']
    plot_heatmap(df_plot, "IC", ax)

elif flash_type == 'CG':
    df_plot = lightning_data_df[lightning_data_df['lightning_type'] == 'CG']
    plot_heatmap(df_plot, "CG", ax)

elif flash_type == 'all':
    df_plot = lightning_data_df[lightning_data_df['lightning_type'].isin(['IC', 'CG'])]
    plot_heatmap(df_plot, "IC + CG", ax)

else:
    raise ValueError("flash_type 必須是 'IC', 'CG', 或 'all'")

plt.tight_layout()
# plt.show()
plt.savefig(f"G:/我的雲端硬碟/工作/2025cook/工作進度_閃電/EN/{year}_{flash_type}_hour_and_month.png", dpi=300)