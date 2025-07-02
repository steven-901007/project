import pandas as pd
import matplotlib.pyplot as plt

data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = 2021

# 讀取資料
file_path = rf"{data_top_path}\flash_data\raw_data\EN\lightning_{year}.txt"
df = pd.read_csv(file_path)

# 時間欄位轉換
df['Time'] = pd.to_datetime(df['Time'], format='mixed')

# 新增月份欄位
df['month'] = df['Time'].dt.month

# 分IC、CG統計
ic_data = df[df['lightning_type'] == 'IC']
cg_data = df[df['lightning_type'] == 'CG']

ic_monthly = ic_data['month'].value_counts().sort_index()
cg_monthly = cg_data['month'].value_counts().sort_index()

print("IC 各月份總數：")
print(ic_monthly)
print("\nCG 各月份總數：")
print(cg_monthly)


plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# 繪圖
plt.figure(figsize=(10, 6))
plt.bar(ic_monthly.index - 0.2, ic_monthly.values, width=0.4, label='IC 閃電')
plt.bar(cg_monthly.index + 0.2, cg_monthly.values, width=0.4, label='CG 閃電')
plt.xticks(range(1, 13),size = 15)
plt.xlabel("月份",size = 20)
plt.ylabel("閃電總數",size = 20)
plt.title(f"{year}年 EN IC/CG 閃電每月總數分布",size = 20)
plt.legend(prop={'size': 20})
plt.grid(True)
plt.show()
