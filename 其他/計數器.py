import tkinter as tk

# 建立主應用程式視窗
root = tk.Tk()
root.title("雙計數器")

# 計數器初始值
counter1 = 0
counter2 = 0

# 更新顯示計數器1的數值
def update_display1():
    display1.config(text=f"{counter1:03}")

# 更新顯示計數器2的數值
def update_display2():
    display2.config(text=f"{counter2:03}")

# 計數器1增減
def increase1():
    global counter1
    counter1 += 1
    update_display1()

def decrease1():
    global counter1
    counter1 -= 1
    update_display1()

# 計數器2增減
def increase2():
    global counter2
    counter2 += 1
    update_display2()

def decrease2():
    global counter2
    counter2 -= 1
    update_display2()

# 創建計數器1框框
frame1 = tk.LabelFrame(root, text="陸地", padx=30, pady=30, font=("Helvetica", 54))  # 字體變大 1.5 倍
frame1.grid(row=0, column=0, padx=30, pady=30)  # 外邊距加大 1.5 倍

# 顯示計數器1的數值
display1 = tk.Label(frame1, text="000", font=("Helvetica", 108))  # 計數器字體變大 1.5 倍
display1.pack()

# 計數器1加減按鈕並排
button_frame1 = tk.Frame(frame1)
button_frame1.pack()

# 設置 `+` 和 `-` 的字體變大，但保持按鈕框框大小不變
button_increase1 = tk.Button(button_frame1, text="+", command=increase1, font=("Helvetica", 72), bg="lightgreen")  # 字體變大但按鈕框框保持不變
button_increase1.grid(row=0, column=0)

button_decrease1 = tk.Button(button_frame1, text="-", command=decrease1, font=("Helvetica", 72), bg="lightcoral")  # 字體變大但按鈕框框保持不變
button_decrease1.grid(row=0, column=1)

# 創建計數器2框框
frame2 = tk.LabelFrame(root, text="海洋", padx=30, pady=30, font=("Helvetica", 54))  # 字體變大 1.5 倍
frame2.grid(row=0, column=1, padx=30, pady=30)  # 外邊距加大 1.5 倍

# 顯示計數器2的數值
display2 = tk.Label(frame2, text="000", font=("Helvetica", 108))  # 計數器字體變大 1.5 倍
display2.pack()

# 計數器2加減按鈕並排
button_frame2 = tk.Frame(frame2)
button_frame2.pack()

button_increase2 = tk.Button(button_frame2, text="+", command=increase2, font=("Helvetica", 72), bg="lightgreen")  # 字體變大但按鈕框框保持不變
button_increase2.grid(row=0, column=0)

button_decrease2 = tk.Button(button_frame2, text="-", command=decrease2, font=("Helvetica", 72), bg="lightcoral")  # 字體變大但按鈕框框保持不變
button_decrease2.grid(row=0, column=1)

# 進入主迴圈，顯示應用程式
root.mainloop()
