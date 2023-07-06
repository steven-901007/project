import matplotlib.pyplot as plt

file = "C:/Users/steve/Desktop/python相關資料/NTU探空/storm_tracker/20220527/2022052709.u.st/aiqc/no_2880_20220527_1615_L2.eol"

Time = []      # 觀測時間
Utc = []       # 國際標準時間(UTC)
Press = []     # 氣壓 (單位可能是毫巴或帕斯卡)
Temp = []      # 溫度 (單位可能是攝氏度或華氏度)
Dewpt = []     # 露點溫度 (單位可能是攝氏度或華氏度)
Rh = []        # 相對濕度 (以百分比表示)
Uwind = []     # 東西向風速分量 (單位可能是米每秒或節)
Vwind = []     # 南北向風速分量 (單位可能是米每秒或節)
Wspd = []      # 風速 (單位可能是米每秒或節)
Dir = []       # 風向 (以度數表示，以北為參考)
dZ = []        # 高度變化率 (單位可能是米每秒)
GeoPoAlt = []  # 幾何高度 (單位可能是米)
Lon = []       # 經度 (以十進制度數表示)
Lat = []       # 緯度 (以十進制度數表示)
GPSAlt = []    # GPS高度 (單位可能是米)
xlong = []     # 繪圖用

with open(file, encoding='utf-8', errors='replace') as file:
    lines = file.readlines()

data = [line.strip().split() for line in lines]

for i in range(14, len(data)):
    Time.append(data[i][0])
    Utc.append(str(data[i][1]) + ":" + str(data[i][2]) + ":" + str(data[i][3]))
    Press.append(float(data[i][4]))
    Temp.append(float(data[i][5]))
    Dewpt.append(float(data[i][6]))
    Rh.append(float(data[i][7]))
    Uwind.append(float(data[i][8]))
    Vwind.append(float(data[i][9]))
    Wspd.append(float(data[i][10]))
    Dir.append(float(data[i][11]))
    dZ.append(float(data[i][12]))
    GeoPoAlt.append(float(data[i][13]))
    Lon.append(float(data[i][14]))
    Lat.append(float(data[i][15]))
    GPSAlt.append(float(data[i][16]))
    xlong.append(i - 13)

i = len(Time) - 1  # 要顯示的時間點索引

plt.rcParams['font.sans-serif'] = ['MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號

fig, ax = plt.subplots()
ax.plot(xlong,Press, color='black', marker=".", linestyle='--', label='壓力')

# 設置Y軸刻度標記
xticks = []
for i in range(0,len(Utc),100):
    xticks.append(Utc[i][:5])
 

if len(Utc)%100 != 0:
    xticks.append(Utc[len(Utc)-1][:5])
    xranges = range(0, len(Utc)+100, 100)
else:
    xranges = range(0, len(Utc), 100)
ax.set_xticks(xranges,xticks)

plt.legend()
plt.show()
