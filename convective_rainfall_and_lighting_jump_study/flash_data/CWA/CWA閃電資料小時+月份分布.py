import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==== 基本設定 ====

data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
# year = 2021
# flash_type = 'CG'  # 可選 'IC', 'CG', 'all'
# flash_type = 'IC'

flash_type_code = {
    'IC': 'Cloud',
    'CG': 'Ground'
}


save_path = "G:/我的雲端硬碟/工作/2025cook/工作進度_閃電/CWA"
os.makedirs(save_path, exist_ok=True)

for year in range(2018, 2025):
    print(f"處理 {year} 年資料...")
    for flash_type in ['IC','CG']:
        file_path = f"{data_top_path}/flash_data/raw_data/CWA/L{year}.csv"
        

        # ==== 讀取資料 ====
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)

        # # ==== 處理時間欄位 ====
        if year in [2024]:
            # 時間轉換為 UTC+8 的 datetime
            df['datetime'] = pd.to_datetime(df['Date/Time'], errors='coerce', utc=True) + pd.Timedelta(hours=8)
        else:
            df['datetime'] = pd.to_datetime(df['Solution Key'], errors='coerce', utc=True) + pd.Timedelta(hours=8)
        df = df.dropna(subset=['datetime'])  # 移除無效時間
        df['hour'] = df['datetime'].dt.hour
        df['month'] = df['datetime'].dt.month

        # print(df)   
        # ==== 根據類型分類處理 ====
        df_type = df[df['Cloud or Ground'] == flash_type_code[flash_type]]

        fig, ax = plt.subplots(figsize=(9, 6))
        count_table = df_type.groupby(['month', 'hour']).size().unstack(fill_value=0)

        sns.heatmap(
            count_table,
            ax=ax,
            cmap='YlGnBu',
            linewidths=0.5,
            xticklabels=True,
            yticklabels=True
        )

        ax.set_title(f"{year} CWA {flash_type} Lightning Count")
        ax.set_xlabel("Hour")
        ax.set_ylabel("Month")
        ax.invert_yaxis()

        plt.tight_layout()
        plt.savefig(f"{save_path}/{year}_CWA_{flash_type}_hour_month.png", dpi=300)
        plt.close()
        # break

# print("✅ IC / CG 各年熱圖繪製完成！")
