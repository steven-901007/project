import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==== 基本設定 ====
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = 2021
flash_type = 'IC'  # 可選 'IC', 'CG', 'all'


for year in range(2018,2025):
    print(year)
    for flash_type in ['IC',"CG"]:
        print(flash_type)

        file_path = f"{data_top_path}/閃電資料/raw_data/EN/lightning_{year}.txt"

        # ==== 讀取資料 ====
        df = pd.read_csv(file_path)

        # ==== 處理時間欄位 ====
        df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
        df = df.dropna(subset=['Time'])

        df['hour'] = df['Time'].dt.hour
        df['month'] = df['Time'].dt.month

        # ==== 根據類型篩選 ====
        if flash_type in ['IC', 'CG']:
            df = df[df['lightning_type'] == flash_type]
        elif flash_type == 'all':
            df = df[df['lightning_type'].isin(['IC', 'CG'])]
        else:
            raise ValueError("flash_type 必須是 'IC', 'CG', 或 'all'")

        # ==== 畫圖函式 ====
        def plot_heatmap(data, title, ax):
            count_table = data.groupby(['month', 'hour']).size().unstack(fill_value=0)
            sns.heatmap(
                count_table,
                ax=ax,
                cmap='YlOrRd',
                linewidths=0.5,
                xticklabels=True,
                yticklabels=True
            )
            ax.set_title(f"{year} EN {title} Lightning Count")
            ax.set_xlabel("Hour")
            ax.set_ylabel("Month")
            ax.invert_yaxis()

        # ==== 繪圖 ==== 
        fig, ax = plt.subplots(figsize=(9, 6))

        title_str = flash_type if flash_type != 'all' else 'IC+CG'
        plot_heatmap(df, title_str, ax)

        plt.tight_layout()
        # plt.show()
        plt.savefig(f"G:/我的雲端硬碟/工作/2025cook/工作進度_閃電/EN/{year}_{flash_type}_hour_month.png", dpi=300)
