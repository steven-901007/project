file = "C:/Users/steve/Desktop/python相關資料/NTU探空/sounding/20220515/46692-2022051500.shr.txt"

Time = []      # 觀測時間
Press = []     #壓力
Height = []    #高度
T = []         #溫度
A = []         #不知道是啥1號
B = []         #不知道是啥2號(猜測是露點溫度)
C = []         #不知道是啥3號(猜測是風向)
D = []         #不知道是啥4號(猜測是風速)

with open(file, encoding='utf-8', errors='replace') as file:
    lines = file.readlines()

data = [line.strip().split() for line in lines]
print(len(data))
print(data[1])
for  i in range(2,len(data)):
    Time.append(data[i][0])
    Height.append(data[i][1])
    Press.append(data[i][2])
    T.append(data[i][3])
    A.append(data[i][4])
    B.append(data[i][5])
    C.append(data[i][6])
    D.append(data[i][7])
print(D)