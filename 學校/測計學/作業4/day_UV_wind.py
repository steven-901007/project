import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import glob
import numpy as np
import statistics

plt.rcParams['font.sans-serif'] = [u'MingLiu'] #設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False #用來正常顯示正負號

files = glob.glob("G:/我的雲端硬碟/學校/大氣/測計學/作業4/data/*.csv")
for path in files:
    # print(path)
    print(path[29:37])

    day = path[29:37]
    # day = '20181001'
    path = "G:/我的雲端硬碟/學校/大氣/測計學/作業4/data/"+day+".csv"
    level = [[],[],[],[],[]] #[風向、風速、U、V、time]
    X = []

    data = pd.read_csv(path,header=None,error_bad_lines=False)
    # print(data)

    # print(times)



    for i in range(len(data[0])):
        if int(data[10][i]) != 99:
            level[0].append(data[10][i])#風向
            level[1].append(data[11][i]) #風速
            level[2].append(data[11][i]*np.sin(np.pi * data[10][i]/ 18)) #U #用np.pi和np.sin就可以但是用math就不行
            level[3].append(data[11][i]*np.cos(np.pi * data[10][i]/ 18)) #V
            level[4].append(data[2][i][11:16]) #time

        else:
            # print(i)
            pass

    # for i in range(5): #test
    #     print(len(level[i]))

    #10分鐘平均
    ave = [[],[],[],[],[]] #[風向、風速、U、V、time]

    for i in range(0,len(level[0]),10):
        # print(i)
        for k in range(4):
            one = []
            for j in range(i,i+10):
                # print(j)
                try:
                    one.append(level[k][j])
                except:
                    pass
            ave[k].append(round(statistics.mean(one),2))
        ave[4].append(level[4][i])

    # for i in range(4):
    #     print(len(ave[i]))
    #10分鐘平均/



    level = ave #控制是要10平均還是不用



    for i in range(len(level[0])):
        X.append(i)

    time = []
    if level != ave:
        rangeset = range(0,len(level[4]),50)
    else:
        rangeset = range(0,len(level[4]),6)
    for i in rangeset:
        time.append(level[4][i])

    # print(len(time[0])) #Test

    fig = plt.figure() #取得一張空白的map
    axes = fig.add_subplot(1,1,1)
    plt.plot(X,level[2],color =  'r',label = 'U')
    plt.plot(X,level[3],color =  'b',label = 'V')

    axes.set_xticks(rangeset,time)
    plt.xticks(rotation = 80)
    plt.legend()
    plt.title(day+'UV')
    if level != ave:
        plt.savefig("G:/我的雲端硬碟/學校/大氣/測計學/作業4/pic/wind/1min/UV-"+day)
    else:
        plt.savefig("G:/我的雲端硬碟/學校/大氣/測計學/作業4/pic/wind/ave/UV_ave-"+day)


    fig = plt.figure() #取得一張空白的map
    axes = fig.add_subplot(1,1,1)
    plt.plot(X,level[0],color =  'black',label = '風向')

    axes.set_xticks(rangeset,time)
    plt.axhline(9,c = "r" , ls = "--" , lw = 2)
    plt.axhline(18,c = "r" , ls = "--" , lw = 2)
    plt.axhline(27,c = "r" , ls = "--" , lw = 2)

    plt.xticks(rotation = 80)
    plt.legend()
    plt.title(day+'風向')
    if level != ave:
        plt.savefig("G:/我的雲端硬碟/學校/大氣/測計學/作業4/pic/wind/1min/D-"+day)
    else:
        plt.savefig("G:/我的雲端硬碟/學校/大氣/測計學/作業4/pic/wind/ave/D_ave-"+day)

    fig = plt.figure() #取得一張空白的map
    axes = fig.add_subplot(1,1,1)
    plt.plot(X,level[1],color = 'black',label = '風速')

    axes.set_xticks(rangeset,time)
    plt.xticks(rotation = 80)
    plt.legend()
    plt.title(day+'風速')
    if level != ave:
        plt.savefig("G:/我的雲端硬碟/學校/大氣/測計學/作業4/pic/wind/1min/V-"+day)
    else:
        plt.savefig("G:/我的雲端硬碟/學校/大氣/測計學/作業4/pic/wind/ave/V_ave-"+day)
# plt.show()