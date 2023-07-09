file = "C:/Users/steve/Desktop/python相關資料/NTU探空/sounding/20220515/46692-2022051500.edt.txt"

Time = []      # 觀測時間
Height = []    #高度
Press = []     #壓力
T = []         #溫度
U = []         #南北風(?
WS = []        #風速
WD = []        #風向
Ascent = []    #上升速率(?

with open(file, encoding='utf-8', errors='replace') as file:
    lines = file.readlines()

data = [line.strip().split() for line in lines]
# print(data)
# print(data[2])
for  i in range(3,len(data)):
    Time.append(data[i][0])
    Height.append(data[i][1])
    Press.append(data[i][2])
    T.append(data[i][3])
    U.append(data[i][4])
    WS.append(data[i][5])
    WD.append(data[i][6])
    Ascent.append(data[i][7])
# print(Time)