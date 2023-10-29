import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import glob

files = glob.glob("G:/我的雲端硬碟/學校/大氣/測計學/作業4/data/*.csv")
for path in files:
    # print(path)
    print(path[29:37])

    day = path[29:37]

    path = "G:/我的雲端硬碟/學校/大氣/測計學/作業4/data/"+day+".csv"


    data = pd.read_csv(path,header=None,error_bad_lines=False)
    # print(data)
    times = data[2].str[11:16]
    # print(times)
    level = []
    for i in range(53,61):
        # print(i)
        level.append(data[i])#[地上5公分、地表、地下5公分、地下10公分、地下20公分、地下30公分、地下50公分、地下100公分]

    # print(level)

    X = []

    for i in range(len(level[0])):
        X.append(i)
    fig = plt.figure() #取得一張空白的map
    # print(level[6])
    axes = fig.add_subplot(1,1,1)
    plt.plot(X,level[0],color =  'r',label = '5')
    plt.plot(X,level[1],color = 'gold',label = '0')
    plt.plot(X,level[2],color =  'orange',label = '-5')
    plt.plot(X,level[3],color =  'y',label = '-10')
    plt.plot(X,level[4],color =  'g',label = '-20')
    # plt.plot(X,level[5],color =  'b',label = '-30')
    plt.plot(X,level[6],color =  'purple',label = '-50')
    plt.plot(X,level[7],color = 'black',label = '-100')

    rangeset = range(0,len(times),50)
    time = []
    for i in rangeset:
        time.append(times[i])

    axes.set_xticks(rangeset,time)
    plt.xticks(rotation = 80)
    plt.legend()
    plt.title(day)
    # plt.show()
    plt.savefig("C:/Users/steve/GitHub/project/學校/測計學/作業4/pic/溫度"+day)