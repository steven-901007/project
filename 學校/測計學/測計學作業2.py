import xlrd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np


wb = xlrd.open_workbook("G:/我的雲端硬碟/學校/大氣/測計學/PSP_20081005.xls")
ws = wb.sheet_by_index(0)
nm_300 = [] #A
nm_400 = [] #B
nm_700 = [] #C
aba = []#(A-B)/A
bca = []#(B-C)/A
cb = []#C/B
az = []#A/Z
Z = 1367
X = []
time = []
max_num = -99
max_time = -99
for row in range(ws.nrows):
    cell_1 = ws.cell(row, 1)
    cell_2 = ws.cell(row, 2)
    cell_3 = ws.cell(row, 3)
    cell_0 = ws.cell(row, 0)
    if cell_1.ctype == xlrd.XL_CELL_TEXT:
        continue  # 如果是文本，跳过当前循环
    cell_1 = cell_1.value
    cell_2 = cell_2.value
    cell_3 = cell_3.value
    cell_0 = xlrd.xldate_as_datetime(cell_0.value, wb.datemode).strftime('%Y/%m/%d %H:%M')[11:]
    if cell_1 and cell_2 and cell_3:
        X.append(row)
        A = round(float(cell_1), 2)
        B = round(float(cell_2), 2)
        C = round(float(cell_3), 2)
        nm_300.append(A)
        nm_400.append(B)
        nm_700.append(C)
        aba.append((A-B)/A)
        bca.append((B-C)/A)
        cb.append(C/B)
        az.append(A/Z)
        time.append(cell_0)
        if C > max_num:   
            max_time = cell_0
            max_num = C     
        # print(cell_0)
print(max_time)a
print(max_num)
# 创建图表

corrcoef = np.corrcoef(nm_300,nm_700)[0,1]
print(corrcoef)

fig, ax = plt.subplots()

# 绘制数据
# plt.plot(time, nm_300, color='r', marker="*", linestyle='--',label = '300')
# plt.plot(time, nm_400, color='g', marker="*", linestyle='--',label = '400')
# plt.plot(time, nm_700, color='b', marker="*", linestyle='--',label = '700')
# plt.plot(time, aba, color='r', marker="*", linestyle='--',label = 'aba')
# plt.plot(time, bca, color='g', marker="*", linestyle='--',label = 'bca')
# plt.plot(time, cb, color='b', marker="*", linestyle='--',label = 'cb')
plt.plot(time, az, color='y', marker="*", linestyle='--',label = 'az')
# 设置X轴刻度
ax.xaxis.set_major_locator(MaxNLocator(10))  # 仅显示10个刻度
plt.legend()
plt.xticks(rotation=45)  # 旋转刻度标签，以免它们重叠

plt.show()