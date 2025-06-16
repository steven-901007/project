from tqdm import tqdm
import pandas as pd
import os
from glob import glob
import matplotlib.pyplot as plt
import seaborn as sns

# ==== 基本設定 ====
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = 2024
flash_type = 'CG'  # 可選 'IC', 'CG', 'all'
# flash_type = 'IC'
data_folder = f"{data_top_path}/閃電資料/raw_data/TLDS/{year}/"
file_paths = sorted(glob(os.path.join(data_folder, f"{year}*")))



# ==== 讀取每個月的資料並合併 ====
all_data = []


for file_path in tqdm(file_paths, desc="讀取TLDS資料"):
    try:
        # 嘗試以標準格式讀取（你已經轉換過的 CSV 結構）
        data = pd.read_csv(file_path, encoding='utf-8')
    except:
        data = pd.read_csv(file_path, encoding='big5')

    # print(data.info())
    # 轉換時間欄位
    data['日期時間'] = pd.to_datetime(data['日期時間'], errors='coerce')
    data = data.dropna(subset=['日期時間'])  # 移除無效時間資料

    # 加上月份與小時欄位
    data["hour"] = data["日期時間"].dt.hour
    data["month"] = data["日期時間"].dt.month

    all_data.append(data)



# ==== 合併所有月份資料 ====
lightning_data_df = pd.concat(all_data, ignore_index=True)

if year in [2023 , 2024]:  ##特別的year raw data
    # ==== 根據類型過濾 ====
    if flash_type == 'IC':
        df_plot = lightning_data_df[lightning_data_df['類型'] == 'IC']
    elif flash_type == 'CG':
        df_plot = lightning_data_df[lightning_data_df['類型'] == 'CG']
    elif flash_type == 'all':
        df_plot = lightning_data_df[lightning_data_df['類型'].isin(['IC', 'CG'])]
    else:
        raise ValueError("flash_type 必須是 'IC', 'CG', 或 'all'")
else:
    # ==== 根據類型過濾 ====
    if flash_type == 'IC':
        df_plot = lightning_data_df[lightning_data_df['雷擊型態'] == 'IC']
    elif flash_type == 'CG':
        df_plot = lightning_data_df[lightning_data_df['雷擊型態'] == 'CG']
    elif flash_type == 'all':
        df_plot = lightning_data_df[lightning_data_df['雷擊型態'].isin(['IC', 'CG'])]
    else:
        raise ValueError("flash_type 必須是 'IC', 'CG', 或 'all'")

# ==== 繪製 heatmap 函式 ====
def plot_heatmap(data, title, ax):
    # 建立所有月份與小時的組合
    full_index = pd.MultiIndex.from_product(
        [range(1, 13), range(0, 24)],
        names=['month', 'hour']
    )

    # 原始計數表
    count_table = data.groupby(['month', 'hour']).size()

    # 補齊所有格子，沒資料的補 0
    count_table = count_table.reindex(full_index, fill_value=0).unstack()

    # 畫圖
    sns.heatmap(
        count_table,
        ax=ax,
        cmap='YlOrRd',
        linewidths=0.5,
        annot=False,
        xticklabels=True,
        yticklabels=True
    )

    ax.set_title(f"{year} TLDS {title} Lightning Count", fontsize=14)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Month")
    ax.invert_yaxis()  # 讓 1 月在底下

# ==== 畫圖 ====
fig, ax = plt.subplots(figsize=(9, 6))
plot_heatmap(df_plot, flash_type, ax)
plt.tight_layout()
# plt.show()

plt.savefig(f"G:/我的雲端硬碟/工作/2025cook/工作進度_閃電/TLDS/{year}_{flash_type}_hour_and_month.png", dpi=300)
# plt.show()