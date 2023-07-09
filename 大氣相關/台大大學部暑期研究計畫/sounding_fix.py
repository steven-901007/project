import matplotlib.pyplot as plt

file = "C:/Users/steve/Desktop/python相關資料/NTU探空/sounding/20220515/46692-2022051500.fix.txt"

Time = []      # 觀測時間
Height = []    #高度
Press = []     #壓力
T = []         #溫度
U = []         #南北風(?
Td = []        #露點溫度
WS = []        #風速
WD = []        #風向
xlong = []     # 繪圖用

with open(file, encoding='utf-8', errors='replace') as file:
    lines = file.readlines()

data = [line.strip().split(',') for line in lines]
# print(len(data))
# print(data[1])
for  i in range(2,len(data)):
    try:
        Time.append(data[i][0])
        Height.append(int(data[i][1]))
        Press.append(float(data[i][2]))
        T.append(float(data[i][3]))
        U.append(int(data[i][4]))
        Td.append(float(data[i][5]))
        WS.append(float(data[i][6]))
        WD.append(int(data[i][7]))
        xlong.append(i-1)
    except:
        print(i)
# print(Press)

plt.rcParams['font.sans-serif'] = ['MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號

fig, ax = plt.subplots()
ax.plot(xlong,U, color='black', marker=".", linestyle='--')
ax.plot(xlong,Td, color='red', marker=".", linestyle='--')

# 設置Y軸刻度標記
# xticks = []
# for i in range(0,len(Time),100):
#     xticks.append(Time[i])
 

# if len(Time)%100 != 0:
#     xticks.append(Time[len(Time)-1][:5])
#     xranges = range(0, len(Time)+100, 100)
# else:
#     xranges = range(0, len(Time), 100)
# ax.set_xticks(xranges,xticks)

plt.legend()
plt.show()