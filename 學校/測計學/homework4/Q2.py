import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import glob

files = glob.glob("G:/我的雲端硬碟/學校/大氣/測計學/homework4/data/*.csv")
for path in files:
    # print(path)
    print(path[29:37])

    day = path[29:37]
    # day = '20181001'
    path = "G:/我的雲端硬碟/學校/大氣/測計學/homework4/data/"+day+".csv"


    data = pd.read_csv(path,header=None,error_bad_lines=False)
    # print(data)
    times = data[2].str[11:16]
    # print(times)
    level = [] #[相對溼度、飽和水氣壓-水氣壓、露點溫度-氣溫、比濕]
    level.append(data[7])#露點溫度
    level.append(data[8]-data[9]) #飽和水氣壓-水氣壓
    level.append(data[6]-data[5]) #露點溫度-氣溫
    # print(data[3])
    level.append(data[8]*0.622/(data[3]-data[8])*1000) #比濕
    # print(level[3])

    plt.rcParams['font.sans-serif'] = [u'MingLiu'] #設定字體為'細明體'
    plt.rcParams['axes.unicode_minus'] = False #用來正常顯示正負號
    X = []
    for i in range(len(level[0])):
        X.append(i)
    fig = plt.figure() #取得一張空白的map
    # print(level[6])
    axes = fig.add_subplot(1,1,1)
    plt.plot(X,level[0],color =  'r',label = '相對溼度')
    plt.plot(X,level[1],color = 'y',label = '飽和水氣壓-水氣壓')
    plt.plot(X,level[2],color =  'b',label = '露點溫度-氣溫')
    plt.plot(X,level[3],color =  'black',label = '比濕')

    rangeset = range(0,len(times),50)
    time = []
    for i in rangeset:
        time.append(times[i])

    axes.set_xticks(rangeset,time)
    plt.xticks(rotation = 80)
    plt.legend()
    plt.title(day)
    # plt.show()
    plt.savefig("C:/Users/steve/GitHub/project/學校/測計學/homework4/pic/Q2-"+day)