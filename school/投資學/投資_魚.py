import pandas as pd
import tkinter as tk

window = tk.Tk()

window.geometry("1000x200")

window.title("My Window")

label = tk.Label(window, text="請輸入檔案名稱(請勿改變檔案位置)")

et = tk.Entry(window)

def read_file():
    path = "C:/Users/steven.LAPTOP-8A1BDJC6/Downloads/" + str(et.get()) + ".csv"
    # print(path)
    df = pd.read_csv(path)
    file = df['現金'] #即期(檔案title有問題)
    # print(file)
    M = str(round(file.mean(),2)) #平均數(預期收益)
    # print(M)
    S = str(round(file.std(),3)) #標準差(預期風險)
    # print(S)
    label.config(text='平均數(預期收益)'+M+'\n標準差(預期風險)'+S)
    
btover = tk.Button(window,text='結束',command=window.destroy)

bt = tk.Button(window, text='輸入完畢', command=read_file)

label.pack()
et.pack()
bt.pack()
btover.pack()
window.mainloop()
# path = et
# df = pd.read_csv(path)
# file = df['現金'] #即期(檔案title有問題)
# # print(file)
# M = str(round(file.mean(),2)) #平均數(預期收益)
# # print(M)
# S = str(round(file.std(),3)) #標準差(預期風險)
# # print(S)
# te ='平均數(預期收益)'+M+'\n標準差(預期風險)'+S

# window_1 = tk.Tk()
# window_1.geometry("1000x200")

# window_1.title(te)

# window_1.mainloop()

# path = "C:/Users/steven.LAPTOP-8A1BDJC6/Downloads/ExchangeRate@202303141527.csv"
# df = pd.read_csv(path)
# file = df['現金'] #即期(檔案title有問題)
# # print(file)
# M = str(round(file.mean(),2)) #平均數(預期收益)
# # print(M)
# S = round(file.std(),3) #標準差(預期風險)
# print(S)