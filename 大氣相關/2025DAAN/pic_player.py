import os
import glob
import tkinter as tk
from PIL import Image, ImageTk

class ImagePlayer:
    def __init__(self, root, folder_path, delay=2000):
        self.root = root
        self.folder_path = folder_path
        self.delay = delay        # 每張停留時間 (毫秒)
        self.is_playing = False
        self.index = 0
        self.speed_factor = 1     # 播放速度倍率（1=正常速度）

        # 找圖片
        self.img_files = sorted(glob.glob(os.path.join(folder_path, "*.*")))
        self.img_files = [f for f in self.img_files if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))]
        if not self.img_files:
            raise ValueError("資料夾內沒有圖片！")

        # Tkinter 畫布
        self.label = tk.Label(root)
        self.label.pack()

        # 按鈕區
        control_frame = tk.Frame(root)
        control_frame.pack()

        tk.Button(control_frame, text="上一張", command=self.prev_image).grid(row=0, column=0)
        tk.Button(control_frame, text="播放/停止", command=self.toggle_play).grid(row=0, column=1)
        tk.Button(control_frame, text="下一張", command=self.next_image).grid(row=0, column=2)

        # 播放速度 (1~5 倍)
        for i in range(1, 6):
            tk.Button(control_frame, text=f"{i}x 速度", command=lambda i=i: self.set_speed(i)).grid(row=1, column=i-1)

        self.show_image()

    def show_image(self):
        img_path = self.img_files[self.index]
        img = Image.open(img_path)
        img = img.resize((800, 600), Image.LANCZOS)  # 固定大小
        self.photo = ImageTk.PhotoImage(img)
        self.label.config(image=self.photo)
        self.root.title(f"{self.index+1}/{len(self.img_files)} - {os.path.basename(img_path)}")

    def prev_image(self):
        self.index = (self.index - 1) % len(self.img_files)
        self.show_image()

    def next_image(self):
        self.index = (self.index + 1) % len(self.img_files)
        self.show_image()

    def set_speed(self, factor):
        """設定播放速度倍率"""
        self.speed_factor = factor
        print(f"速度倍率：{self.speed_factor}x")

    def toggle_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play()

    def play(self):
        if self.is_playing:
            self.next_image()
            # 根據 speed_factor 調整間隔
            interval = int(self.delay / self.speed_factor)
            self.root.after(interval, self.play)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("圖片播放器")

    folder = r"C:\Users\steve\python_data\2025DAAN_park\TemperatureMinuteMaps"
    if folder:
        app = ImagePlayer(root, folder)
        root.mainloop()
